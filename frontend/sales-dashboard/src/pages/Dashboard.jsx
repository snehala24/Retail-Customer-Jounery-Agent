import { TrendingUp, DollarSign, Users, ArrowUpRight, Sparkles, ShoppingBag, Activity } from "lucide-react";

function Dashboard() {
  return (
    <div style={{ minHeight: '100vh', paddingBottom: '2rem' }}>
      {/* Welcome Header Section */}
      <div style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        borderRadius: '20px',
        padding: '40px',
        marginBottom: '32px',
        boxShadow: '0 20px 60px rgba(102, 126, 234, 0.3)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{
          position: 'absolute',
          top: '-50%',
          right: '-10%',
          width: '400px',
          height: '400px',
          background: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '50%',
          filter: 'blur(80px)'
        }}></div>
        <div style={{ position: 'relative', zIndex: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '20px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
              <div style={{
                background: 'rgba(255, 255, 255, 0.2)',
                backdropFilter: 'blur(10px)',
                padding: '12px',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Sparkles style={{ width: '24px', height: '24px', color: 'white' }} />
              </div>
              <h1 style={{
                fontSize: '42px',
                fontWeight: '800',
                color: 'white',
                margin: 0,
                letterSpacing: '-0.5px'
              }}>
                Welcome back, Sneha! 👋
              </h1>
            </div>
            <p style={{
              fontSize: '18px',
              color: 'rgba(255, 255, 255, 0.9)',
              margin: 0,
              marginLeft: '56px'
            }}>
              Here's your intelligent sales assistant overview.
            </p>
          </div>
          <div style={{
            background: 'rgba(255, 255, 255, 0.15)',
            backdropFilter: 'blur(10px)',
            padding: '12px 20px',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            border: '1px solid rgba(255, 255, 255, 0.2)'
          }}>
            <div style={{
              width: '8px',
              height: '8px',
              background: '#10b981',
              borderRadius: '50%',
              animation: 'pulse 2s infinite'
            }}></div>
            <span style={{ color: 'white', fontSize: '14px', fontWeight: '600' }}>Live</span>
          </div>
        </div>
      </div>

      {/* Metrics Cards Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '24px',
        marginBottom: '32px'
      }}>
        {/* Total Orders Card */}
        <div style={{
          background: 'linear-gradient(145deg, #1e293b 0%, #0f172a 100%)',
          borderRadius: '16px',
          padding: '28px',
          border: '1px solid rgba(148, 163, 184, 0.1)',
          boxShadow: '0 10px 40px rgba(0, 0, 0, 0.3)',
          transition: 'all 0.3s ease',
          cursor: 'pointer',
          position: 'relative',
          overflow: 'hidden'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'translateY(-8px)';
          e.currentTarget.style.boxShadow = '0 20px 60px rgba(99, 102, 241, 0.4)';
          e.currentTarget.style.borderColor = 'rgba(99, 102, 241, 0.5)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = '0 10px 40px rgba(0, 0, 0, 0.3)';
          e.currentTarget.style.borderColor = 'rgba(148, 163, 184, 0.1)';
        }}>
          <div style={{
            position: 'absolute',
            top: '-50px',
            right: '-50px',
            width: '150px',
            height: '150px',
            background: 'rgba(99, 102, 241, 0.1)',
            borderRadius: '50%',
            filter: 'blur(60px)'
          }}></div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px', position: 'relative', zIndex: 1 }}>
            <div style={{
              background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
              padding: '14px',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 8px 20px rgba(99, 102, 241, 0.3)'
            }}>
              <TrendingUp style={{ width: '24px', height: '24px', color: 'white' }} />
            </div>
            <ArrowUpRight style={{ width: '20px', height: '20px', color: '#10b981', opacity: 0.7 }} />
          </div>
          <div style={{ position: 'relative', zIndex: 1 }}>
            <h3 style={{
              fontSize: '13px',
              fontWeight: '600',
              color: '#94a3b8',
              textTransform: 'uppercase',
              letterSpacing: '1px',
              marginBottom: '12px'
            }}>
              Total Orders
            </h3>
            <p style={{
              fontSize: '48px',
              fontWeight: '800',
              background: 'linear-gradient(135deg, #818cf8 0%, #a78bfa 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              margin: '0 0 12px 0',
              lineHeight: '1'
            }}>
              1,245
            </p>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <TrendingUp style={{ width: '16px', height: '16px', color: '#10b981' }} />
              <span style={{ color: '#10b981', fontSize: '14px', fontWeight: '600' }}>
                +12.5% from last month
              </span>
            </div>
          </div>
        </div>

        {/* Revenue Card */}
        <div style={{
          background: 'linear-gradient(145deg, #1e293b 0%, #0f172a 100%)',
          borderRadius: '16px',
          padding: '28px',
          border: '1px solid rgba(148, 163, 184, 0.1)',
          boxShadow: '0 10px 40px rgba(0, 0, 0, 0.3)',
          transition: 'all 0.3s ease',
          cursor: 'pointer',
          position: 'relative',
          overflow: 'hidden'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'translateY(-8px)';
          e.currentTarget.style.boxShadow = '0 20px 60px rgba(139, 92, 246, 0.4)';
          e.currentTarget.style.borderColor = 'rgba(139, 92, 246, 0.5)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = '0 10px 40px rgba(0, 0, 0, 0.3)';
          e.currentTarget.style.borderColor = 'rgba(148, 163, 184, 0.1)';
        }}>
          <div style={{
            position: 'absolute',
            top: '-50px',
            right: '-50px',
            width: '150px',
            height: '150px',
            background: 'rgba(139, 92, 246, 0.1)',
            borderRadius: '50%',
            filter: 'blur(60px)'
          }}></div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px', position: 'relative', zIndex: 1 }}>
            <div style={{
              background: 'linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%)',
              padding: '14px',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 8px 20px rgba(139, 92, 246, 0.3)'
            }}>
              <DollarSign style={{ width: '24px', height: '24px', color: 'white' }} />
            </div>
            <ArrowUpRight style={{ width: '20px', height: '20px', color: '#10b981', opacity: 0.7 }} />
          </div>
          <div style={{ position: 'relative', zIndex: 1 }}>
            <h3 style={{
              fontSize: '13px',
              fontWeight: '600',
              color: '#94a3b8',
              textTransform: 'uppercase',
              letterSpacing: '1px',
              marginBottom: '12px'
            }}>
              Revenue
            </h3>
            <p style={{
              fontSize: '48px',
              fontWeight: '800',
              background: 'linear-gradient(135deg, #a78bfa 0%, #818cf8 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              margin: '0 0 12px 0',
              lineHeight: '1'
            }}>
              ₹4.7L
            </p>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <TrendingUp style={{ width: '16px', height: '16px', color: '#10b981' }} />
              <span style={{ color: '#10b981', fontSize: '14px', fontWeight: '600' }}>
                +8.3% from last month
              </span>
            </div>
          </div>
        </div>

        {/* Active Users Card */}
        <div style={{
          background: 'linear-gradient(145deg, #1e293b 0%, #0f172a 100%)',
          borderRadius: '16px',
          padding: '28px',
          border: '1px solid rgba(148, 163, 184, 0.1)',
          boxShadow: '0 10px 40px rgba(0, 0, 0, 0.3)',
          transition: 'all 0.3s ease',
          cursor: 'pointer',
          position: 'relative',
          overflow: 'hidden'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'translateY(-8px)';
          e.currentTarget.style.boxShadow = '0 20px 60px rgba(99, 102, 241, 0.4)';
          e.currentTarget.style.borderColor = 'rgba(99, 102, 241, 0.5)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = '0 10px 40px rgba(0, 0, 0, 0.3)';
          e.currentTarget.style.borderColor = 'rgba(148, 163, 184, 0.1)';
        }}>
          <div style={{
            position: 'absolute',
            top: '-50px',
            right: '-50px',
            width: '150px',
            height: '150px',
            background: 'rgba(99, 102, 241, 0.1)',
            borderRadius: '50%',
            filter: 'blur(60px)'
          }}></div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px', position: 'relative', zIndex: 1 }}>
            <div style={{
              background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
              padding: '14px',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 8px 20px rgba(99, 102, 241, 0.3)'
            }}>
              <Users style={{ width: '24px', height: '24px', color: 'white' }} />
            </div>
            <ArrowUpRight style={{ width: '20px', height: '20px', color: '#10b981', opacity: 0.7 }} />
          </div>
          <div style={{ position: 'relative', zIndex: 1 }}>
            <h3 style={{
              fontSize: '13px',
              fontWeight: '600',
              color: '#94a3b8',
              textTransform: 'uppercase',
              letterSpacing: '1px',
              marginBottom: '12px'
            }}>
              Active Users
            </h3>
            <p style={{
              fontSize: '48px',
              fontWeight: '800',
              background: 'linear-gradient(135deg, #818cf8 0%, #a78bfa 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              margin: '0 0 12px 0',
              lineHeight: '1'
            }}>
              318
            </p>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <TrendingUp style={{ width: '16px', height: '16px', color: '#10b981' }} />
              <span style={{ color: '#10b981', fontSize: '14px', fontWeight: '600' }}>
                +5.2% from last month
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Insights Card */}
      <div style={{
        background: 'linear-gradient(145deg, #1e293b 0%, #0f172a 100%)',
        borderRadius: '16px',
        padding: '32px',
        border: '1px solid rgba(148, 163, 184, 0.1)',
        boxShadow: '0 10px 40px rgba(0, 0, 0, 0.3)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{
          position: 'absolute',
          inset: 0,
          background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%)',
          pointerEvents: 'none'
        }}></div>
        <div style={{ position: 'relative', zIndex: 1, display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
          <div style={{
            background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
            padding: '10px',
            borderRadius: '10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 8px 20px rgba(99, 102, 241, 0.3)'
          }}>
            <Sparkles style={{ width: '20px', height: '20px', color: 'white' }} />
          </div>
          <h3 style={{
            fontSize: '24px',
            fontWeight: '700',
            background: 'linear-gradient(135deg, #818cf8 0%, #a78bfa 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            margin: 0
          }}>
            Quick Insights
          </h3>
        </div>
        <p style={{
          fontSize: '16px',
          color: '#cbd5e1',
          lineHeight: '1.7',
          margin: 0,
          maxWidth: '800px'
        }}>
          Track live orders, monitor conversions, and identify your top-selling products in real time. 
          More analytics and interactive charts coming soon!
        </p>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
}

export default Dashboard;