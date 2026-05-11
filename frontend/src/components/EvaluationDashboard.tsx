import React, { useEffect, useState } from 'react';
import { BarChart, Card, LineChart, Metric, Table, Text } from '@tremor/react';
import 'reactflow/dist/style.css';

const EvaluationDashboard: React.FC = () => {
  const [abTestData, setAbTestData] = useState<any[]>([]);
  const [brierTrend, setBrierTrend] = useState<any[]>([]);
  const [citationStats, setCitationStats] = useState<any>(null);

  useEffect(() => {
    // Fetch latest A/B test results
    const fetchData = async () => {
      const res = await fetch('/api/v1/evaluation/ab-test/results');
      const data = await res.json();
      setAbTestData(data.results || []);

      // Brier score trend over time
      const trendRes = await fetch('/api/v1/evaluation/brier-trend');
      const trendData = await trendRes.json();
      setBrierTrend(trendData || []);

      // Citation statistics
      const citRes = await fetch('/api/v1/evaluation/citation-stats');
      const citData = await citRes.json();
      setCitationStats(citData);
    };

    fetchData();
    const interval = setInterval(fetchData, 15000); // refresh every 15s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="h-screen bg-gray-950 text-white p-6 overflow-auto">
      <h1 className="text-3xl font-bold mb-6">📊 Evaluation & A/B Testing Dashboard</h1>

      <div className="grid grid-cols-12 gap-6">
        {/* Overall A/B Summary */}
        <Card className="col-span-12">
          <Text className="mb-4 text-lg">A/B Test Results — Treatment vs Control</Text>
          <Table
            data={abTestData}
            columns={[
              { header: 'Variant', accessor: 'variant' },
              { header: 'Avg Brier Score', accessor: 'avg_brier', cell: (v) => v.toFixed(4) },
              { header: 'Citation Rate', accessor: 'citation_rate', cell: (v) => `${(v * 100).toFixed(1)}%` },
              { header: 'Evidence Coverage', accessor: 'evidence_coverage', cell: (v) => `${(v * 100).toFixed(1)}%` },
              { header: 'Sample Size', accessor: 'sample_size' },
              { header: 'Last Test', accessor: 'last_test', cell: (v) => new Date(v).toLocaleDateString() },
            ]}
          />
        </Card>

        {/* Brier Score Trend */}
        <Card className="col-span-8">
          <Text>Brier Score Trend Over Time</Text>
          <LineChart
            data={brierTrend}
            index="date"
            categories={['control_brier', 'treatment_brier']}
            colors={['slate', 'violet']}
            yAxisWidth={60}
          />
        </Card>

        {/* Citation & Evidence Stats */}
        <Card className="col-span-4">
          <Text>Citation Performance</Text>
          <div className="mt-6 space-y-6">
            <div>
              <Text>Treatment Citation Rate</Text>
              <Metric color="violet">
                {citationStats ? `${(citationStats.treatment_citation_rate * 100).toFixed(1)}%` : '—'}
              </Metric>
            </div>
            <div>
              <Text>Control Citation Rate</Text>
              <Metric color="slate">
                {citationStats ? `${(citationStats.control_citation_rate * 100).toFixed(1)}%` : '—'}
              </Metric>
            </div>
            <div>
              <Text>Improvement</Text>
              <Metric color="emerald">
                {citationStats
                  ? `+${((citationStats.treatment_citation_rate - citationStats.control_citation_rate) * 100).toFixed(1)}%`
                  : '—'}
              </Metric>
            </div>
          </div>
        </Card>

        {/* Evidence ID Usage */}
        <Card className="col-span-12">
          <Text>Evidence ID Usage Distribution</Text>
          <BarChart
            data={[
              { name: 'Treatment', value: citationStats?.treatment_evidence_ids_used || 0 },
              { name: 'Control', value: citationStats?.control_evidence_ids_used || 0 },
            ]}
            index="name"
            categories={['value']}
            colors={['violet', 'slate']}
          />
        </Card>
      </div>
    </div>
  );
};

export default EvaluationDashboard;
