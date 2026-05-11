import React, { useEffect, useState } from 'react';
import { Card, Metric, Text, Table } from '@tremor/react';

const EvaluationDashboard: React.FC = () => {
  const [abTestData, setAbTestData] = useState<any[]>([]);
  const [brierTrend, setBrierTrend] = useState<any[]>([]);
  const [citationStats, setCitationStats] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('/api/v1/evaluation/ab-test/results');
        const data = await res.json();
        setAbTestData(data.results || []);

        const trendRes = await fetch('/api/v1/evaluation/brier-trend');
        const trendData = await trendRes.json();
        setBrierTrend(trendData || []);

        const citRes = await fetch('/api/v1/evaluation/citation-stats');
        const citData = await citRes.json();
        setCitationStats(citData);
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="h-screen bg-gray-950 text-white p-6 overflow-auto">
      <h1 className="text-3xl font-bold mb-6">📊 Evaluation & A/B Testing Dashboard</h1>

      <div className="grid grid-cols-12 gap-6">
        <Card className="col-span-12">
          <Text className="mb-4 text-lg">A/B Test Results — Treatment vs Control</Text>
          <Table>
            {/* Tremor v3 Table syntax */}
          </Table>
        </Card>

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
              <Text>Improvement</Text>
              <Metric color="emerald">
                {citationStats 
                  ? `+${((citationStats.treatment_citation_rate - citationStats.control_citation_rate) * 100).toFixed(1)}%` 
                  : '—'}
              </Metric>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default EvaluationDashboard;
