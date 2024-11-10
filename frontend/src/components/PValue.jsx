import React from 'react';
import PValueTable from './PValueTable';

const PValue = ({ data }) => {
  if (!data) return <p>No p-value data available.</p>;

  return (
    <div className="p-value-section">
      {Object.entries(data).map(([groupKey, groupData]) => (
        <div key={groupKey} className="p-value-group">
          <h3>{groupData.title}</h3>
          <PValueTable data={groupData.data} columnOrder={Object.keys(groupData.data)} />
        </div>
      ))}
    </div>
  );
};

export default PValue;
