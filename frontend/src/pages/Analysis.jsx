import React, { useEffect, useState } from 'react';
import { fetchAnalysisData } from '../api';
import PValueTable from '../components/PValueTable';
import ChiSquareTable from '../components/ChiSquareTable';
import '../style/Analysis.css';
import GenderPValueAnalysis from '../components/GenderPValueAnalysis';

const Analysis = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await fetchAnalysisData();
        console.log("Fetched Data: ", data); // Log API response
        setAnalysisResult(data.stats);
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

  console.log(analysisResult);
  

  return (
    <div className="analysis-container">
      <h2 className="title">Analysis Results</h2>
      <h2>Accuracy Analysis</h2>
      <h2 style={{ color: 'green' }}>Cumuliatve Session Analysis</h2>
      {analysisResult?.p_value?.between_group && (
        <div className="table-section">
          <h3 className="section-title">{analysisResult.p_value.between_group.title}</h3>
          <PValueTable
            data={analysisResult.p_value.between_group.data}
            columnOrder={["ADHD Mean ± SD", "Non-ADHD Mean ± SD", "p_value_between"]}
          />
        </div>
      )}
      {analysisResult?.p_value?.within_group && (
        <div className="table-section">
          <h3 className="section-title">{analysisResult.p_value.within_group.title}</h3>
          <PValueTable
            data={analysisResult.p_value.within_group.data}
            columnOrder={["Mean ± SD With Distraction", "Mean ± SD Without Distraction", "p_value_within"]}
          />
        </div>
      )}
      <h2 style={{ color: 'green' }}>General Session Trendline Analysis</h2>
      <h3>Chi Square Analysis Across Sessions</h3>
      <ChiSquareTable data={analysisResult?.chi_square?.data} />
      <h3>Comparision among gender groups</h3>
      <GenderPValueAnalysis genderData={analysisResult.trend_pvalue.data} />
    </div>
  );
};

export default Analysis;
