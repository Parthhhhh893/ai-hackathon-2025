import { Loader2, ShieldCheck } from "lucide-react";
import React from "react";

const Loader = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 text-center px-4">
      <div className="mb-6 bg-blue-100 rounded-full p-4">
        <ShieldCheck className="w-12 h-12 text-blue-600" />
      </div>
      <h1 className="text-xl font-semibold text-gray-800 mb-2">
        Generating Your Credit Score
      </h1>
      <p className="text-gray-600 max-w-md">
        Our AI system is securely analyzing your financial data. This will just
        take a moment.
      </p>
      <div className="flex items-center mt-6 space-x-2">
        <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
        <span className="text-sm text-gray-700">Processing securely...</span>
      </div>
      <p className="mt-4 text-xs text-gray-500">
        Powered by AI • Encrypted data handling
      </p>
    </div>
  );
};

export default Loader;
