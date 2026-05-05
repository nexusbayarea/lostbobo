import { useState, useRef, useEffect } from 'react';
import { Send, Bot, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
  confidence?: number;
}

export default function RAGChatbot() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: "Hello! Ask me anything about your simulations." }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await fetch('/api/v1/rag/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query: input,
          simulation_context: true 
        })
      });

      const data = await res.json();
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        confidence: data.confidence
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "Sorry, I couldn't process that request."
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <Card className="w-full h-[600px] flex flex-col">
      <CardHeader>
        <CardTitle className="flex items-center gap-3">
          <Bot className="w-6 h-6 text-cyan-500" />
          SimHPC RAG Assistant
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Ask about simulations, thermal events, compliance, or design insights
        </p>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col p-0">
        <ScrollArea className="flex-1 p-4">
          <div className="space-y-6">
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                  msg.role === 'user' 
                    ? 'bg-primary text-primary-foreground' 
                    : 'bg-muted'
                }`}>
                  <p>{msg.content}</p>
                  {msg.sources && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {msg.sources.map((src, idx) => (
                        <Badge key={idx} variant="outline" className="text-xs">
                          {src}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
          <div ref={scrollRef} />
        </ScrollArea>

        <div className="p-4 border-t">
          <div className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask about thermal runaway, Sobol indices..."
              disabled={isLoading}
            />
            <Button onClick={sendMessage} disabled={isLoading || !input.trim()}>
              {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}