import { useEffect, useState } from "react";
import apiCall from "../network/Api";
import { ThresholdCategory } from "./ThresholdCategory";
import ThresholdSection from "./ThresholdSection";

export const SettingsPanel = ({}) => {
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

  return (
    <div>
      <div className="space-y-6">
        <h3 className="text-xl font-medium mb-4">Configurations</h3>
        <ThresholdSection
          isSetting={true}
          formData={rules}
          setFormData={setRules}
        />
      </div>
    </div>
  );
};
