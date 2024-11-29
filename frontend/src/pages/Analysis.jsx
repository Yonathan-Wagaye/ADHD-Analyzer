import React, { useEffect, useState } from 'react';
import { fetchAnalysisData } from '../api';
import AccuracyAnalysis from '../components/AccuracyAnalysis';
import PoseAnalysis from '../components/PoseAnalsysis';

const Analysis = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [selectedAnalysis, setSelectedAnalysis] = useState('accuracy'); // Default to 'accuracy'

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await fetchAnalysisData();
        console.log("Fetched Data: ", data); // Log API response
        setAnalysisResult(data);
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
      <h2>Analysis Results</h2>
      <div className="dropdown-container">
        <label htmlFor="analysis-select">Select Analysis Type: </label>
        <select
          id="analysis-select"
          value={selectedAnalysis}
          onChange={(e) => setSelectedAnalysis(e.target.value)}
        >
          <option value="accuracy">Accuracy Analysis</option>
          <option value="pose">Pose Analysis</option>
        </select>
      </div>

      {selectedAnalysis === 'accuracy' && analysisResult?.accuracy && (
        <AccuracyAnalysis accuracyData={analysisResult.accuracy} />
      )}

      {selectedAnalysis === 'pose' && analysisResult?.pose && (
        <PoseAnalysis poseData={analysisResult.pose} />
      )}
    </div>
  );
};

export default Analysis;
