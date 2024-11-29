import React from 'react';
import PlotCard from './PlotCard';
import '../style/Plots.css';

const AccuracyPlot = ({ plots }) => {
  return (
    <div>
      <h3>General Accuracy Trendlines</h3>
      <div className="plot-card-container">
        {plots.map((plot, index) => (
          <PlotCard
            key={index}
            title={plot.title}
            plots={[`data:image/png;base64,${plot.plotUrl}`]}
            description={plot.description}
          />
        ))}
      </div>
    </div>
  );
};

export default AccuracyPlot;
