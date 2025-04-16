import io
import json

import openai
from PyPDF2 import PdfReader
from fastapi import (APIRouter, UploadFile, Form,
                     File)

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
        rules: str = Form(...)
        # db: AsyncSession = Depends(get_db)
):
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
    # cibil_response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=[{"role": "user", "content": cibil_prompt}],
    #     temperature=0.3,
    # )
    #
    # if cibil_response:
    #     cibil_data = cibil_response['choices'][0]['message']['content']
    #     final_data = cibil_data

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

    gst_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": gst_prompt}],
        temperature=0.3,
    )

    if gst_response:
        gst_data = gst_response['choices'][0]['message']['content']
        # final_data.update({'gst':gst_data})

    return {"result": json.loads(gst_data)}




