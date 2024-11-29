import React from 'react';
import PValueTable from '../components/PValueTable';
import ChiSquareTable from '../components/ChiSquareTable';
import GenderPValueAnalysis from '../components/GenderPValueAnalysis';
import CumulativePValueTables from '../components/CumulativePvalueTables';
import '../style/Analysis.css';

const AccuracyAnalysis = ({ accuracyData }) => {
  if (!accuracyData) return <p>No accuracy data available.</p>;

  return (
    <div className="analysis-container">
      <h2 className="title">Accuracy Analysis</h2>

      <h2 style={{ color: 'green' }}>Cumulative Session Analysis</h2>
      {accuracyData?.p_value?.between_group && (
        <div className="table-section">
          <h3 className="section-title">{accuracyData.p_value.between_group.title}</h3>
          <PValueTable
            data={accuracyData.p_value.between_group.data}
            columnOrder={["ADHD Mean ± SD", "Non-ADHD Mean ± SD", "p_value_between"]}
          />
        </div>
      )}

      {accuracyData?.p_value?.within_group && (
        <div className="table-section">
          <h3 className="section-title">{accuracyData.p_value.within_group.title}</h3>
          <PValueTable
            data={accuracyData.p_value.within_group.data}
            columnOrder={["Mean ± SD With Distraction", "Mean ± SD Without Distraction", "p_value_within"]}
          />
        </div>
      )}

      <h2 style={{ color: 'green' }}>Gender-Based Analysis</h2>
      <h2>Per Session</h2>
      <GenderPValueAnalysis genderData={accuracyData.trend_pvalue.data} />
      <h2>Cumulative</h2>
      <CumulativePValueTables data={accuracyData.cumulative_pvalues.data} />
    </div>
  );
};

export default AccuracyAnalysis;
