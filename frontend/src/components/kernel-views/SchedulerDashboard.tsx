import React from 'react';

export default function SchedulerDashboard() {
  return (
    <div className="h-full p-4 border rounded-xl bg-card">
      <h2 className="text-xl font-bold mb-4">Scheduler Status</h2>
      <div className="grid grid-cols-2 gap-4">
        <div className="border p-4 rounded-lg bg-background">Queue Depth Monitoring</div>
        <div className="border p-4 rounded-lg bg-background">GPU/MIG Allocation Map</div>
        <div className="border p-4 rounded-lg bg-background col-span-2">Tenant Fairness and SLA Compliance</div>
      </div>
    </div>
  );
}
