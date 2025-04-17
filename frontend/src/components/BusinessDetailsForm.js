import { useState } from "react";
import { CompanyBasicSection } from "./CompanyBasicSection";
import { DocumentUploadSection } from "./DocumentUploadSection";
import ThresholdSection from "./ThresholdSection";

export const BusinessDetailsForm = ({ setCurrentView }) => {
  const [businessData, setBusinessData] = useState({
    company_name: "",
    business_vintage: "",
    proprietor_age: "",
    co_applicant_age: "",
    gst_file: "",
    cibil_file: "",
    rules: "",
  });

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
        <ThresholdSection isSetting={false} />

        <div className="mt-6">
          <button
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            onClick={() => setCurrentView("loading")}
          >
            Submit Business Details
          </button>
        </div>
      </div>
    </div>
  );
};
