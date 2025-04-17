import io
import simplejson as json

import openai
from PyPDF2 import PdfReader
from fastapi import (APIRouter, UploadFile, Form,
                     File, Depends)
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from backend.app.crud.db_crud_operations import fetch_model_entries, create_model_entry
from backend.app.db import get_db
from backend.app.models import Business, DocumentData
from backend.app.utils.rule_engine_utils import predict_risk_score_based_on_rule_engine

openai.api_key = (
    "sk-proj-yML_w4bVd34rEH1DHfSLpZzUIpAdC4hcFpj9YenGs-x-08ZuoMRlN5SOpqCwCvMu6wwn-TJTc5T3BlbkFJDaRppjEuqtQr"
    "xq9gitgMIrATxpC-MLqp3gwsg8DWiI49xDoApZJKJqHH-_sanZTbBLby42xbcA")

backend_routers = APIRouter()


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
    # try:
    #     rules_dict = json.loads(rules)
    # except json.JSONDecodeError:
    #     return JSONResponse(
    #         content={"error": "Invalid JSON string"},
    #         status_code=400
    #     )
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
    print("fetching cibil response")
    # try:
    #     # Send the CIBIL text to the OpenAI API
    #     cibil_response = openai.ChatCompletion.create(
    #         model="gpt-3.5-turbo",
    #         messages=[{"role": "user", "content": cibil_prompt}],
    #         temperature=0.3,
    #     )
    # except Exception as e:
    #     print("e---------------",e)
    #
    # if cibil_response:
    #     cibil_data = cibil_response['choices'][0]['message']['content']
    # document_data = {
    #     'type': "CIBIL",
    #     'raw_response': json.loads(json.dumps(cibil_data)),
    #     'business_id': business_object.id
    # }
    # cibil_data = json.loads(cibil_data)
    # create_model_entry(db, document_data, DocumentData)
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

        """

    # gst_response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=[{"role": "user", "content": gst_prompt}],
    #     temperature=0.3,
    # )

    # if gst_response:
    #     gst_data = gst_response['choices'][0]['message']['content']
    #     print(f"gst data type---{type(gst_data)}-------------{gst_data}")
    # document_data = {
    #     'type': "GST",
    #     'raw_response': json.loads(json.dumps(gst_data)),
    #     'business_id': business_object.id
    # }
    # gst_data = json.loads(gst_data)
    # create_model_entry(db, document_data, DocumentData)
    # fetched_data_points = cibil_data
    # fetched_data_points.update(gst_data)
    # risk_response = predict_risk_score_based_on_rule_engine(fetched_data_points, rules, strict=True)
    # print("risk_response----------------------------", risk_response)
    # risk_response = predict_risk_score_based_on_rule_engine(fetched_data_points, rules_dict, strict=True)
    risk_response = {
  "verdict": "REJECTED",
  "credit_limit": None,
  "reason": "Failed 3/13 criteria in strict mode.",
  "criteria": {
    "is_30_plus_dpd": {
      "expected": False,
      "actual": True,
      "result": "Fail",
      "remark": "Is 30 Plus Dpd status doesn't meet requirements"
    },
    "is_60_plus_dpd": {
      "expected": False,
      "actual": False,
      "result": "Pass",
      "remark": "Is 60 Plus Dpd status is acceptable"
    },
    "is_90_plus_dpd": {
      "expected": False,
      "actual": False,
      "result": "Pass",
      "remark": "Is 90 Plus Dpd status is acceptable"
    },
    "adverse_remarks_present": {
      "expected": False,
      "actual": False,
      "result": "Pass",
      "remark": "Adverse Remarks Present status is acceptable"
    },
    "unsecured_credit_enquiries_90_days": {
      "expected": 0,
      "actual": 0,
      "result": "Pass",
      "remark": "Unsecured Credit Enquiries 90 Days count is within limits"
    },
    "unsecured_loans_disbursed_3_months": {
      "expected": 0,
      "actual": 0,
      "result": "Pass",
      "remark": "Unsecured Loans Disbursed 3 Months count is within limits"
    },
    "debt_gt_one_year": {
      "expected": False,
      "actual": True,
      "result": "Fail",
      "remark": "Debt Gt One Year status doesn't meet requirements"
    },
    "turnover_dip_percent_change": {
      "expected": 75,
      "actual": 50,
      "result": "Pass",
      "remark": "Turnover dip is acceptable at 50%"
    },
    "last_12_month_sales_in_rs": {
      "expected": 1000000,
      "actual": 1500000,
      "result": "Pass",
      "remark": "Annual sales of Rs 1,500,000 meet minimum requirements"
    },
    "debt_to_turnover_ratio": {
      "expected": 2,
      "actual": 3,
      "result": "Fail",
      "remark": "Debt-to-turnover ratio of 3.0 exceeds maximum of 2.0"
    },
    "business_vintage": {
      "expected": 2,
      "actual": 5,
      "result": "Pass",
      "remark": "Business Vintage of 5 meets minimum requirements"
    },
    "applicant_age": {
      "expected": 25,
      "actual": 30,
      "result": "Pass",
      "remark": "Applicant Age of 30 meets minimum requirements"
    },
    "proprietor_age": {
      "expected": 35,
      "actual": 40,
      "result": "Pass",
      "remark": "Proprietor Age of 40 meets minimum requirements"
    }
  }
}
    # business_object.risk_response = json.dumps(json.loads(risk_response))
    db.add(business_object)
    db.commit()

    return {
            'business_name': business_object.business_name,
            'risk_response': risk_response
        }


@backend_routers.post("/fetch/logs")
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
            'risk_response': json.loads(business_object.risk_response)
        }
        response_list.append(response_data)
    return {
        "response": response_list
    }