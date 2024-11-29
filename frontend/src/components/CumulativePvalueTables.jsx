import React from "react";
import "../style/TableStyles.css"; // Import the CSS file for table styles

const CumulativePValueTables = ({ data }) => {
  const tableTitles = {
    ADHD_Male_vs_ADHD_Female: "ADHD Male vs ADHD Female",
    NonADHD_Male_vs_NonADHD_Female: "Non-ADHD Male vs Non-ADHD Female",
    ADHD_Male_vs_NonADHD_Male: "ADHD Male vs Non-ADHD Male",
    ADHD_Female_vs_NonADHD_Female: "ADHD Female vs Non-ADHD Female",
  };

  const groupLabels = {
    ADHD_Male_vs_ADHD_Female: { group1: "ADHD_Male", group2: "ADHD_Female" },
    NonADHD_Male_vs_NonADHD_Female: { group1: "NonADHD_Male", group2: "NonADHD_Female" },
    ADHD_Male_vs_NonADHD_Male: { group1: "ADHD_Male", group2: "NonADHD_Male" },
    ADHD_Female_vs_NonADHD_Female: { group1: "ADHD_Female", group2: "NonADHD_Female" },
  };

  return (
    <div className="cumulative-pvalue-tables">
      {Object.keys(data).map((key) => (
        <div key={key} className="cumulative-pvalue-table">
          <h3>{tableTitles[key]}</h3>
          <table className="styled-table">
            <thead>
              <tr>
                <th>{groupLabels[key].group1} (Mean ± Std)</th>
                <th>{groupLabels[key].group2} (Mean ± Std)</th>
                <th>P-Value</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>{data[key].mean_std[groupLabels[key].group1]}</td>
                <td>{data[key].mean_std[groupLabels[key].group2]}</td>
                <td
                  style={{
                    color: data[key].p_value < 0.05 ? "red" : "inherit",
                    fontWeight: data[key].p_value < 0.05 ? "bold" : "normal",
                  }}
                >
                  {data[key].p_value.toFixed(3)}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      ))}
    </div>
  );
};

export default CumulativePValueTables;
