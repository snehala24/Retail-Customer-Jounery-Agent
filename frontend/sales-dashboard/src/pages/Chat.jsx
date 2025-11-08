import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Loader2, Sparkles } from "lucide-react";

function Chat() {
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Hello Sneha! How can I assist you today?" },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/v1/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          channel: "web",
          text: input,
          customer_id: "CUST-001",
        }),
      });

      if (!response.ok) {
        throw new Error("Backend returned error: " + response.status);
      }

      const data = await response.json();
      console.log("API response:", data);

      let reply = "";
    let toolMessages = "";
    let productCards = [];

    // ✅ 1. Use Gemini’s direct reply if available
    if (data.reply_text) {
    reply = data.reply_text;
    } else if (data.actions?.reply) {
    reply = data.actions.reply;
    }

    // ✅ 2. Collect tool messages and product cards
    if (data.actions?.tool_results?.length) {
    for (const t of data.actions.tool_results) {
        if (t.result?.message) {
        toolMessages += `\n🛠 ${t.tool}: ${t.result.message}`;
        } else if (t.error) {
        toolMessages += `\n⚠ ${t.tool} failed: ${t.error}`;
        }

        if (t.tool === "recommend" && t.result?.items?.length) {
        productCards = t.result.items.map((item) => ({
            name: item.name,
            price: item.price,
            image: item.image_url,
            sku: item.sku,
        }));
        }
    }
    }

    // ✅ 3. Append tool messages only if reply exists
    if (reply.trim()) {
    reply += toolMessages;
    } 
    // ✅ 4. Otherwise fallback to the default message
    else if (toolMessages.trim()) {
    reply = toolMessages;
    } 
    else {
    reply = "Sorry, I didn’t understand that.";
    }


      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: reply, products: productCards },
      ]);
    } catch (err) {
      console.error("Error:", err);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "⚠ Unable to connect to server." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
          <div style={{
            background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
            padding: '10px',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 8px 20px rgba(99, 102, 241, 0.4)'
          }}>
            <Sparkles style={{ width: '20px', height: '20px', color: 'white' }} />
          </div>
          <h2 style={{
            fontSize: '32px',
            fontWeight: '800',
            background: 'linear-gradient(135deg, #818cf8 0%, #a78bfa 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            margin: 0,
            letterSpacing: '-0.5px'
          }}>
            Chat Assistant
          </h2>
        </div>
        <p style={{ color: '#94a3b8', fontSize: '16px', margin: 0, marginLeft: '52px' }}>
          Get instant answers and product recommendations
        </p>
      </div>

      {/* Chat Container */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        height: 'calc(100vh - 280px)',
        minHeight: '600px',
        background: 'linear-gradient(145deg, #1e293b 0%, #0f172a 100%)',
        borderRadius: '20px',
        border: '1px solid rgba(148, 163, 184, 0.1)',
        boxShadow: '0 20px 60px rgba(0, 0, 0, 0.4)',
        overflow: 'hidden'
      }}>
        {/* Messages Area */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: '24px',
          display: 'flex',
          flexDirection: 'column',
          gap: '20px'
        }} className="custom-scrollbar">
          {messages.map((m, idx) => (
            <div
              key={idx}
              style={{
                display: 'flex',
                gap: '12px',
                justifyContent: m.role === "user" ? "flex-end" : "flex-start",
                alignItems: 'flex-start'
              }}
            >
              {m.role === "assistant" && (
                <div style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                  boxShadow: '0 8px 20px rgba(99, 102, 241, 0.4)'
                }}>
                  <Bot style={{ width: '20px', height: '20px', color: 'white' }} />
                </div>
              )}
              
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '8px',
                maxWidth: '70%',
                alignItems: m.role === "user" ? "flex-end" : "flex-start"
              }}>
                <div style={{
                  padding: '14px 18px',
                  borderRadius: m.role === "assistant" ? '16px 16px 16px 4px' : '16px 16px 4px 16px',
                  background: m.role === "assistant"
                    ? 'rgba(30, 41, 59, 0.8)'
                    : 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                  color: m.role === "assistant" ? '#e2e8f0' : 'white',
                  border: m.role === "assistant" ? '1px solid rgba(148, 163, 184, 0.1)' : 'none',
                  boxShadow: m.role === "user" ? '0 8px 20px rgba(99, 102, 241, 0.3)' : 'none',
                  whiteSpace: 'pre-line',
                  fontSize: '14px',
                  lineHeight: '1.6'
                }}>
                  {m.text}
                </div>

                {/* Product Cards */}
                {m.products && m.products.length > 0 && (
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                    gap: '12px',
                    width: '100%',
                    marginTop: '8px'
                  }}>
                    {m.products.map((prod) => (
                      <div
                        key={prod.sku}
                        style={{
                          background: 'rgba(30, 41, 59, 0.8)',
                          border: '1px solid rgba(148, 163, 184, 0.1)',
                          borderRadius: '12px',
                          padding: '16px',
                          transition: 'all 0.2s ease',
                          cursor: 'pointer'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.borderColor = 'rgba(99, 102, 241, 0.5)';
                          e.currentTarget.style.boxShadow = '0 8px 20px rgba(99, 102, 241, 0.2)';
                          e.currentTarget.style.transform = 'translateY(-2px)';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.borderColor = 'rgba(148, 163, 184, 0.1)';
                          e.currentTarget.style.boxShadow = 'none';
                          e.currentTarget.style.transform = 'translateY(0)';
                        }}
                      >
                        <div style={{
                          aspectRatio: '16/9',
                          background: 'rgba(15, 23, 42, 0.5)',
                          borderRadius: '8px',
                          marginBottom: '12px',
                          overflow: 'hidden',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}>
                          <img
                            src={prod.image || "https://via.placeholder.com/200"}
                            alt={prod.name}
                            style={{
                              width: '100%',
                              height: '100%',
                              objectFit: 'cover'
                            }}
                          />
                        </div>
                        <h3 style={{
                          color: '#818cf8',
                          fontWeight: '700',
                          fontSize: '14px',
                          marginBottom: '6px',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap'
                        }}>
                          {prod.name}
                        </h3>
                        <p style={{
                          color: '#a78bfa',
                          fontWeight: '800',
                          fontSize: '18px',
                          margin: 0
                        }}>
                          ₹{prod.price}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {m.role === "user" && (
                <div style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #818cf8 0%, #a78bfa 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0
                }}>
                  <User style={{ width: '20px', height: '20px', color: 'white' }} />
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-start' }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
                boxShadow: '0 8px 20px rgba(99, 102, 241, 0.4)'
              }}>
                <Bot style={{ width: '20px', height: '20px', color: 'white' }} />
              </div>
              <div style={{
                padding: '14px 18px',
                borderRadius: '16px 16px 16px 4px',
                background: 'rgba(30, 41, 59, 0.8)',
                border: '1px solid rgba(148, 163, 184, 0.1)',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                color: '#94a3b8'
              }}>
                <Loader2 style={{ width: '16px', height: '16px', animation: 'spin 1s linear infinite' }} />
                <span style={{ fontSize: '14px' }}>Agentic AI is thinking...</span>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div style={{
          padding: '20px 24px',
          borderTop: '1px solid rgba(148, 163, 184, 0.1)',
          background: 'rgba(15, 23, 42, 0.5)',
          display: 'flex',
          gap: '12px'
        }}>
          <input
            type="text"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
            style={{
              flex: 1,
              padding: '14px 18px',
              borderRadius: '12px',
              background: 'rgba(30, 41, 59, 0.8)',
              border: '1px solid rgba(148, 163, 184, 0.1)',
              color: 'white',
              fontSize: '15px',
              outline: 'none',
              transition: 'all 0.2s ease'
            }}
            onFocus={(e) => {
              e.currentTarget.style.borderColor = 'rgba(99, 102, 241, 0.5)';
              e.currentTarget.style.boxShadow = '0 0 0 3px rgba(99, 102, 241, 0.1)';
            }}
            onBlur={(e) => {
              e.currentTarget.style.borderColor = 'rgba(148, 163, 184, 0.1)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            style={{
              padding: '14px 24px',
              background: loading || !input.trim() 
                ? 'rgba(99, 102, 241, 0.3)' 
                : 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              fontSize: '15px',
              fontWeight: '700',
              cursor: loading || !input.trim() ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              boxShadow: loading || !input.trim() 
                ? 'none' 
                : '0 8px 20px rgba(99, 102, 241, 0.3)',
              transition: 'all 0.2s ease',
              opacity: loading || !input.trim() ? 0.5 : 1
            }}
            onMouseEnter={(e) => {
              if (!loading && input.trim()) {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 12px 30px rgba(99, 102, 241, 0.4)';
              }
            }}
            onMouseLeave={(e) => {
              if (!loading && input.trim()) {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 8px 20px rgba(99, 102, 241, 0.3)';
              }
            }}
          >
            {loading ? (
              <Loader2 style={{ width: '18px', height: '18px', animation: 'spin 1s linear infinite' }} />
            ) : (
              <Send style={{ width: '18px', height: '18px' }} />
            )}
            <span>Send</span>
          </button>
        </div>
      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default Chat;