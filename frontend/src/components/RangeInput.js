import React, { useState, useEffect } from "react";

export const RangeInput = ({ value, onChange }) => {
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");

  // Split incoming value into start and end
  useEffect(() => {
    const [s, e] = value.split("-");
    setStart(s || "");
    setEnd(e || "");
  }, [value]);

  const handleStartChange = (newStart) => {
    setStart(newStart);
    onChange(`${newStart}-${end}`);
  };

  const handleEndChange = (newEnd) => {
    setEnd(newEnd);
    onChange(`${start}-${newEnd}`);
  };

  return (
    <div className="flex items-center space-x-2">
      <input
        type="number"
        value={start}
        onChange={(e) => handleStartChange(e.target.value)}
        className="w-20 px-2 py-1 border border-gray-300 rounded"
      />
      <span className="text-gray-600">-</span>
      <input
        type="number"
        value={end}
        onChange={(e) => handleEndChange(e.target.value)}
        className="w-20 px-2 py-1 border border-gray-300 rounded"
      />
    </div>
  );
};
