import io
import logging

import simplejson as json

import openai
from PyPDF2 import PdfReader
from fastapi import (APIRouter, UploadFile, Form,
                     File, Depends)
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from backend.app.crud.db_crud_operations import fetch_model_entries, create_model_entry
from backend.app.db import get_db
from backend.app.models import Business, DocumentData, Rule
from backend.app.utils.rule_engine_utils import predict_risk_score_based_on_rule_engine

openai.api_key = (
    "sk-proj-yML_w4bVd34rEH1DHfSLpZzUIpAdC4hcFpj9YenGs-x-08ZuoMRlN5SOpqCwCvMu6wwn-TJTc5T3BlbkFJDaRppjEuqtQr"
    "xq9gitgMIrATxpC-MLqp3gwsg8DWiI49xDoApZJKJqHH-_sanZTbBLby42xbcA")

backend_routers = APIRouter()

# TODO: Only 1 thing is pending, rule which is fetched in input needs to be passed as dictionary in the function.
# Conversion is left
@backend_routers.post("/upload/documents")
async def upload_financial_docs(
        gst_file: UploadFile = File(...),
        cibil_file: UploadFile = File(...),
        business_vintage: int = Form(...),
        co_applicant_age: int = Form(...),
        proprietor_age: int = Form(...),
        company_name: str = Form(...),
        rules: str = Form(...),
        db: Session = Depends(get_db)
):
    try:
        rules_dict = json.loads(rules)
    except json.JSONDecodeError:
        return JSONResponse(
            content={"error": "Invalid JSON string"},
            status_code=400
        )
    # rules_dict={
    #     "is_30_plus_dpd": False,
    #     "is_60_plus_dpd": False,
    #     "is_90_plus_dpd": False,
    #     "adverse_remarks_present": False,
    #     "unsecured_credit_enquiries_90_days": 0,
    #     "unsecured_loans_disbursed_3_months": 0,
    #     "debt_gt_one_year": False,
    #     "turnover_dip_percent_change": 75,
    #     "last_12_month_sales_in_rs": "1000000",
    #     "debt_to_turnover_ratio": "2",
    #     "business_vintage": "2",
    #     "applicant_age": "25",
    #     "proprietor_age": "35"
    # }

    used_business = (
        db.query(Business)
        .filter(Business.business_name.ilike(f"%{company_name}%"))
        .first()
    )

    if used_business:
        logging.info(f"Fetched from database cache for company:{company_name}")
        return {
            'business_name': used_business.business_name,
            'risk_response': used_business.risk_response
        }

    # Create Business entry
    business_data = {
        'business_name': company_name,
        'business_sector': "IT",
        'risk_score': "Not evaluated"
    }
    business_object= create_model_entry(db, business_data, Business)


    cibil_data = await cibil_file.read()
    gst_data = await gst_file.read()

    reader = PdfReader(io.BytesIO(cibil_data))
    cibil_text = ""

    for page in reader.pages:
        cibil_text += page.extract_text() + "\n"

    reader = PdfReader(io.BytesIO(gst_data))
    gst_text = ""

    for page in reader.pages:
        gst_text += page.extract_text() + "\n"

    final_data = {}

    cibil_prompt = f"""
        Below is a **CIBIL report**. Your task is to extract
         **specific financial data points** from the CIBIL
        content and return the result as a **valid JSON**.
        ---
        **CIBIL REPORT SNIPPET**:
        {cibil_text}
        Extract and return the following data points in JSON format:
        1. dpd_30_plus_sma_1  (Meaning any entry where days past due is greater than 30)
        2. dpd_60_plus_sma_2  (Meaning any entry where days past due is greater than 60)
        3. dpd_90_plus_npa  (Meaning any entry where days past due is greater than 90)
        4. adverse_remarks — return a list of adverse remarks with their type and source  
        5. unsecured_credit_enquiries_90_days — number of unsecured credit inquiries in the last 90 days  
        6. unsecured_loans_disbursed_3_months — number of unsecured loans disbursed in the last 3 months  
        7. debt_more_than_one_year — total debt older than 1 year

        Also, include a derived boolean summary like this:

        ```json
        1."is_30_plus_dpd": true/false(Give true when there is a days past due greater than 30),
        2."is_60_plus_dpd": true/false(Give true when there is a days past due greater than 60),
        3."is_90_plus_dpd": true/false(Give true when there is a days past due greater than 90),
        4."adverse_remarks_present": true/false,
        5."unsecured_credit_enquiries_in_last_90_days": true/false,
        6."unsecured_number_of_loans_in_last_3_months": <integer>,
        7."debt_gt_one_year": true/false
        """
    # Send the CIBIL text to the OpenAI API
    cibil_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": cibil_prompt}],
        temperature=0.3,
    )
    if cibil_response:
        cibil_data = cibil_response['choices'][0]['message']['content']

    gst_prompt = f"""
    **GST SNIPPET**:
    {gst_text}
    You are an expert at analyzing financial reports. Given a GST sales report, extract and calculate the following data points:
    1. Turnover DIP Acceptance: Is there a drop or increase in recent 12-month sales compared to the previous 12-months? Mention the percentage change and whether it's acceptable.
    2. Debt to Turnover: If total debt is provided, calculate debt/turnover ratio using the recent 12-month sales.
    3. Last 12 Month Sales: Mention the total taxable value for the last 12 months.
    4. Anchor Dependency: If customer-level sales data is available, calculate the percentage of total sales from the top customer(s).
    5. Vintage with Anchor: Determine how long the business has been transacting with its key anchor customer.
    Use accurate formulas and context from the data file. Return the result in structured JSON format.
    Please always give response in this format:
    This is the sample response format I expect:
            {{
      "Turnover DIP Acceptance": {{
        "Percentage Change": "182%",
        "Acceptable": "Yes"
      }},
      "Debt to Turnover Ratio": "27.89%",
      "Last 12 Month Sales": "₹ 60,987,301.20",
      "Anchor Dependency": "N/A",
      "Vintage with Anchor": "N/A"
    }}
    """

    gst_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": gst_prompt}],
        temperature=0.3,
    )

    if gst_response:
        gst_data = gst_response['choices'][0]['message']['content']

    document_data = {
        'type': "GST",
        'raw_response': json.loads(gst_data),
        'business_id': business_object.id
    }

    gst_data = json.loads(gst_data)
    debt_to_turnover_ratio = gst_data.get('Debt_to_Turnover_Ratio') or gst_data.get('Debt to Turnover Ratio')
    last_12_month_sales = gst_data.get('Last_12_Month_Sales_Total_Taxable_Value') or gst_data.get('Last 12 Month Sales')
    turnover_dip_percent_change_config = gst_data.get('Turnover_DIP_Acceptance') or gst_data.get('Turnover DIP Acceptance')
    turnover_dip_percent_change = turnover_dip_percent_change_config.get('Percentage_Change') or turnover_dip_percent_change_config.get('Percentage Change')
    gst_data = {
        'debt_to_turnover_ratio': float(debt_to_turnover_ratio.replace('%', '').strip()),
        'business_vintage': business_vintage,
        'applicant_age': co_applicant_age,
        'proprietor_age': proprietor_age
    }
    print(f"turnover_dip_percent_change----------------",turnover_dip_percent_change)
    print(f"last_12_month_sales_in_rs----------------",last_12_month_sales)
    if turnover_dip_percent_change:
        gst_data['turnover_dip_percent_change'] = float(
            turnover_dip_percent_change.replace('%', '').strip())
    if last_12_month_sales:
        gst_data['last_12_month_sales_in_rs'] = float(last_12_month_sales.replace('₹', '').replace(',', '').strip())
    print(f"Gst data---------------------{gst_data}",)
    create_model_entry(db, document_data, DocumentData)
    clean_cibil_data = cibil_data.strip().strip('```json').strip('```')
    # Parse the cleaned string into a dictionary
    cibil_data_dict = json.loads(clean_cibil_data)
    fetched_data_points = cibil_data_dict.copy()
    fetched_data_points.update(gst_data)  # Merge gst_data into fetched_data_points
    # rules = {"is_30_plus_dpd": False,"is_60_plus_dpd": False,"is_90_plus_dpd": False,
    #          "adverse_remarks_present": False,
    #          "unsecured_credit_enquiries_90_days": 0,
    #          "unsecured_loans_disbursed_3_months": 0,
    #          "debt_gt_one_year": False,"turnover_dip_percent_change": 75,"last_12_month_sales_in_rs": "1000000","debt_to_turnover_ratio": "2","business_vintage": "2","applicant_age": "25","proprietor_age": "35"}
    risk_response = predict_risk_score_based_on_rule_engine(fetched_data_points, rules_dict, strict=True)
    # risk_response = predict_risk_score_based_on_rule_engine(fetched_data_points, parsed, strict=True)

    document_data = {
        'type': "CIBIL",
        'raw_response': json.loads(clean_cibil_data),
        'business_id': business_object.id
    }
    create_model_entry(db, document_data, DocumentData)
    business_object.risk_response = risk_response
    db.add(business_object)
    db.commit()

    return {
        'business_name': business_object.business_name,
        'risk_response': risk_response
    }


@backend_routers.get("/fetch/logs")
async def fetch_logs(
        db: Session = Depends(get_db)
):
    business_list  =  fetch_model_entries(
        db=db,
        model=Business
    )
    response_list = []
    for business_object in business_list:
        response_data = {
            'business_name': business_object.business_name,
            'risk_response': business_object.risk_response
        }
        response_list.append(response_data)
    return {
        "response": response_list
    }


@backend_routers.get("/fetch/default")
async def fetch_default(
        db: Session = Depends(get_db)
):
    rule  =  fetch_model_entries(
        filter_data={
            'is_enabled': True
        },
        db=db,
        model=Rule,
        fetch_one=True
    )
    return {
        "response": rule.rule_config
    }

# TODO: fetching rule from input string, to be fetched as dictionary
from fastapi import Request
@backend_routers.post("/update/default")
async def fetch_logs(
        request: Request,db: Session = Depends(get_db)

):
    rule_config = request.rule_config

    rule  =  fetch_model_entries(
        filter_data={
            'is_enabled': True
        },
        db=db,
        model=Rule
    )
    rule.is_enabled = False
    rule_data = {
        'rule_config': rule_config,
        'is_enabled': True
    }
    create_model_entry(db, rule_data, Rule)
    db.add(rule)
    db.commit()
    return {
        "response": rule.rule_config
    }