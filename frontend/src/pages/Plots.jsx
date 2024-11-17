import React, { useEffect, useState } from 'react';
import { fetchPlotData } from '../api';
import PlotCard from '../components/PlotCard';
import '../style/Plots.css';

const Plots = () => {
  const [plots, setPlots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await fetchPlotData();
        setPlots(data.plots);
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
      <h3>General Acuuracy Trendines</h3>
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

export default Plots;
