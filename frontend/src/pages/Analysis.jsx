import React, { useEffect, useState } from 'react';
import { fetchAnalysisData } from '../api';
import PValueTable from '../components/PValueTable';
import '../style/Analysis.css';

const Analysis = () => {
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await fetchAnalysisData();
        setAnalysisData(data.stats.p_value); // Access p_value data directly
      } catch (err) {
        setError(`Failed to fetch analysis data: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <p>Loading analysis data...</p>;
  if (error) return <p style={{ color: 'red' }}>{error}</p>;

  return (
    <div className="analysis-container">
      <h2 className="title">Analysis Results</h2>
      {analysisData && analysisData.between_group && (
        <div className="table-section">
          <h3 className="section-title">{analysisData.between_group.title}</h3>
          <PValueTable
            data={analysisData.between_group.data}
            columnOrder={["ADHD Mean ± SD", "Non-ADHD Mean ± SD", "p_value_between"]}
          />
        </div>
      )}
      {analysisData && analysisData.within_group && (
        <div className="table-section">
          <h3 className="section-title">{analysisData.within_group.title}</h3>
          <PValueTable
            data={analysisData.within_group.data}
            columnOrder={["Mean ± SD With Distraction", "Mean ± SD Without Distraction", "p_value_within"]}
          />
        </div>
      )}
    </div>
  );
};

export default Analysis;
