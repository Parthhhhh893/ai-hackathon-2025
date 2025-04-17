import { Building, ClipboardList, Settings } from "lucide-react";

export const TabNavigation = ({ activeTab, setActiveTab }) => {
  const tabs = [
    {
      id: "logs",
      label: "Reports",
      icon: <ClipboardList className="w-5 h-5 mr-2" />,
    },
    {
      id: "business",
      label: "Generate Report",
      icon: <Building className="w-5 h-5 mr-2" />,
    },
    {
      id: "settings",
      label: "Config",
      icon: <Settings className="w-5 h-5 mr-2" />,
    },
  ];

  return (
    <div className="flex border-b border-gray-200 mb-6">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => setActiveTab(tab.id)}
          className={`flex items-center py-3 px-6 ${
            activeTab === tab.id
              ? "border-b-2 border-blue-500 text-blue-600 font-medium"
              : "text-gray-500 hover:text-blue-500"
          }`}
        >
          {tab.icon}
          {tab.label}
        </button>
      ))}
    </div>
  );
};
