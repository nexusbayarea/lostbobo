// frontend/src/components/LineageVisualizer.tsx
import React, { useEffect, useState, useCallback } from 'react';
import ReactFlow, {
  Node, Edge, Controls, MiniMap, Background,
  useNodesState, useEdgesState
} from 'reactflow';
import 'reactflow/dist/style.css';

const nodeTypes = {
  execution: (props: any) => (
    <div className="bg-blue-600 text-white px-4 py-3 rounded-xl shadow text-center text-sm font-medium">
      🚀 Execution
    </div>
  ),
  model: (props: any) => (
    <div className="bg-emerald-600 text-white px-4 py-3 rounded-xl shadow text-center text-sm font-medium">
      📦 Model
    </div>
  ),
  agent: (props: any) => (
    <div className="bg-violet-600 text-white px-4 py-3 rounded-xl shadow text-center text-sm font-medium">
      🤖 Agent
    </div>
  ),
  hardware: (props: any) => (
    <div className="bg-amber-600 text-white px-4 py-3 rounded-xl shadow text-center text-sm font-medium">
      🖥️ Hardware
    </div>
  ),
  dataset: (props: any) => (
    <div className="bg-teal-600 text-white px-4 py-3 rounded-xl shadow text-center text-sm font-medium">
      📊 Dataset
    </div>
  ),
  dag_node: (props: any) => (
    <div className="bg-rose-600 text-white px-4 py-3 rounded-xl shadow text-center text-sm font-medium">
      ⚙️ DAG Node
    </div>
  ),
};

export default function LineageVisualizer({ executionId }: { executionId?: string }) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<any>(null);

  const loadLineage = useCallback(async () => {
    if (!executionId) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/graph/lineage/${executionId}`);
      const data = await res.json();

      const flowNodes: Node[] = data.nodes.map((n: any, i: number) => ({
        id: n.id,
        type: n.type || 'execution',
        position: { x: i * 220 + (Math.random() * 80), y: i * 120 + (Math.random() * 60) },
        data: {
          label: n.name || n.type,
          ...n
        },
      }));

      const flowEdges: Edge[] = data.edges.map((e: any) => ({
        id: e.id || `${e.source}-${e.target}`,
        source: e.source,
        target: e.target,
        label: e.relation,
        animated: true,
        style: { stroke: '#64748b', strokeWidth: 2 },
      }));

      setNodes(flowNodes);
      setEdges(flowEdges);
    } catch (err) {
      console.error("Failed to load lineage graph", err);
    } finally {
      setLoading(false);
    }
  }, [executionId, setNodes, setEdges]);

  useEffect(() => {
    loadLineage();
  }, [loadLineage]);

  const onNodeClick = useCallback((event: any, node: any) => {
    setSelectedNode(node.data);
  }, []);

  return (
    <div className="h-[760px] w-full border border-gray-300 rounded-3xl overflow-hidden bg-gray-50 relative">
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-white/70 z-10">
          Loading Lineage Graph...
        </div>
      )}

      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        fitView
      >
        <Controls />
        <MiniMap />
        <Background variant="dots" gap={12} size={1} />
      </ReactFlow>

      {/* Side Panel */}
      {selectedNode && (
        <div className="absolute top-4 right-4 w-80 bg-white border border-gray-200 rounded-2xl shadow-xl p-5 max-h-[70vh] overflow-auto">
          <h3 className="font-semibold text-lg mb-3">{selectedNode.label}</h3>
          <pre className="text-xs bg-gray-100 p-3 rounded-xl overflow-auto">
            {JSON.stringify(selectedNode, null, 2)}
          </pre>
          <button
            onClick={() => setSelectedNode(null)}
            className="mt-4 text-sm text-gray-500 hover:text-gray-700"
          >
            Close
          </button>
        </div>
      )}
    </div>
  );
}
