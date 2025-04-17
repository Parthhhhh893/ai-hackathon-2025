import { useState } from "react";
import { BusinessDetailsForm } from "./BusinessDetailsForm";
import { LogsTable } from "./LogsTable";
import { SettingsPanel } from "./SettingsPanel";
import { TabNavigation } from "./TabNavigation";
import Loader from "./Loader";
import ResultDetailsPage from "./ResultDetailPage";

export default function BusinessApp() {
  const [activeTab, setActiveTab] = useState("logs");
  const [currentView, setCurrentView] = useState("main");
  const [viewData, setViewData] = useState(null);
  const [threshold, setThreshold] = useState(0.75);
  const [defaultThreshold, setDefaultThreshold] = useState(0.75);
  const [thresholdConfig, setThresholdConfig] = useState({
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

  // Sample log data
  const verdict = {
    business_name: "Business",
    risk_response: {
      verdict: "REJECTED",
      credit_limit: null,
      reason: "Failed 3/13 criteria in strict mode.",
      criteria: {
        is_30_plus_dpd: {
          expected: false,
          actual: true,
          result: "Fail",
          remark: "Is 30 Plus Dpd status doesn't meet requirements",
        },
        is_60_plus_dpd: {
          expected: false,
          actual: false,
          result: "Pass",
          remark: "Is 60 Plus Dpd status is acceptable",
        },
        is_90_plus_dpd: {
          expected: false,
          actual: false,
          result: "Pass",
          remark: "Is 90 Plus Dpd status is acceptable",
        },
        adverse_remarks_present: {
          expected: false,
          actual: false,
          result: "Pass",
          remark: "Adverse Remarks Present status is acceptable",
        },
        unsecured_credit_enquiries_90_days: {
          expected: 0,
          actual: 0,
          result: "Pass",
          remark: "Unsecured Credit Enquiries 90 Days count is within limits",
        },
        unsecured_loans_disbursed_3_months: {
          expected: 0,
          actual: 0,
          result: "Pass",
          remark: "Unsecured Loans Disbursed 3 Months count is within limits",
        },
        debt_gt_one_year: {
          expected: false,
          actual: true,
          result: "Fail",
          remark: "Debt Gt One Year status doesn't meet requirements",
        },
        turnover_dip_percent_change: {
          expected: 75,
          actual: 50,
          result: "Pass",
          remark: "Turnover dip is acceptable at 50%",
        },
        last_12_month_sales_in_rs: {
          expected: 1000000,
          actual: 1500000,
          result: "Pass",
          remark: "Annual sales of Rs 1,500,000 meet minimum requirements",
        },
        debt_to_turnover_ratio: {
          expected: 2,
          actual: 3,
          result: "Fail",
          remark: "Debt-to-turnover ratio of 3.0 exceeds maximum of 2.0",
        },
        business_vintage: {
          expected: 2,
          actual: 5,
          result: "Pass",
          remark: "Business Vintage of 5 meets minimum requirements",
        },
        applicant_age: {
          expected: 25,
          actual: 30,
          result: "Pass",
          remark: "Applicant Age of 30 meets minimum requirements",
        },
        proprietor_age: {
          expected: 35,
          actual: 40,
          result: "Pass",
          remark: "Proprietor Age of 40 meets minimum requirements",
        },
      },
    },
  };
  const logs = [verdict, verdict, verdict];

  const handleResultClick = (type, data) => {
    setCurrentView(type);
    setViewData(data);
  };

  const handleBackClick = () => {
    setCurrentView("main");
    setViewData(null);
  };

  const updateDefaultThreshold = () => {
    setDefaultThreshold(threshold);
    alert("Default threshold updated successfully!");
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-blue-600 text-white p-4">
        <div className="container mx-auto">
          <h1 className="text-2xl font-bold">Business Assessment Portal</h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-grow container mx-auto p-4">
        {currentView === "main" ? (
          <>
            {/* Tabs */}
            <TabNavigation activeTab={activeTab} setActiveTab={setActiveTab} />

            {/* Tab Content */}
            <div className="bg-white p-6 rounded-lg shadow">
              {activeTab === "logs" && (
                <LogsTable logs={logs} handleResultClick={handleResultClick} />
              )}

              {activeTab === "business" && (
                <BusinessDetailsForm
                  threshold={threshold}
                  setThreshold={setThreshold}
                  defaultThreshold={defaultThreshold}
                  setDefaultThreshold={setDefaultThreshold}
                  thresholdConfig={thresholdConfig}
                  updateThresholdConfig={setThresholdConfig}
                  setCurrentView={setCurrentView}
                />
              )}

              {activeTab === "settings" && (
                <SettingsPanel
                  threshold={threshold}
                  setThreshold={setThreshold}
                  defaultThreshold={defaultThreshold}
                  setDefaultThreshold={setDefaultThreshold}
                  thresholdConfig={thresholdConfig}
                  updateThresholdConfig={setThresholdConfig}
                />
              )}
            </div>
          </>
        ) : (
          <div className="bg-white p-6 rounded-lg shadow">
            {currentView === "result" && viewData && (
              <ResultDetailsPage
                data={verdict}
                handleBackClick={handleBackClick}
              />
            )}
            {currentView === "loading" && <Loader />}
          </div>
        )}
      </main>
    </div>
  );
}
