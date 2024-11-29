import React, { useEffect, useState } from 'react';
import { fetchInfoData } from '../api'; // Adjust to your API utilities location
import '../style/Info.css';

const Info = () => {
  const [infoData, setInfoData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await fetchInfoData();
        setInfoData(data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <div className="info-container">Loading...</div>;
  }

  if (error) {
    return <div className="info-container error">Error: {error}</div>;
  }

  if (!infoData) {
    return <div className="info-container">No data available</div>;
  }

  return (
    <div className="info-container">
      <h1>Experiment Information</h1>
      <div className="info-description">
        <p>
          This section provides a summary of the pre-experiment and post-experiment analysis.
          The plots and statistical analyses are based on participant data categorized by ADHD and non-ADHD groups.
        </p>
      </div>

      <div className="info-section">
        <h2>Participant Counts</h2>
        <ul className="participant-counts">
          {Object.entries(infoData.participant_counts).map(([key, value]) => (
            <li key={key}>
              <strong>{key}:</strong> {value}
            </li>
          ))}
        </ul>
      </div>

      <div className="info-section">
        <h2>Pre-Experiment Plot</h2>
        <div className="plot-container">
          <img
            src={`data:image/png;base64,${infoData.plots[0].plotUrl}`}
            alt={infoData.plots[0].title}
          />
          <p>{infoData.plots[0].description}</p>
        </div>
      </div>

      <div className="info-section">
        <h2>Post-Experiment Plots</h2>
        <div className="plot-row">
          <div className="plot-container">
            <img
              src={`data:image/png;base64,${infoData.plots[1].plotUrl}`}
              alt="ADHD Distraction Levels"
            />
            <p>Level of Distraction - ADHD</p>
          </div>
          <div className="plot-container">
            <img
              src={`data:image/png;base64,${infoData.plots[2].plotUrl}`}
              alt="Non-ADHD Distraction Levels"
            />
            <p>Level of Distraction - Non-ADHD</p>
          </div>
        </div>
        <div className="plot-row">
        <h3 style={{marginTop: '50px'}}>Level of Distraction - By Gender</h3>
          {infoData.gender_box_plots.map((plot, index) => (
            <div className="plot-container" key={index}>
              <img src={`data:image/png;base64,${plot.plotUrl}`} alt={plot.title} />
              <p>{plot.description}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="info-section">
        <h2>Statistical Analysis (P-Values)</h2>
        <table className="styled-table">
          <thead>
            <tr>
              <th>Distraction Type</th>
              <th>P-Value</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(infoData.p_values).map(([key, value]) => (
              <tr key={key}>
                <td>{key}</td>
                <td
                  style={
                    value < 0.05
                      ? { color: 'red', fontWeight: 'bold' }
                      : {}
                  }
                >{value.toFixed(4)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Info;
