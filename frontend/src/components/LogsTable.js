export const LogsTable = ({ logs, handleResultClick }) => {
  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Business Reports</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-gray-100">
              <th className="py-3 px-4 border-b font-medium">Company Name</th>
              <th className="py-3 px-4 border-b font-medium">Verdict</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => {
              const verdictColor =
                log.risk_response?.verdict === "APPROVED"
                  ? "text-green-600"
                  : "text-red-600";
              return (
                <tr key={log.id} className="hover:bg-gray-50">
                  <td className="py-3 px-4 border-b">{log.business_name}</td>
                  <td className="py-3 px-4 border-b">
                    <button
                      onClick={() => handleResultClick("result", log)}
                      className={`${verdictColor} underline`}
                    >
                      {log.risk_response?.verdict}
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
