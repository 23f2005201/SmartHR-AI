import React, { useState } from 'react';

export default function AICopilotDrawer({ isOpen, onClose }) {
  const [messages, setMessages] = useState([
    { sender: 'ai', text: 'Greetings operator. I am your live SmartHR AI assistant. How can I assist you with workforce trends, anomaly scans, or calculations today?' }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [sending, setSending] = useState(false);
  const [currentStepStatus, setCurrentStepStatus] = useState('');

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || sending) return;

    const userText = inputMessage;
    setMessages((prev) => [...prev, { sender: 'user', text: userText }]);
    setInputMessage('');
    setSending(true);
    setCurrentStepStatus('Initializing agent pipeline intent parser...');

    try {
      // ⚡ PERFORMANCE UPGRADE: Swapped out Axios wrapper for low-overhead vanilla fetch Event-Stream processing
      const response = await fetch('http://localhost:8000/api/v1/ai/copilot/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
        },
        body: JSON.stringify({ message: userText })
      });

      if (!response.body) throw new Error("Readable streaming pipeline absent from server context.");
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let completeBuffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        completeBuffer += decoder.decode(value, { stream: true });
        const textLines = completeBuffer.split('\n');
        
        // Preserve unfinished tail fragments for the next iteration step
        completeBuffer = textLines.pop() || '';

        for (const rawLine of textLines) {
          if (rawLine.startsWith('DATA:')) {
            const cleanJsonStr = rawLine.replace('DATA:', '').trim();
            try {
              const dataObj = json.parse(cleanJsonStr);

              // Capture intermediate multi-step sequence statuses
              if (dataObj.status_update) {
                setCurrentStepStatus(dataObj.status_update);
              }

              // Intercept the final consolidated summary payload
              if (dataObj.reply) {
                setMessages((prev) => [...prev, { sender: 'ai', text: dataObj.reply }]);
                
                // Trigger client action scripts
                const { action_trigger, action_meta } = dataObj;
                if (action_trigger === "DOWNLOAD" && action_meta?.url) {
                  window.location.href = `http://localhost:8000${action_meta.url}`;
                }
                if (action_trigger === "TERMINATE") {
                  localStorage.clear();
                  sessionStorage.clear();
                  window.location.href = '/login';
                }
              }
            } catch (jsonErr) {
              // Gracefully pass parsing alignment exceptions
            }
          }
        }
      }

    } catch (err) {
      setMessages((prev) => [...prev, { sender: 'ai', text: 'Error interacting with local AI agent pipeline. Confirm Ollama model instances are running.' }]);
    } finally {
      setSending(false);
      setCurrentStepStatus('');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-96 bg-slate-900 border-l border-slate-800 shadow-2xl z-50 flex flex-col animate-slideLeft">
      {/* Drawer Header */}
      <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-950/40">
        <div className="flex items-center space-x-2">
          <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse"></span>
          <h3 className="font-bold text-white text-md">SmartHR AI Copilot</h3>
        </div>
        <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors text-sm font-semibold">✕ Close</button>
      </div>

      {/* Messages Window View Canvas */}
      <div className="flex-1 p-4 overflow-y-auto space-y-4 text-sm scrollbar-thin">
        {messages.map((msg, index) => (
          <div key={index} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] rounded-2xl px-4 py-2.5 leading-relaxed font-medium ${
              msg.sender === 'user' ? 'bg-white text-slate-900 rounded-tr-none' : 'bg-slate-800 text-slate-100 rounded-tl-none border border-slate-700/40'
            }`}>
              {msg.text}
            </div>
          </div>
        ))}
        {sending && (
          <div className="flex flex-col space-y-2 items-start justify-start">
            <div className="bg-slate-800/50 text-slate-400 rounded-2xl rounded-tl-none px-4 py-2.5 border border-slate-800 animate-pulse text-xs font-bold uppercase tracking-wider">
              Thinking / Formulating Insights...
            </div>
            {currentStepStatus && (
              <span className="text-[11px] font-semibold text-blue-400 tracking-wide bg-blue-500/10 px-2.5 py-1 rounded-full border border-blue-500/10 transition-all">
                ⚙️ {currentStepStatus}
              </span>
            )}
          </div>
        )}
      </div>

      {/* Input Execution Box Form */}
      <form onSubmit={handleSendMessage} className="p-4 border-t border-slate-800 bg-slate-950/20">
        <div className="flex space-x-2">
          <input
            type="text"
            className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-slate-700"
            placeholder="Ask anything about HR systems..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
          />
          <button type="submit" disabled={sending} className="bg-white text-slate-900 font-bold px-4 rounded-xl text-sm hover:bg-slate-100 transition-colors disabled:opacity-40">
            Send
          </button>
        </div>
      </form>
    </div>
  );
}