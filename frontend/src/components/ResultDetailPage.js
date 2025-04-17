import React from "react";

export default function ResultDetailPage({ data, handleBackClick }) {
  const { verdict, credit_limit, reason, criteria } = data?.risk_response;

  const verdictColor =
    verdict === "APPROVED" ? "text-green-600" : "text-red-600";
  const borderColor =
    verdict === "APPROVED" ? "border-green-400" : "border-red-400";

  return (
    <div>
      <div className="flex justify-start">
        <button
          onClick={() => handleBackClick()}
          className="bg-gray-200 text-black px-4 py-2 rounded-lg hover:bg-gray-300"
        >
          ← Back to Home
        </button>
      </div>
      <div
        className={`p-6 max-w-4xl mx-auto border-2 ${borderColor} rounded-2xl shadow bg-white`}
      >
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold">{data?.business_name}</h1>
            <h2 className={`text-2xl font-bold ${verdictColor}`}>
              Verdict: {verdict}
            </h2>
            <p className="text-lg font-medium">
              Credit Limit: {credit_limit !== null ? credit_limit : "-"}
            </p>
            <p className="text-gray-600">{reason}</p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full border border-gray-300 rounded-md">
            <thead className="bg-gray-100 text-left">
              <tr>
                <th className="p-3 border-b">Criteria</th>
                <th className="p-3 border-b">Expected</th>
                <th className="p-3 border-b">Actual</th>
                <th className="p-3 border-b">Result</th>
                <th className="p-3 border-b">Remark</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(criteria).map(([key, value]) => (
                <tr key={key} className="border-t border-gray-200">
                  <td className="p-3 font-medium capitalize">
                    {key.replace(/_/g, " ")}
                  </td>
                  <td className="p-3">{String(value.expected)}</td>
                  <td className="p-3">{String(value.actual)}</td>
                  <td className="p-3 font-semibold text-green-600">
                    {value.result}
                  </td>
                  <td className="p-3 text-gray-700">{value.remark}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
