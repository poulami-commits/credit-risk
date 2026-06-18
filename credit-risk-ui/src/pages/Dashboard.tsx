import { useState, useEffect } from "react";

const STATS = [
  { label: "Total Assessments", value: 128, change: "+12%", dir: "up" as const, icon: "◎", color: "cyan" as const },
  { label: "Approvals",         value: 74,  change: "+8%",  dir: "up" as const, icon: "✓", color: "emerald" as const },
  { label: "Manual Reviews",    value: 31,  change: "+3%",  dir: "up" as const, icon: "◷", color: "amber" as const },
  { label: "Declines",          value: 23,  change: "-5%",  dir: "down" as const, icon: "✕", color: "rose" as const },
];

const PURPOSES = [
  { label: "Debt Consolidation", pct: 38, color: "#22d3ee" },
  { label: "Home Improvement",   pct: 21, color: "#10b981" },
  { label: "Credit Card",        pct: 18, color: "#6366f1" },
  { label: "Major Purchase",     pct: 14, color: "#f59e0b" },
  { label: "Other",              pct: 9,  color: "#64748b" },
];

const RECENT = [
  { initials: "JD", name: "James Davis",    amount: "$18,500", score: 742, decision: "APPROVE" as const },
  { initials: "SM", name: "Sarah Mitchell", amount: "$9,200",  score: 651, decision: "REVIEW"  as const },
  { initials: "KL", name: "Kevin Li",       amount: "$32,000", score: 598, decision: "DECLINE" as const },
  { initials: "AB", name: "Amy Brown",      amount: "$6,000",  score: 788, decision: "APPROVE" as const },
  { initials: "RN", name: "Raj Nair",       amount: "$14,750", score: 705, decision: "APPROVE" as const },
];

type Decision = "APPROVE" | "REVIEW" | "DECLINE";

const decisionLabel: Record<Decision, string> = {
  APPROVE: "Approved",
  REVIEW:  "Review",
  DECLINE: "Declined",
};

// SVG donut
function DonutChart() {
  const data = [
    { label: "Approvals",  pct: 57.8, color: "#10b981" },
    { label: "Reviews",    pct: 24.2, color: "#f59e0b" },
    { label: "Declines",   pct: 18,   color: "#f43f5e" },
  ];

  const r = 56, cx = 64, cy = 64;
  const circumference = 2 * Math.PI * r;
  let offset = 0;

  const segments = data.map((d) => {
    const dashArray = (d.pct / 100) * circumference;
    const seg = { ...d, dashArray, dashOffset: -offset };
    offset += dashArray;
    return seg;
  });

  return (
    <div className="donut-wrap">
      <div className="donut-svg-wrap" style={{ width: 128, height: 128 }}>
        <svg viewBox="0 0 128 128" width={128} height={128}>
          <circle cx={cx} cy={cy} r={r} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth={14} />
          {segments.map((s) => (
            <circle
              key={s.label}
              cx={cx} cy={cy} r={r}
              fill="none"
              stroke={s.color}
              strokeWidth={14}
              strokeDasharray={`${s.dashArray} ${circumference}`}
              strokeDashoffset={s.dashOffset}
              strokeLinecap="butt"
              transform="rotate(-90 64 64)"
            />
          ))}
        </svg>
        <div className="donut-center">
          <span className="donut-center-value">128</span>
          <span className="donut-center-label">Total</span>
        </div>
      </div>
      <div className="donut-legend">
        {data.map((d) => (
          <div key={d.label} className="donut-legend-item">
            <div className="donut-legend-dot" style={{ background: d.color }} />
            <span className="donut-legend-label">{d.label}</span>
            <span className="donut-legend-pct">{d.pct.toFixed(1)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setMounted(true), 80);
    return () => clearTimeout(t);
  }, []);

  return (
    <div>
      {/* Header */}
      <div className="page-header">
        <div className="page-eyebrow">Overview</div>
        <h1 className="page-title">Risk Dashboard</h1>
        <p className="page-subtitle">Credit risk assessments · Last 30 days</p>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        {STATS.map((s) => (
          <div key={s.label} className={`stat-card ${s.color}`}>
            <div className={`stat-icon ${s.color}`}>{s.icon}</div>
            <div className="stat-value">{s.value}</div>
            <div className="stat-label">{s.label}</div>
            <div className={`stat-change ${s.dir}`}>
              {s.dir === "up" ? "↑" : "↓"} {s.change} vs last month
            </div>
          </div>
        ))}
      </div>

      {/* Panels */}
      <div className="dashboard-panels">
        {/* Left: purposes + recent */}
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          {/* Purpose breakdown */}
          <div className="panel">
            <div className="panel-header">
              <div>
                <div className="panel-title">Loan Purpose Breakdown</div>
                <div className="panel-subtitle">Distribution of 128 assessments</div>
              </div>
              <span className="panel-badge">This month</span>
            </div>
            <div className="panel-body">
              <div className="bar-chart">
                {PURPOSES.map((p) => (
                  <div key={p.label} className="bar-row">
                    <span className="bar-label">{p.label}</span>
                    <div className="bar-track">
                      <div
                        className="bar-fill"
                        style={{
                          width: mounted ? `${p.pct}%` : "0%",
                          background: p.color,
                        }}
                      />
                    </div>
                    <span className="bar-pct">{p.pct}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Recent decisions */}
          <div className="panel">
            <div className="panel-header">
              <div className="panel-title">Recent Decisions</div>
              <span className="panel-badge">5 latest</span>
            </div>
            <div className="panel-body">
              <div className="decision-list">
                {RECENT.map((r) => (
                  <div key={r.name} className="decision-row">
                    <div className="decision-avatar">{r.initials}</div>
                    <div className="decision-info">
                      <div className="decision-name">{r.name}</div>
                      <div className="decision-meta">{r.amount} · FICO {r.score}</div>
                    </div>
                    <span className={`decision-badge ${r.decision.toLowerCase()}`}>
                      {decisionLabel[r.decision]}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Right: donut */}
        <div className="panel">
          <div className="panel-header">
            <div>
              <div className="panel-title">Decision Split</div>
              <div className="panel-subtitle">Approval rate 57.8%</div>
            </div>
          </div>
          <div className="panel-body">
            <DonutChart />
          </div>
        </div>
      </div>
    </div>
  );
}
