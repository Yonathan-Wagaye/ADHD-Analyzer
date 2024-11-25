import React from "react";
import GenderPValueTable from "./GenderPValueTable";

const GenderPValueAnalysis = ({ genderData }) => {
  const groupLabels = {
    ADHD_Male_vs_ADHD_Female: { group1: "ADHD_Male", group2: "ADHD_Female" },
    NonADHD_Male_vs_NonADHD_Female: { group1: "NonADHD_Male", group2: "NonADHD_Female" },
    ADHD_Male_vs_NonADHD_Male: { group1: "ADHD_Male", group2: "NonADHD_Male" },
    ADHD_Female_vs_NonADHD_Female: { group1: "ADHD_Female", group2: "NonADHD_Female" },
  };

  return (
    <div className="gender-analysis">
      {Object.keys(genderData).map((comparisonKey, index) => (
        <GenderPValueTable
          key={index}
          title={comparisonKey.replace(/_/g, " ")} // Format title for readability
          data={genderData[comparisonKey]}
          groupLabels={groupLabels[comparisonKey]} // Pass appropriate group labels
        />
      ))}
    </div>
  );
};

export default GenderPValueAnalysis;
