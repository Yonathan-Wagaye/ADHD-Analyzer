import React from 'react';
import '../style/PlotCard.css';

const PlotCard = ({ title, description, plots }) => {
  return (
    <div className="plot-card">
      <h3 className="plot-card-title">{title}</h3>
      <div className="plot-card-content">
        {plots.length === 2 ? (
          <div className="plot-images">
            <img src={plots[0]} alt="Plot 1" className="plot-image" />
            <img src={plots[1]} alt="Plot 2" className="plot-image" />
          </div>
        ) : (
          <div className="plot-image-single">
            <img src={plots[0]} alt="Single Plot" className="plot-image" />
            {description && <p className="plot-description">{description}</p>}
          </div>
        )}
      </div>
    </div>
  );
};

export default PlotCard;
