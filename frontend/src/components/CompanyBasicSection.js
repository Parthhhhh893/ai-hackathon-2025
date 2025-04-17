export const CompanyBasicSection = ({ businessData, setBusinessData }) => {
  const onChange = (key, value) => {
    setBusinessData({ ...businessData, [key]: value });
  };
  return (
    <div className="border-b pb-6">
      <h3 className="text-lg font-medium mb-4">Company Basic Information</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="flex flex-col items-start">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Company Name
          </label>
          <input
            id="company_name"
            type="text"
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
            placeholder="Enter company name"
            onChange={(e) => onChange(e.target.id, e.target.value)}
          />
        </div>
        <div className="flex flex-col items-start">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Years in Business
          </label>
          <input
            id="business_vintage"
            type="number"
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
            placeholder="Enter Years in Business"
            onChange={(e) => onChange(e.target.id, e.target.value)}
          />
        </div>
        <div className="flex flex-col items-start">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Proprietor / Key Promoter/ Key Partner Age
          </label>
          <input
            id="proprietor_age"
            type="number"
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
            placeholder="Enter Proprietor / Key Promoter/ Key Partner Age"
            onChange={(e) => onChange(e.target.id, e.target.value)}
          />
        </div>
        <div className="flex flex-col items-start">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Co-Applicant Age
          </label>
          <input
            id="co_applicant_age"
            type="number"
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
            placeholder="Enter Co-Applicant Age"
            onChange={(e) => onChange(e.target.id, e.target.value)}
          />
        </div>
      </div>
    </div>
  );
};
