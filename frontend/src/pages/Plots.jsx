import React from 'react';
import '../style/Plots.css'
const Plots = ({ plotUrls }) => {
  if (!plotUrls) return <p>No plot available. Please upload data on the Home page.</p>;

  return (
    <div>
      <h1>Box Plots: ADHD Accuracy with Distraction vs Non-Distraction</h1>
      {Object.entries(plotUrls).map(([key, plotUrl], index) => (
        <div key={index}>
          <h3>Plot {index + 1}</h3>
          <img src={`data:image/png;base64,${plotUrl}`} alt={`Plot ${index + 1}`} />
        </div>
      ))}
    </div>
  );
};

export default Plots;
