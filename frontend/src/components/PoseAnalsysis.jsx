import React from 'react';
import PValueTable from '../components/PValueTable';
import GenderPValueTable from './GenderPValueTable';
import '../style/Analysis.css';
import GenderPValueAnalysis from './GenderPValueAnalysis';
import CumulativePValueTables from './CumulativePvalueTables';

const PoseAnalysis = ({ poseData }) => {
  if (!poseData) return <p>No pose data available.</p>;
    console.log('iN POSE ANALYSIS', poseData)
;  return (
    <div className="analysis-container">
      <h2 className="title">Pose Analysis</h2>

      <h2 style={{ color: 'green' }}>Cumulative Session Analysis</h2>
      {poseData?.threshold_15?.data?.p_value?.between_group && (
        <div className="table-section">
          <h3 className="section-title">{poseData.threshold_15.data.p_value.between_group.title}</h3>
          <PValueTable
            data={poseData.threshold_15.data.p_value.between_group.data}
            columnOrder={["ADHD Mean ± SD", "Non-ADHD Mean ± SD", "p_value_between"]}
          />
          {console.log('after rendeting cummmulraive 1')}
        </div>
      )}

      {poseData?.threshold_15?.data?.p_value?.within_group && (
        <div className="table-section">
          <h3 className="section-title">{poseData?.threshold_15?.data?.p_value?.within_group.title}</h3>
          <PValueTable
            data={poseData.threshold_15.data.p_value.within_group.data}
            columnOrder={["Mean ± SD With Distraction", "Mean ± SD Without Distraction", "p_value_within"]}
          />
          {console.log('after rendeting cummmulraive 2')}
        </div>
        
      )}

    {poseData?.trend_pvalue && (
        <div className="table-section">
          <h3 className="section-title">{poseData.trend_pvalue.title}</h3>
          <GenderPValueTable
            data={poseData.trend_pvalue.data['ADHD_vs_NonADHD']}
            title="Pose Trendline P-Values"
            groupLabels={{
              group1: "ADHD",
              group2: "Non-ADHD",
            }}
          />
          {console.log('Rendered trendline analysis')}
        </div>
      )}
      <h2 style={{ color: 'green' }}>Gender-Based Analysis</h2>
      <h2>Per Session</h2>
      <GenderPValueAnalysis genderData={poseData.gender_trend_p_value.data} />
      <h2>Cumulative</h2>
      <CumulativePValueTables data={poseData.cumulative_pvalues.data} />
    </div>
  );
};

export default PoseAnalysis;
