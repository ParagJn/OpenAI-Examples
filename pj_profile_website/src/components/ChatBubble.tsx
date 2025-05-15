"use client";
import React, { useState, useRef } from "react";

function renderMessageContent(content: string) {
  // Render bullet points if the message contains lines starting with '- '
  if (content.includes('\n- ')) {
    const lines = content.split(/\r?\n/);
    const bullets = lines.filter(line => line.trim().startsWith('- '));
    const rest = lines.filter(line => !line.trim().startsWith('- '));
    return (
      <>
        {rest.map((line, i) => line && <div key={i}>{line}</div>)}
        {bullets.length > 0 && (
          <ul className="list-disc pl-6 my-2">
            {bullets.map((line, i) => (
              <li key={i}>{line.replace(/^-\s*/, "")}</li>
            ))}
          </ul>
        )}
      </>
    );
  }
  return content.split(/\r?\n/).map((line, i) => <div key={i}>{line}</div>);
}

const ChatBubble: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Hi! Ask me anything about this website." }
  ]);
  const [loading, setLoading] = useState(false);
  const chatRef = useRef<HTMLDivElement>(null);

  const handleSend = async () => {
    if (!input.trim()) return;
    setMessages((msgs) => [...msgs, { role: "user", content: input }]);
    setInput("");
    setLoading(true);
    try {
      const res = await fetch("/api/gpt4o-chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: [
            ...messages,
            { role: "user", content: input }
          ]
        })
      });
      const data = await res.json();
      setMessages((msgs) => [...msgs, { role: "assistant", content: data.answer }]);
    } catch (e) {
      setMessages((msgs) => [...msgs, { role: "assistant", content: "Sorry, something went wrong." }]);
    }
    setLoading(false);
    setTimeout(() => {
      if (chatRef.current) {
        chatRef.current.scrollTop = chatRef.current.scrollHeight;
      }
    }, 100);
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
      {open && (
        <div className="w-80 bg-white border border-slate-200 shadow-xl rounded-xl flex flex-col overflow-hidden mb-2 animate-fadeIn">
          <div className="bg-blue-600 text-white px-4 py-2 font-semibold">Ask Parag's AI Assistant</div>
          <div ref={chatRef} className="flex-1 max-h-72 overflow-y-auto px-4 py-2 space-y-2 bg-slate-50 text-sm">
            {messages.map((msg, i) => (
              <div key={i} className={msg.role === "user" ? "text-right" : "text-left"}>
                <span className={msg.role === "user" ? "inline-block bg-blue-100 text-blue-800 rounded-lg px-3 py-1 my-1" : "inline-block bg-slate-200 text-slate-800 rounded-lg px-3 py-1 my-1"}>
                  {msg.role === "assistant"
                    ? renderMessageContent(msg.content)
                    : msg.content}
                </span>
              </div>
            ))}
            {loading && <div className="text-slate-400">Thinking...</div>}
          </div>
          <div className="flex border-t border-slate-200">
            <input
              className="flex-1 px-3 py-2 outline-none text-slate-800"
              placeholder="Type your question..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleSend()}
              disabled={loading}
            />
            <button
              className="px-4 py-2 text-blue-600 font-bold disabled:opacity-50"
              onClick={handleSend}
              disabled={loading}
              aria-label="Send"
            >
              ➤
            </button>
          </div>
        </div>
      )}
      <button
        className="bg-blue-600 hover:bg-blue-700 text-white rounded-full w-14 h-14 flex items-center justify-center shadow-lg text-2xl focus:outline-none focus:ring-2 focus:ring-blue-400"
        onClick={() => setOpen((v) => !v)}
        aria-label="Open chat assistant"
      >
        <svg width="32" height="32" viewBox="0 0 32 32" fill="none"><circle cx="16" cy="16" r="16" fill="#fff"/><path d="M10 22v-2a4 4 0 014-4h4a4 4 0 014 4v2" stroke="#2563eb" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/><circle cx="12" cy="14" r="1" fill="#2563eb"/><circle cx="16" cy="14" r="1" fill="#2563eb"/><circle cx="20" cy="14" r="1" fill="#2563eb"/></svg>
      </button>
    </div>
  );
};

export default ChatBubble;
