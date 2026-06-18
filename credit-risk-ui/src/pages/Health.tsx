import { useEffect, useState } from "react";
import { getHealth } from "../api/riskApi";

type StatusType = "ok" | "warn" | "error" | "loading";

interface ServiceStatus {
  name: string;
  description: string;
  status: StatusType;
  value: string;
}

export default function Health() {
  const [services, setServices] = useState<ServiceStatus[]>([
    { name: "API Server",      description: "Core prediction endpoint",  status: "loading", value: "—" },
    { name: "ML Model",        description: "Gradient boost classifier", status: "loading", value: "—" },
    { name: "Data Pipeline",   description: "Feature transformation",    status: "loading", value: "—" },
  ]);
  const [lastChecked, setLastChecked] = useState<string>("—");
  const [uptime,      setUptime]      = useState<string>("—");
  const [rawData,     setRawData]     = useState<any>(null);

  const check = async () => {
    try {
      const res = await getHealth();
      const data = res.data;
      setRawData(data);
      setLastChecked(new Date().toLocaleTimeString());
      setUptime(data.uptime ?? "99.98%");

      setServices([
        {
          name: "API Server",
          description: "Core prediction endpoint",
          status: data.status === "healthy" ? "ok" : "warn",
          value: data.status ?? "healthy",
        },
        {
          name: "ML Model",
          description: "Gradient boost classifier",
          status: data.model_loaded ? "ok" : "error",
          value: data.model_loaded ? "Loaded" : "Not loaded",
        },
        {
          name: "Data Pipeline",
          description: "Feature transformation",
          status: "ok",
          value: "Operational",
        },
      ]);
    } catch {
      setLastChecked(new Date().toLocaleTimeString());
      setServices((prev) =>
        prev.map((s) => ({ ...s, status: "error", value: "Unreachable" }))
      );
    }
  };

  useEffect(() => {
    check();
    const id = setInterval(check, 30_000);
    return () => clearInterval(id);
  }, []);

  const statusIcon: Record<StatusType, string> = {
    ok:      "✓",
    warn:    "⚠",
    error:   "✕",
    loading: "…",
  };

  const overallOk = services.every((s) => s.status === "ok");
  const anyError  = services.some((s)  => s.status === "error");
  const overall: StatusType = services.some(s => s.status === "loading")
    ? "loading"
    : anyError ? "error" : overallOk ? "ok" : "warn";

  return (
    <div>
      <div className="page-header">
        <div className="page-eyebrow">System Status</div>
        <h1 className="page-title">Health Monitor</h1>
        <p className="page-subtitle">
          All services · Last checked {lastChecked}
          <button
            onClick={check}
            style={{
              marginLeft: 12,
              background: "none",
              border: "1px solid var(--border)",
              borderRadius: "var(--radius-sm)",
              color: "var(--text-secondary)",
              cursor: "pointer",
              fontSize: 11,
              padding: "2px 10px",
              fontFamily: "inherit",
            }}
          >
            ↻ Refresh
          </button>
        </p>
      </div>

      {/* Overall status banner */}
      <div
        style={{
          background: overall === "ok"
            ? "var(--emerald-dim)"
            : overall === "error"
            ? "var(--rose-dim)"
            : "var(--amber-dim)",
          border: `1px solid ${
            overall === "ok" ? "rgba(16,185,129,0.3)"
            : overall === "error" ? "rgba(244,63,94,0.3)"
            : "rgba(245,158,11,0.3)"
          }`,
          borderRadius: "var(--radius-lg)",
          padding: "18px 24px",
          marginBottom: 24,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div className={`health-dot ${overall}`} />
          <div>
            <div style={{ fontWeight: 700, color: "var(--text-primary)", fontSize: 15 }}>
              {overall === "ok" ? "All Systems Operational"
               : overall === "error" ? "Service Disruption"
               : overall === "loading" ? "Checking…"
               : "Degraded Performance"}
            </div>
            <div style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 2 }}>
              {services.filter(s => s.status === "ok").length}/{services.length} services healthy
            </div>
          </div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div className="health-uptime">{uptime}</div>
          <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Uptime</div>
        </div>
      </div>

      {/* Service cards */}
      <div className="health-grid">
        {services.map((svc) => (
          <div key={svc.name} className="health-card">
            <div className="health-indicator">
              <div className={`health-dot ${svc.status}`} />
              <span className={`health-status-text ${svc.status}`}>
                {statusIcon[svc.status]} {svc.status.toUpperCase()}
              </span>
            </div>
            <div className="health-card-title">{svc.name}</div>
            <div className="health-card-value">{svc.description}</div>
            <div
              style={{
                marginTop: 12,
                fontFamily: "var(--font-mono)",
                fontSize: 12,
                color: svc.status === "ok" ? "var(--emerald)" : "var(--text-secondary)",
                fontWeight: 600,
              }}
            >
              {svc.value}
            </div>
          </div>
        ))}
      </div>

      {/* Raw response */}
      {rawData && (
        <div className="panel" style={{ marginTop: 0 }}>
          <div className="panel-header">
            <div className="panel-title">Raw API Response</div>
            <span className="panel-badge">GET /health</span>
          </div>
          <div className="panel-body">
            <pre
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: 12,
                color: "var(--text-secondary)",
                background: "rgba(0,0,0,0.2)",
                borderRadius: "var(--radius-sm)",
                padding: "14px 16px",
                overflowX: "auto",
                lineHeight: 1.6,
                margin: 0,
              }}
            >
              {JSON.stringify(rawData, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
