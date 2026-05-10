// frontend/src/components/ExecutionGraphVisualizer.tsx
import React, { useEffect, useState } from 'react';
import ReactFlow, { Node, Edge, Controls, MiniMap, Background, useNodesState, useEdgesState } from 'reactflow';
import 'reactflow/dist/style.css';

const nodeTypes = {
  execution: (props: any) => <div className="bg-blue-500 text-white p-2 rounded">Execution</div>,
  forecast: (props: any) => <div className="bg-green-500 text-white p-2 rounded">Forecast</div>,
  hardware: (props: any) => <div className="bg-purple-500 text-white p-2 rounded">Hardware</div>,
  agent: (props: any) => <div className="bg-orange-500 text-white p-2 rounded">Agent</div>,
};

export default function ExecutionGraphVisualizer({ runId }: { runId?: string }) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const loadGraph = async () => {
    const url = runId 
      ? `/api/graph/provenance/${runId}`
      : '/api/graph/world-state';
    
    const data = await fetch(url).then(r => r.json());

    const flowNodes: Node[] = Object.values(data.nodes || {}).map((n: any) => ({
      id: n.id,
      type: n.node_type,
      position: { x: Math.random() * 600, y: Math.random() * 400 },
      data: { label: `${n.node_type} • ${n.entity_id.slice(0,8)}` },
    }));

    const flowEdges: Edge[] = (data.edges || []).map((e: any) => ({
      id: e.id,
      source: e.source_id,
      target: e.target_id,
      label: e.relation,
      animated: true,
    }));

    setNodes(flowNodes);
    setEdges(flowEdges);
  };

  useEffect(() => {
    loadGraph();
  }, [runId]);

  return (
    <div className="h-[700px] border border-gray-300 rounded-xl overflow-hidden bg-white">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
      >
        <Controls />
        <MiniMap />
        <Background variant="dots" gap={12} size={1} />
      </ReactFlow>
    </div>
  );
}
