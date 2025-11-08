import {
  TrendingUp,
  DollarSign,
  Users,
  ShoppingCart,
  BarChart3,
  Activity,
  ArrowUpRight,
  Sparkles,
} from "lucide-react";

function Insights() {
  const metrics = [
    {
      title: "Total Orders",
      value: "1,245",
      change: "+12.5%",
      icon: ShoppingCart,
      color: "primary",
    },
    {
      title: "Revenue",
      value: "₹4.7L",
      change: "+8.3%",
      icon: DollarSign,
      color: "accent",
    },
    {
      title: "Active Users",
      value: "318",
      change: "+5.2%",
      icon: Users,
      color: "primary",
    },
    {
      title: "Conversion Rate",
      value: "24.8%",
      change: "+2.1%",
      icon: TrendingUp,
      color: "accent",
    },
    {
      title: "Avg Order Value",
      value: "₹3,847",
      change: "+6.7%",
      icon: BarChart3,
      color: "primary",
    },
    {
      title: "Active Sessions",
      value: "1,892",
      change: "+15.3%",
      icon: Activity,
      color: "accent",
    },
  ];

  return (
    <div style={{ minHeight: "100vh", paddingBottom: "2rem" }}>
      {/* Header */}
      <div style={{ marginBottom: "32px" }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "12px",
            marginBottom: "8px",
          }}
        >
          <div
            style={{
              background: "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
              padding: "10px",
              borderRadius: "12px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 8px 20px rgba(99, 102, 241, 0.4)",
            }}
          >
            <Sparkles style={{ width: "20px", height: "20px", color: "white" }} />
          </div>
          <h2
            style={{
              fontSize: "32px",
              fontWeight: "800",
              background: "linear-gradient(135deg, #818cf8 0%, #a78bfa 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              backgroundClip: "text",
              margin: 0,
              letterSpacing: "-0.5px",
            }}
          >
            Sales Insights
          </h2>
        </div>
        <p
          style={{
            color: "#94a3b8",
            fontSize: "16px",
            margin: 0,
            marginLeft: "52px",
            maxWidth: "600px",
          }}
        >
          Here you'll soon see analytics from your backend — like top products,
          order trends, and customer engagement data.
        </p>
      </div>

      {/* Metrics Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
          gap: "24px",
          marginBottom: "32px",
        }}
      >
        {metrics.map((metric, idx) => {
          const Icon = metric.icon;
          const isPrimary = metric.color === "primary";
          const gradientFrom = isPrimary ? "#6366f1" : "#8b5cf6";
          const gradientTo = isPrimary ? "#8b5cf6" : "#a78bfa";
          const bgGlow = isPrimary
            ? "rgba(99, 102, 241, 0.1)"
            : "rgba(139, 92, 246, 0.1)";

          return (
            <div
              key={idx}
              style={{
                background: "linear-gradient(145deg, #1e293b 0%, #0f172a 100%)",
                borderRadius: "16px",
                padding: "28px",
                border: "1px solid rgba(148, 163, 184, 0.1)",
                boxShadow: "0 10px 40px rgba(0, 0, 0, 0.3)",
                transition: "all 0.3s ease",
                cursor: "pointer",
                position: "relative",
                overflow: "hidden",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = "translateY(-8px)";
                e.currentTarget.style.boxShadow = `0 20px 60px ${
                  isPrimary
                    ? "rgba(99, 102, 241, 0.4)"
                    : "rgba(139, 92, 246, 0.4)"
                }`;
                e.currentTarget.style.borderColor = `rgba(${
                  isPrimary ? "99, 102, 241" : "139, 92, 246"
                }, 0.5)`;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.boxShadow =
                  "0 10px 40px rgba(0, 0, 0, 0.3)";
                e.currentTarget.style.borderColor =
                  "rgba(148, 163, 184, 0.1)";
              }}
            >
              <div
                style={{
                  position: "absolute",
                  top: "-50px",
                  right: "-50px",
                  width: "150px",
                  height: "150px",
                  background: bgGlow,
                  borderRadius: "50%",
                  filter: "blur(60px)",
                }}
              ></div>

              <div style={{ position: "relative", zIndex: 1 }}>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                    marginBottom: "20px",
                  }}
                >
                  <div
                    style={{
                      background: `linear-gradient(135deg, ${gradientFrom} 0%, ${gradientTo} 100%)`,
                      padding: "14px",
                      borderRadius: "12px",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      boxShadow: `0 8px 20px ${
                        isPrimary
                          ? "rgba(99, 102, 241, 0.3)"
                          : "rgba(139, 92, 246, 0.3)"
                      }`,
                    }}
                  >
                    <Icon style={{ width: "24px", height: "24px", color: "white" }} />
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                    <ArrowUpRight
                      style={{ width: "16px", height: "16px", color: "#10b981" }}
                    />
                    <span
                      style={{
                        color: "#10b981",
                        fontSize: "14px",
                        fontWeight: "700",
                      }}
                    >
                      {metric.change}
                    </span>
                  </div>
                </div>

                <h3
                  style={{
                    fontSize: "13px",
                    fontWeight: "600",
                    color: "#94a3b8",
                    textTransform: "uppercase",
                    letterSpacing: "1px",
                    marginBottom: "12px",
                  }}
                >
                  {metric.title}
                </h3>

                <p
                  style={{
                    fontSize: "42px",
                    fontWeight: "800",
                    background: `linear-gradient(135deg, ${
                      isPrimary ? "#818cf8" : "#a78bfa"
                    } 0%, ${
                      isPrimary ? "#a78bfa" : "#818cf8"
                    } 100%)`,
                    WebkitBackgroundClip: "text",
                    WebkitTextFillColor: "transparent",
                    backgroundClip: "text",
                    margin: 0,
                    lineHeight: "1",
                  }}
                >
                  {metric.value}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Additional Info Section */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))",
          gap: "24px",
        }}
      >
        {[BarChart3, Activity].map((Icon, i) => (
          <div
            key={i}
            style={{
              background: "linear-gradient(145deg, #1e293b 0%, #0f172a 100%)",
              borderRadius: "16px",
              padding: "32px",
              border: "1px solid rgba(148, 163, 184, 0.1)",
              boxShadow: "0 10px 40px rgba(0, 0, 0, 0.3)",
              position: "relative",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                position: "absolute",
                inset: 0,
                background:
                  "linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%)",
                pointerEvents: "none",
              }}
            ></div>

            <div
              style={{
                position: "relative",
                zIndex: 1,
                display: "flex",
                alignItems: "center",
                gap: "12px",
                marginBottom: "20px",
              }}
            >
              <div
                style={{
                  background: "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
                  padding: "10px",
                  borderRadius: "10px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  boxShadow: "0 8px 20px rgba(99, 102, 241, 0.3)",
                }}
              >
                <Icon style={{ width: "20px", height: "20px", color: "white" }} />
              </div>

              <h3
                style={{
                  fontSize: "22px",
                  fontWeight: "700",
                  background:
                    "linear-gradient(135deg, #818cf8 0%, #a78bfa 100%)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                  backgroundClip: "text",
                  margin: 0,
                }}
              >
                {i === 0 ? "Performance Overview" : "Real-time Analytics"}
              </h3>
            </div>

            <p
              style={{
                fontSize: "16px",
                color: "#cbd5e1",
                lineHeight: "1.7",
                margin: 0,
              }}
            >
              {i === 0
                ? "Your sales performance is showing strong growth trends across all key metrics. The conversion rate improvement indicates effective optimization strategies."
                : "Monitor live order trends, customer engagement patterns, and product performance in real-time. Advanced analytics and interactive charts coming soon!"}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Insights;
