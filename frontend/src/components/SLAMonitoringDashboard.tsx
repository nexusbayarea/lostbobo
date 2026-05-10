import React, { useEffect, useState } from "react";
import { Card, Metric, ProgressBar, Table } from "@tremor/react";

interface SLAStats {
  overall_compliance: number;
  by_tier: Record<string, { compliance: number; breaches: number; avg_queue_ms: number }>;
  breaches_last_24h: number;
  active_isolated_reserve: number;
  avg_queue_ms: number;
  itar_compliance_pct: number;
  warm_hit_rate: number;
  health_score?: number;
  active_alerts?: number;
  critical_breaches?: number;
}

export default function SLAMonitoringDashboard() {
  const [stats, setStats] = useState<SLAStats | null>(null);
  const [breaches, setBreaches] = useState<any[]>([]);

  useEffect(() => {
    fetch("/sla/status")
      .then((r) => r.json())
      .then((d) => setStats((prev) => ({ ...prev, ...d })));
    fetch("/sla/breaches")
      .then((r) => r.json())
      .then(setBreaches);
    fetch("/sla/health")
      .then((r) => r.json())
      .then((d) => setStats((prev) => (prev ? { ...prev, ...d } : d as SLAStats)));
  }, []);

  if (!stats) return <div>Loading SLA Dashboard...</div>;

  const health = stats.health_score ?? 92;
  const activeAlerts = stats.active_alerts ?? 0;
  const critical = stats.critical_breaches ?? 0;

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">SLA Monitoring Dashboard</h1>

      <Card>
        <Metric>Overall SLA Health: {health}%</Metric>
        <ProgressBar value={health} color="emerald" className="mt-2" />
      </Card>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Object.entries(stats.by_tier || {}).map(([tier, data]) => (
          <Card key={tier}>
            <div className="text-sm text-gray-500 capitalize">{tier}</div>
            <Metric>{data.compliance}%</Metric>
            <p className="text-xs text-gray-400">
              {data.breaches} breaches &bull; {data.avg_queue_ms}ms avg queue
            </p>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-4">
        <Card>
          <div className="text-sm text-gray-500">Warm Hit Rate</div>
          <Metric>{stats.warm_hit_rate}%</Metric>
        </Card>
        <Card>
          <div className="text-sm text-gray-500">ITAR Compliance</div>
          <Metric>{stats.itar_compliance_pct}%</Metric>
        </Card>
        <Card>
          <div className="text-sm text-gray-500">24h Breaches</div>
          <Metric className={stats.breaches_last_24h > 0 ? "text-red-600" : ""}>
            {stats.breaches_last_24h}
          </Metric>
        </Card>
      </div>

      <Card>
        <h3 className="text-lg font-medium mb-4">Recent SLA Breaches</h3>
        <Table>
          <thead>
            <tr>
              <th>Time</th>
              <th>Tier</th>
              <th>Incident</th>
              <th>Impact</th>
            </tr>
          </thead>
          <tbody>
            {breaches.slice(0, 8).map((b) => (
              <tr key={b.id}>
                <td>{new Date(b.created_at).toLocaleTimeString()}</td>
                <td className="capitalize">{b.sla_tier}</td>
                <td>{b.description || b.breach_type}</td>
                <td className="text-red-600">{b.credit_usd}$ credit</td>
              </tr>
            ))}
          </tbody>
        </Table>
      </Card>
    </div>
  );
}
