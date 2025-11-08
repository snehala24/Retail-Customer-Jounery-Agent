import { NavLink } from "react-router-dom";
import { BarChart3, MessageSquare, TrendingUp, Sparkles } from "lucide-react";

function Sidebar() {
  return (
    <aside style={{
      width: '280px',
      height: '100vh',
      background: 'linear-gradient(180deg, #0f172a 0%, #1e293b 100%)',
      borderRight: '1px solid rgba(148, 163, 184, 0.1)',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
      position: 'relative',
      overflow: 'hidden',
      boxShadow: '4px 0 20px rgba(0, 0, 0, 0.3)'
    }}>
      {/* Background gradient effect */}
      <div style={{
        position: 'absolute',
        inset: 0,
        background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.08) 100%)',
        pointerEvents: 'none'
      }}></div>
      
      <div style={{ padding: '32px', position: 'relative', zIndex: 1 }}>
        {/* Logo Section */}
        <div style={{ marginBottom: '48px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '6px' }}>
            <div style={{
              background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
              padding: '10px',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 8px 20px rgba(99, 102, 241, 0.4)'
            }}>
              <Sparkles style={{ width: '24px', height: '24px', color: 'white' }} />
            </div>
            <div>
              <h1 style={{
                fontSize: '22px',
                fontWeight: '800',
                background: 'linear-gradient(135deg, #818cf8 0%, #a78bfa 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
                margin: 0,
                letterSpacing: '-0.5px'
              }}>
                Agentic AI
              </h1>
              <p style={{
                fontSize: '11px',
                color: '#64748b',
                margin: 0,
                fontWeight: '500',
                textTransform: 'uppercase',
                letterSpacing: '1px'
              }}>
                Sales Intelligence
              </p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <NavLink
            to="/"
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '14px 18px',
              borderRadius: '12px',
              textDecoration: 'none',
              fontSize: '15px',
              fontWeight: '600',
              transition: 'all 0.2s ease',
              position: 'relative',
              background: isActive 
                ? 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)' 
                : 'transparent',
              color: isActive ? 'white' : '#94a3b8',
              boxShadow: isActive ? '0 8px 20px rgba(99, 102, 241, 0.4)' : 'none'
            })}
            onMouseEnter={(e) => {
              if (!e.currentTarget.style.background.includes('gradient')) {
                e.currentTarget.style.background = 'rgba(99, 102, 241, 0.1)';
                e.currentTarget.style.color = '#cbd5e1';
              }
            }}
            onMouseLeave={(e) => {
              const isActive = e.currentTarget.style.background.includes('gradient');
              if (!isActive) {
                e.currentTarget.style.background = 'transparent';
                e.currentTarget.style.color = '#94a3b8';
              }
            }}
          >
            <BarChart3 style={{ width: '20px', height: '20px' }} />
            <span>Dashboard</span>
          </NavLink>

          <NavLink
            to="/chat"
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '14px 18px',
              borderRadius: '12px',
              textDecoration: 'none',
              fontSize: '15px',
              fontWeight: '600',
              transition: 'all 0.2s ease',
              background: isActive 
                ? 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)' 
                : 'transparent',
              color: isActive ? 'white' : '#94a3b8',
              boxShadow: isActive ? '0 8px 20px rgba(99, 102, 241, 0.4)' : 'none'
            })}
            onMouseEnter={(e) => {
              if (!e.currentTarget.style.background.includes('gradient')) {
                e.currentTarget.style.background = 'rgba(99, 102, 241, 0.1)';
                e.currentTarget.style.color = '#cbd5e1';
              }
            }}
            onMouseLeave={(e) => {
              const isActive = e.currentTarget.style.background.includes('gradient');
              if (!isActive) {
                e.currentTarget.style.background = 'transparent';
                e.currentTarget.style.color = '#94a3b8';
              }
            }}
          >
            <MessageSquare style={{ width: '20px', height: '20px' }} />
            <span>Chat</span>
          </NavLink>

          <NavLink
            to="/insights"
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '14px 18px',
              borderRadius: '12px',
              textDecoration: 'none',
              fontSize: '15px',
              fontWeight: '600',
              transition: 'all 0.2s ease',
              background: isActive 
                ? 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)' 
                : 'transparent',
              color: isActive ? 'white' : '#94a3b8',
              boxShadow: isActive ? '0 8px 20px rgba(99, 102, 241, 0.4)' : 'none'
            })}
            onMouseEnter={(e) => {
              if (!e.currentTarget.style.background.includes('gradient')) {
                e.currentTarget.style.background = 'rgba(99, 102, 241, 0.1)';
                e.currentTarget.style.color = '#cbd5e1';
              }
            }}
            onMouseLeave={(e) => {
              const isActive = e.currentTarget.style.background.includes('gradient');
              if (!isActive) {
                e.currentTarget.style.background = 'transparent';
                e.currentTarget.style.color = '#94a3b8';
              }
            }}
          >
            <TrendingUp style={{ width: '20px', height: '20px' }} />
            <span>Insights</span>
          </NavLink>
        </nav>
      </div>

      {/* Footer */}
      <footer style={{
        padding: '24px 32px',
        borderTop: '1px solid rgba(148, 163, 184, 0.1)',
        position: 'relative',
        zIndex: 1
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '12px',
          color: '#64748b'
        }}>
          <span>© 2025 Agentic AI</span>
          <span style={{
            padding: '4px 10px',
            background: 'rgba(99, 102, 241, 0.15)',
            borderRadius: '6px',
            color: '#818cf8',
            fontWeight: '600',
            border: '1px solid rgba(99, 102, 241, 0.2)'
          }}>
            v1.0
          </span>
        </div>
      </footer>
    </aside>
  );
}

export default Sidebar;