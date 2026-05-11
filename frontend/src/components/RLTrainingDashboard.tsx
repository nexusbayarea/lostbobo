import React, { useEffect, useState } from 'react';
import { Card, Metric, Text, Table, Button, LineChart, BarChart } from '@tremor/react';
import 'reactflow/dist/style.css';

const RLTrainingDashboard: React.FC = () => {
  const [trainingData, setTrainingData] = useState<any>(null);
  const [snapshots, setSnapshots] = useState<any[]>([]);

  // Poll RL training metrics
  useEffect(() => {
    const interval = setInterval(async () => {
      const res = await fetch('/api/v1/core/rl-training-stats');
      const data = await res.json();
      setTrainingData(data);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  // Load snapshots
  useEffect(() => {
    fetch('/api/v1/core/rl/snapshots?limit=10')
      .then(r => r.json())
      .then(setSnapshots);
  }, []);

  return (
    <div className="h-screen bg-gray-950 text-white p-6 flex flex-col gap-6 overflow-auto">
      <h1 className="text-3xl font-bold flex items-center gap-3">
        🧠 RL Training & Policy Visualization
      </h1>

      <div className="grid grid-cols-12 gap-6">
        {/* Reward Trajectory */}
        <Card className="col-span-8">
          <Text>Reward Trajectory (Training Progress)</Text>
          <LineChart
            data={trainingData?.reward_history?.map((r: number, i: number) => ({
              step: i,
              reward: r,
              moving_avg: trainingData?.moving_avg?.[i] || r
            })) || []}
            index="step"
            categories={["reward", "moving_avg"]}
            colors={["violet", "emerald"]}
          />
        </Card>

        {/* Policy Distribution */}
        <Card className="col-span-4">
          <Text>Current Policy Distribution</Text>
          <BarChart
            data={[
              { name: "Sandbox", value: trainingData?.action_distribution?.sandbox || 0 },
              { name: "WASM", value: trainingData?.action_distribution?.wasm || 0 },
              { name: "Kata", value: trainingData?.action_distribution?.kata || 0 },
            ]}
            index="name"
            categories={["value"]}
            colors={["emerald", "amber", "violet"]}
          />
        </Card>

        {/* Recent Decisions */}
        <Card className="col-span-12">
          <Text>Recent RL Decisions</Text>
          <Table
            data={trainingData?.recent_decisions?.slice(0, 8) || []}
            columns={[
              { header: "Time", accessor: "timestamp", cell: (v) => new Date(v * 1000).toLocaleTimeString() },
              { header: "Action", accessor: "action" },
              { header: "Reward", accessor: "reward" },
            ]}
          />
        </Card>

        {/* Snapshots with Restore Button */}
        <Card className="col-span-12">
          <Text>Policy Snapshots (One-Click Restore)</Text>
          <Table
            data={snapshots}
            columns={[
              { header: "Snapshot ID", accessor: "snapshot_id", cell: (v) => v.slice(0, 8) + "..." },
              { header: "Time", accessor: "timestamp", cell: (v) => new Date(v * 1000).toLocaleString() },
              { header: "Epsilon", accessor: "epsilon" },
              { header: "Reward", accessor: "last_reward" },
              {
                header: "Action",
                accessor: "snapshot_id",
                cell: (id) => (
                  <Button
                    size="xs"
                    variant="secondary"
                    onClick={async () => {
                      if (window.confirm(`Restore policy from snapshot ${id}?`)) {
                        await fetch(`/api/v1/core/rl/snapshot/${id}/restore`, { method: 'POST' });
                        alert('Policy restored successfully!');
                      }
                    }}
                  >
                    Restore
                  </Button>
                )
              }
            ]}
          />
        </Card>
      </div>
    </div>
  );
};

export default RLTrainingDashboard;
