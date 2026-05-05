import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useGraphRAGStream } from '@/hooks/useGraphRAGStream';
import { Play, RefreshCw, Brain } from 'lucide-react';

interface SwarmControlPanelProps {
  questionId: string;
  query: string;
  onSwarmComplete?: (forecast: any) => void;
}

export function SwarmControlPanel({ questionId, query, onSwarmComplete }: SwarmControlPanelProps) {
  const [isRunning, setIsRunning] = useState(false);
  const [forecast, setForecast] = useState<any>(null);
  const { streamQuery, isStreaming, updates, finalContext } = useGraphRAGStream();

  const runFullPipeline = async () => {
    setIsRunning(true);
    setForecast(null);

    await streamQuery(questionId, query);

    const res = await fetch('/api/swarm/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ questionId, query, graphContext: finalContext }),
    });

    const result = await res.json();
    setForecast(result);
    onSwarmComplete?.(result);
    setIsRunning(false);
  };

  return (
    <Card className="border-blue-500/30 bg-card">
      <CardHeader>
        <CardTitle className="flex items-center gap-3">
          <Brain className="h-6 w-6 text-blue-500" />
          Swarm Intelligence Forecast
          {(isStreaming || isRunning) && <Badge variant="secondary">LIVE</Badge>}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <Button
          onClick={runFullPipeline}
          disabled={isRunning || isStreaming}
          className="w-full h-12 text-lg font-semibold bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
        >
          {isRunning ? (
            <>Running Swarm <RefreshCw className="ml-2 h-5 w-5 animate-spin" /></>
          ) : (
            <>Run GraphRAG → Swarm Forecast <Play className="ml-2 h-5 w-5" /></>
          )}
        </Button>

        <ScrollArea className="h-80 rounded border p-4 text-sm">
          {updates.length > 0 && (
            <div className="space-y-3">
              {updates.map((u, i) => (
                <div key={i} className="border-l-2 border-blue-500 pl-3">
                  {u.type === 'start' && <div className="font-medium">🔍 Starting GraphRAG retrieval...</div>}
                  {u.type === 'chunk' && (
                    <div>
                      Chunk {i + 1}: {u.chunk?.text_preview.substring(0, 120)}...
                      <span className="text-blue-400 ml-2">score {u.chunk?.score}</span>
                    </div>
                  )}
                  {u.type === 'complete' && (
                    <div className="text-green-500 font-medium">
                      ✅ GraphRAG complete — {u.context?.total_chunks} chunks • {u.context?.retrieval_ms}ms
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {forecast && (
            <div className="mt-6 p-4 bg-green-950/50 rounded border border-green-500/30">
              <div className="text-xl font-bold text-green-400">
                Final Forecast: {(forecast.probability * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-green-500/80 mt-1">
                90% CI: [{(forecast.conf_lower * 100).toFixed(0)}% – {(forecast.conf_upper * 100).toFixed(0)}%]
              </div>
              <div className="text-xs mt-3 opacity-75">
                Consensus: {forecast.consensus_score.toFixed(2)} • Dissent: {forecast.dissent_flags.length}
              </div>
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
}