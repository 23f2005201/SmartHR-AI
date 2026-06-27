import React, { useState } from 'react';
import api from '../../services/api';

export default function AICopilotDrawer({ isOpen, onClose }) {
  const [messages, setMessages] = useState([
    { sender: 'ai', text: 'Greetings operator. I am your live SmartHR AI assistant. How can I assist you with workforce trends, anomaly scans, or calculations today?' }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [sending, setSending] = useState(false);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || sending) return;

    const userText = inputMessage;
    setMessages((prev) => [...prev, { sender: 'user', text: userText }]);
    setInputMessage('');
    setSending(true);

    try {
      const response = await api.post('/ai/copilot/chat', { message: userText });
      
      // 1. Render the natural text response string safely
      setMessages((prev) => [...prev, { sender: 'ai', text: response.data.reply }]);

      // 🚀 2. DYNAMIC CLIENT-SIDE ACTION INTERCEPTORS
      const { action_trigger, action_meta } = response.data;

      if (action_trigger === "DOWNLOAD" && action_meta?.url) {
        console.log("📥 Autonomous Agent Triggered: Compiling & Downloading Ledger...");
        // Re-route target location frame to auto-download the backend file stream
        window.location.href = `http://localhost:8000${action_meta.url}`;
      }

      if (action_trigger === "TERMINATE") {
        console.log("🔒 Autonomous Agent Triggered: Session Termination Protocol...");
        // Flush all authentication cache values immediately
        localStorage.clear();
        sessionStorage.clear();
        // Redirect the user to your landing login gateway interface
        window.location.href = '/login';
      }

    } catch (err) {
      setMessages((prev) => [...prev, { sender: 'ai', text: 'Error interacting with local AI agent pipeline. Confirm Ollama model instances are running.' }]);
    } finally {
      setSending(false);
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
          <div className="flex justify-start">
            <div className="bg-slate-800/50 text-slate-400 rounded-2xl rounded-tl-none px-4 py-2.5 border border-slate-800 animate-pulse text-xs font-bold uppercase tracking-wider">
              Thinking / Formulating Insights...
            </div>
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