import { useEffect, useState } from "react";
import { CompanyBasicSection } from "./CompanyBasicSection";
import { DocumentUploadSection } from "./DocumentUploadSection";
import ThresholdSection from "./ThresholdSection";
import apiCall from "../network/Api";

export const BusinessDetailsForm = ({ setCurrentView, setVerdict }) => {
  const [businessData, setBusinessData] = useState({
    company_name: "",
    business_vintage: "",
    proprietor_age: "",
    co_applicant_age: "",
    gst_file: "",
    cibil_file: "",
    rules: "",
  });
  const [rules, setRules] = useState({
    is_30_plus_dpd: false,
    is_60_plus_dpd: false,
    is_90_plus_dpd: false,
    adverse_remarks_present: false,
    unsecured_credit_enquiries_90_days: 0,
    unsecured_loans_disbursed_3_months: 0,
    debt_gt_one_year: false,
    turnover_dip_percent_change: 0,
    last_12_month_sales_in_rs: "",
    debt_to_turnover_ratio: "",
    business_vintage: "",
    applicant_age: "",
    proprietor_age: "",
  });

  const getConfig = async () => {
    try {
      const result = await apiCall({
        endpoint: "/fetch/default",
        method: "GET",
        data: null,
        params: null,
      }).then((res) => {
        setRules(res?.response);
      });
      return result;
    } catch (err) {}
  };

  useEffect(() => {
    getConfig();
  }, []);

  const handleSubmit = async () => {
    setCurrentView("loading");
    try {
      const result = await apiCall({
        endpoint: "/upload/documents",
        method: "POST",
        data: { ...businessData, rules: JSON.stringify(rules) },
        params: null,
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }).then((res) => {
        setVerdict(res);
        setCurrentView("result");
      });
      return result;
    } catch (err) {}
  };

  return (
    <div>
      <h2 className="text-xl font-semibold mb-6">Enter Business Details</h2>

      <div className="space-y-8">
        {/* Part 1: Company Basic */}
        <CompanyBasicSection
          businessData={businessData}
          setBusinessData={setBusinessData}
        />

        {/* Part 2: Document Upload */}
        <DocumentUploadSection
          businessData={businessData}
          setBusinessData={setBusinessData}
        />

        {/* Part 3: Threshold */}
        <ThresholdSection
          isSetting={false}
          formData={rules}
          setFormData={setRules}
        />

        <div className="mt-6">
          <button
            className="px-6 py-2 bg-[#4F46E5] text-white rounded-md hover:bg-blue-700"
            onClick={handleSubmit}
          >
            Submit Business Details
          </button>
        </div>
      </div>
    </div>
  );
};
