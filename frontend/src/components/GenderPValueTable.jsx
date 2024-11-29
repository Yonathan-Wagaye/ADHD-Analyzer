import React from "react";
import "../style/TableStyles.css"; // Import the CSS file for table styles



const GenderPValueTable = ({ data, title, groupLabels }) => {
  return (
    <div className="gender-pvalue-table">
      <h3>{title}</h3>
      <table className="styled-table">
        <thead>
          <tr>
            <th>Session</th>
            <th>P-Value</th>
            <th>{groupLabels.group1} (Mean ± Std)</th>
            <th>{groupLabels.group2} (Mean ± Std)</th>
          </tr>
        </thead>
        <tbody>
          {Object.keys(data.p_values).map((session, index) => (
            <tr key={index}>
              <td>{session}</td>
              <td
                style={{
                  color: data.p_values[session] < 0.05 ? "red" : "inherit",
                  fontWeight: data.p_values[session] < 0.05 ? "bold" : "normal",
                }}
              >
                {data.p_values[session].toFixed(3)}
              </td>
              <td>{data.mean_std[session][groupLabels.group1]}</td>
              <td>{data.mean_std[session][groupLabels.group2]}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default GenderPValueTable;
