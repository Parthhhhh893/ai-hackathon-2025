import { RangeInput } from "./RangeInput";

export const ThresholdCategory = ({ label, values, onChange }) => {
  function toTitleCaseLabel(str) {
    return str
      .replace(/_/g, " ") // Replace underscores with spaces
      .replace(
        /\w\S*/g,
        (word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
      );
  }
  return (
    <div className="mb-4 flex items-center gap-3">
      <h4 className="text-sm font-medium ">{toTitleCaseLabel(label)}:</h4>
      <div className="grid grid-cols-3 gap-2">
        {Object.entries(values).map(([key, range]) => (
          <div key={key} className="flex items-center">
            <span className="mr-2 text-xs text-gray-500"> {key}</span>

            <div className="flex items-center space-x-2">
              <RangeInput
                value={range}
                onChange={(value) => onChange(label, key, value)}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
