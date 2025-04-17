import React, { useRef, useState } from "react";
import { Upload } from "lucide-react"; // or your icon library

const FileUpload = ({ onUpload, label }) => {
  const fileInputRef = useRef(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.type !== "application/pdf") {
        setError("Only PDF files are allowed.");
        setSelectedFile(null);
        return;
      }

      if (file.size > 10 * 1024 * 1024) {
        setError("File size should be less than 10MB.");
        setSelectedFile(null);
        return;
      }

      setError("");
      setSelectedFile(file);

      const formData = new FormData();
      formData.append("file", file); // Use "file" or whatever your API expects
      // Optional callback to handle upload outside
      onUpload(file);
    }
  };

  const handleBrowseClick = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="space-y-3 w-full">
      <label>{label}</label>
      <div
        className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center cursor-pointer"
        // onClick={handleBrowseClick}
      >
        <Upload className="mx-auto h-12 w-12 text-gray-400" />
        <p className="mt-2 text-sm text-gray-600">
          Drag and drop files here, or click to select files
        </p>
        <button
          type="button"
          className="mt-3 px-4 py-2 bg-[#4F46E5] text-white rounded-md hover:bg-blue-700"
          onClick={handleBrowseClick}
        >
          Browse Files
        </button>
        <input
          type="file"
          accept="application/pdf"
          ref={fileInputRef}
          onChange={handleFileChange}
          className="hidden"
        />
      </div>
      {selectedFile && (
        <div className="text-sm text-green-600">
          Selected File: {selectedFile.name}
        </div>
      )}
      {error && <div className="text-sm text-red-600">{error}</div>}
      <div className="text-sm text-gray-500">
        Accepted file type: PDF (Max 10MB)
      </div>
    </div>
  );
};

export default FileUpload;
