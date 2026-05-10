// frontend/src/components/ExecutionGraphVisualizer.tsx
import React, { useEffect, useState, useCallback } from 'react';
import ReactFlow, { 
  Node, Edge, Controls, MiniMap, Background, 
  useNodesState, useEdgesState 
} from 'reactflow';
import 'reactflow/dist/style.css';

const nodeTypes = {
  execution: (props: any) => (
    <div className="bg-blue-600 text-white px-4 py-2 rounded-lg shadow">🚀 Execution</div>
  ),
  forecast: (props: any) => (
    <div className="bg-green-600 text-white px-4 py-2 rounded-lg shadow">📈 Forecast</div>
  ),
  hardware: (props: any) => (
    <div className="bg-purple-600 text-white px-4 py-2 rounded-lg shadow">🖥️ Hardware</div>
  ),
  agent: (props: any) => (
    <div className="bg-orange-600 text-white px-4 py-2 rounded-lg shadow">🤖 Agent</div>
  ),
};

export default function ExecutionGraphVisualizer({ runId }: { runId?: string }) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(true);

  const loadGraph = useCallback(async () => {
    setLoading(true);
    try {
      const url = runId 
        ? `/api/graph/provenance/${runId}?depth=5`
        : '/api/graph/world-state';
      
      const res = await fetch(url);
      const data = await res.json();

      const flowNodes: Node[] = Object.values(data.nodes || {}).map((n: any, i: number) => ({
        id: n.id,
        type: n.node_type || 'execution',
        position: { x: i * 180, y: i * 80 },
        data: { 
          label: `${n.node_type?.toUpperCase()} • ${n.entity_id?.slice(0,8)}`,
          ...n 
        },
      }));

      const flowEdges: Edge[] = (data.edges || []).map((e: any) => ({
        id: e.id,
        source: e.source_id,
        target: e.target_id,
        label: e.relation,
        animated: true,
        style: { stroke: '#64748b' },
      }));

      setNodes(flowNodes);
      setEdges(flowEdges);
    } catch (e) {
      console.error("Failed to load graph", e);
    } finally {
      setLoading(false);
    }
  }, [runId]);

  useEffect(() => {
    loadGraph();
  }, [loadGraph]);

  return (
    <div className="h-[720px] w-full border border-gray-300 rounded-2xl overflow-hidden bg-gray-50">
      {loading && <div className="absolute inset-0 flex items-center justify-center">Loading Graph...</div>}
      
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        attributionPosition="bottom-left"
      >
        <Controls />
        <MiniMap />
        <Background variant="dots" gap={12} size={1} />
      </ReactFlow>
    </div>
  );
}
