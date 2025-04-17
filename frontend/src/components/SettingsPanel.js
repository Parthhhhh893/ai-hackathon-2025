import { ThresholdCategory } from "./ThresholdCategory";
import ThresholdSection from "./ThresholdSection";

export const SettingsPanel = ({
  threshold,
  setThreshold,
  defaultThreshold,
  setDefaultThreshold,
  thresholdConfig,
  updateThresholdConfig,
}) => {
  const updateThreshold = () => {
    setDefaultThreshold(threshold);
    alert("Default threshold updated successfully!");
  };

  return (
    <div>
      <div className="space-y-6">
        <h3 className="text-xl font-medium mb-4">Configurations</h3>
        <ThresholdSection isSetting={true} />
      </div>
    </div>
  );
};
