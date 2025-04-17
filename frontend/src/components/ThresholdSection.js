import React, { useState } from "react";

export default function ThresholdSection({ isSetting = false }) {
  const [formData, setFormData] = useState({
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

  const handleChange = (e) => {
    const { name, type, value, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Submitted Config:", formData);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="p-6 max-w-2xl mx-auto grid gap-4 bg-white rounded-2xl shadow"
    >
      <h2 className="text-lg font-medium">CIBIL Configs</h2>

      {[
        { label: "30+ DPD", name: "is_30_plus_dpd" },
        { label: "60+ DPD", name: "is_60_plus_dpd" },
        { label: "90+ DPD", name: "is_90_plus_dpd" },
        { label: "Adverse Remarks Present", name: "adverse_remarks_present" },
        { label: "Debt > 1 Year", name: "debt_gt_one_year" },
      ].map((item) => (
        <label key={item.name} className="flex items-center gap-2">
          <input
            type="checkbox"
            name={item.name}
            checked={formData[item.name]}
            onChange={handleChange}
          />
          {item.label}
        </label>
      ))}

      <label className="flex gap-2">
        Unsecured Credit Enquiries (90 days)
        <input
          type="number"
          name="unsecured_credit_enquiries_90_days"
          value={formData.unsecured_credit_enquiries_90_days}
          onChange={handleChange}
          className="w-20 px-2 py-1 border border-gray-300 rounded"
        />
      </label>

      <label className="flex gap-2">
        Unsecured Loans Disbursed (3 months)
        <input
          type="number"
          name="unsecured_loans_disbursed_3_months"
          value={formData.unsecured_loans_disbursed_3_months}
          onChange={handleChange}
          className="w-20 px-2 py-1 border border-gray-300 rounded"
        />
      </label>

      <h2 className="text-lg font-medium mt-4">GST Config</h2>

      <label className="flex gap-2">
        Turnover DIP % Change
        <input
          type="number"
          name="turnover_dip_percent_change"
          value={formData.turnover_dip_percent_change}
          onChange={handleChange}
          className="w-20 px-2 py-1 border border-gray-300 rounded"
        />
      </label>

      <label className="flex gap-2">
        Last 12 Month Sales (₹)
        <input
          type="text"
          name="last_12_month_sales_in_rs"
          value={formData.last_12_month_sales_in_rs}
          onChange={handleChange}
          className="w-20 px-2 py-1 border border-gray-300 rounded"
        />
      </label>

      <label className="flex gap-2">
        Debt to Turnover Ratio
        <input
          type="text"
          name="debt_to_turnover_ratio"
          value={formData.debt_to_turnover_ratio}
          onChange={handleChange}
          className="w-20 px-2 py-1 border border-gray-300 rounded"
        />
      </label>

      <h2 className="text-lg font-medium mt-4">Generic Data</h2>

      <label className="flex gap-2">
        Business Vintage (years)
        <input
          type="text"
          name="business_vintage"
          value={formData.business_vintage}
          onChange={handleChange}
          className="w-20 px-2 py-1 border border-gray-300 rounded"
        />
      </label>

      <label className="flex gap-2">
        Applicant Age
        <input
          type="text"
          name="applicant_age"
          value={formData.applicant_age}
          onChange={handleChange}
          className="w-20 px-2 py-1 border border-gray-300 rounded"
        />
      </label>

      <label className="flex gap-2">
        Proprietor Age
        <input
          type="text"
          name="proprietor_age"
          value={formData.proprietor_age}
          onChange={handleChange}
          className="w-20 px-2 py-1 border border-gray-300 rounded"
        />
      </label>

      {isSetting && (
        <button
          type="submit"
          className="mt-4 bg-blue-600 text-white py-2 px-4 rounded-xl"
        >
          Submit Config
        </button>
      )}
    </form>
  );
}
