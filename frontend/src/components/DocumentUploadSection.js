import FileUpload from "./FileUpload";

export const DocumentUploadSection = ({ businessData, setBusinessData }) => {
  const onUpload = (key, file) => {
    setBusinessData({ ...businessData, [key]: file });
  };

  return (
    <div className="border-b pb-6">
      <h3 className="text-lg font-medium mb-4">Upload Documents</h3>
      <div className="flex gap-10 w-full">
        <FileUpload
          onUpload={(file) => onUpload("cibil_file", file)}
          label={"Upload CIBIL CREDIT REPORT:"}
        />
        <FileUpload
          onUpload={(file) => onUpload("gst_file", file)}
          label={"Upload GST:"}
        />
      </div>
    </div>
  );
};
