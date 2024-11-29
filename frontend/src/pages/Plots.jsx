import React, { useEffect, useState } from 'react';
import AccuracyPlot from '../components/AccuracyPlot';
import PosePlot from '../components/PosePlot';
import { fetchPlotData } from '../api';
import '../style/Plots.css';

const Plots = () => {
  const [selectedCategory, setSelectedCategory] = useState('accuracy');
  const [accuracyPlots, setAccuracyPlots] = useState([]);
  const [posePlots, setPosePlots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await fetchPlotData();

        // Separate plots for accuracy and pose
        setAccuracyPlots(data.accuracy_plots || []);
        setPosePlots(data.pose_plots || []);
      } catch (err) {
        setError(`Failed to fetch plot data: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <p>Loading plots...</p>;
  if (error) return <p style={{ color: 'red' }}>{error}</p>;

  return (
    <div>
      <h2 className="page-title">Plots</h2>
      <div className="dropdown-container">
        <label htmlFor="plot-category">Select Plot Category:</label>
        <select
          id="plot-category"
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
        >
          <option value="accuracy">Accuracy Plots</option>
          <option value="pose">Pose Stability Plots</option>
        </select>
      </div>
      {selectedCategory === 'accuracy' && <AccuracyPlot plots={accuracyPlots} />}
      {selectedCategory === 'pose' && <PosePlot plots={posePlots} />}
    </div>
  );
};

export default Plots;
