import React from "react";
import '../style/ChiSquareTable.css'

const ChiSquareTable = ({ data }) => {
  if (!data || Object.keys(data).length === 0) {
    return <p>No Chi-Square data available.</p>;
  }

  return (
    <table className="styled-table">
      <thead>
        <tr>
          <th>Session</th>
          <th>Chi2</th>
          <th>P-Value</th>
          <th>Observed (ADHD, Non-ADHD)</th>
          <th>Expected (ADHD, Non-ADHD)</th>
        </tr>
      </thead>
      <tbody>
        {Object.entries(data).map(([session, result]) => (
          <tr key={session}>
            <td>{session}</td>
            <td>{result.chi2.toFixed(4)}</td>
            {/* Highlight significant p-values in red */}
            <td style={{ color: result.p_value < 0.05 ? "red" : "inherit" }}>
              {result.p_value.toFixed(4)}
            </td>
            <td>{result.observed.join(", ")}</td>
            <td>{result.expected.join(", ")}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default ChiSquareTable;
