import React from 'react';

const Analysis = ({ data }) => {
  if (!data) return <p>No data available. Please upload a file first.</p>;

  return (
    <div>
      <h2>Analysis Results</h2>
      <p>Message: {data.message}</p>
      <h3>Statistics:</h3>
      <pre>{JSON.stringify(data.stats, null, 2)}</pre>
    </div>
  );
};

export default Analysis;
