import ReactFlow, { Background, Controls, MiniMap } from 'reactflow';
import 'reactflow/dist/style.css';
import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';

export default function WorldStateGraph() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  const { data } = useQuery({
    queryKey: ['entity-graph'],
    queryFn: () => fetch('/api/v1/graph/entity-graph').then(r => r.json()),
    refetchInterval: 8000, // live updates
  });

  useEffect(() => {
    if (data && data.nodes) {
      // Transform with temporal decay visualization (node opacity = 1 - uncertainty)
      const vizNodes = data.nodes.map((n: any) => ({
        id: n.entity_id,
        position: { x: Math.random() * 800, y: Math.random() * 600 }, // force layout later
        data: { label: n.name, uncertainty: n.uncertainty, regime: n.regime },
        style: { opacity: 1 - (n.uncertainty || 0) },
      }));
      setNodes(vizNodes);
      setEdges(data.edges || []);
    }
  }, [data]);

  return (
    <div className="h-[700px] border rounded-xl overflow-hidden relative">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        nodesDraggable={true}
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
      {/* Regime + Entropy Legend */}
      <div className="absolute top-4 right-4 bg-black/80 p-4 rounded text-white text-sm">
        Regime: <span className="font-bold">{data?.regime || 'N/A'}</span><br/>
        Entropy: {(data?.entropy || 0).toFixed(3)}
      </div>
    </div>
  );
}
