import React from 'react';
import '../style/PValueTable.css';

const PValueTable = ({ data, columnOrder }) => {
  if (!data || !columnOrder || columnOrder.length === 0) return <p>No data available to display.</p>;

  const rowLabels = Object.keys(data);

  return (
    <table className="p-value-table">
      <thead>
        <tr>
          <th>Condition</th>
          {columnOrder.map((col, index) => (
            <th key={index}>{col}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rowLabels.map((label, rowIndex) => (
          <tr key={rowIndex}>
            <td>{label}</td>
            {columnOrder.map((col, colIndex) => (
              <td
                key={colIndex}
                style={{
                  color: col.toLowerCase().includes('p_value') && data[label][col] < 0.05 ? 'red' : 'inherit',
                }}
              >
                {data[label][col] !== undefined ? data[label][col] : ''}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default PValueTable;
