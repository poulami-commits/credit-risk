type Props = {
  result: any;
};

type Decision = "APPROVE" | "REVIEW" | "DECLINE";

function getScoreColor(score: number): string {
  if (score >= 700) return "#10b981";
  if (score >= 600) return "#f59e0b";
  return "#f43f5e";
}

function getTierLabel(tier: string): string {
  const map: Record<string, string> = {
    low:    "Low Risk",
    medium: "Medium Risk",
    high:   "High Risk",
  };
  return map[tier?.toLowerCase()] ?? tier;
}

export default function ResultCard({ result }: Props) {
  if (!result) {
    return (
      <div className="result-panel">
        <div className="panel-header">
          <div className="panel-title">Assessment Result</div>
        </div>
        <div className="result-empty">
          <div className="result-empty-icon">◎</div>
          <p className="result-empty-text">
            Fill in the applicant details and click <strong>Run Assessment</strong> to see the risk evaluation.
          </p>
        </div>
      </div>
    );
  }

  const decision: Decision = result.decision?.toUpperCase() as Decision;
  const prob = (result.default_probability ?? 0) * 100;
  const score = result.risk_score ?? 0;
  const scoreColor = getScoreColor(score);
  const scoreWidth = Math.min(100, Math.max(0, (score / 1000) * 100));
  const probWidth = Math.min(100, prob);

  const probColor = prob < 20
    ? "#10b981"
    : prob < 50
    ? "#f59e0b"
    : "#f43f5e";

  const decisionIcon: Record<Decision, string> = {
    APPROVE: "✓",
    REVIEW:  "◷",
    DECLINE: "✕",
  };

  return (
    <div className="result-panel">
      <div className="panel-header">
        <div className="panel-title">Assessment Result</div>
      </div>

      {/* Score hero */}
      <div className="result-header">
        <div className="result-decision-row">
          <span className={`result-decision-badge ${decision}`}>
            {decisionIcon[decision] ?? "?"} {decision}
          </span>
          <span style={{ fontSize: 11, color: "var(--text-muted)" }}>
            Risk evaluation
          </span>
        </div>

        <div className="result-score-row">
          <span className="result-score-value" style={{ color: scoreColor }}>
            {score}
          </span>
          <div className="result-score-meta">
            <div className="result-score-label">Risk Score</div>
            <div className="result-score-tier" style={{ color: scoreColor }}>
              {getTierLabel(result.risk_tier)}
            </div>
          </div>
        </div>

        <div className="score-gauge">
          <div className="score-gauge-track">
            <div
              className="score-gauge-fill"
              style={{ width: `${scoreWidth}%`, background: scoreColor }}
            />
          </div>
          <div className="score-gauge-ticks">
            <span className="score-gauge-tick">0</span>
            <span className="score-gauge-tick">250</span>
            <span className="score-gauge-tick">500</span>
            <span className="score-gauge-tick">750</span>
            <span className="score-gauge-tick">1000</span>
          </div>
        </div>
      </div>

      {/* Default probability */}
      <div className="prob-section" style={{ padding: "16px 20px", borderBottom: "1px solid var(--border)" }}>
        <div className="prob-label-row">
          <span className="prob-label">Default Probability</span>
          <span className="prob-value" style={{ color: probColor }}>{prob.toFixed(2)}%</span>
        </div>
        <div className="prob-track">
          <div
            className="prob-fill"
            style={{ width: `${probWidth}%`, background: probColor }}
          />
        </div>
      </div>

      {/* Metrics */}
      <div className="result-metrics">
        <div className="metric-row">
          <span className="metric-label">
            <span className="metric-icon">⬡</span>
            Risk Tier
          </span>
          <span className="metric-value">{getTierLabel(result.risk_tier)}</span>
        </div>

        <div className="metric-row">
          <span className="metric-label">
            <span className="metric-icon">◎</span>
            Decision
          </span>
          <span
            className="metric-value"
            style={{ color: decision === "APPROVE" ? "var(--emerald)" : decision === "DECLINE" ? "var(--rose)" : "var(--amber)" }}
          >
            {result.decision}
          </span>
        </div>

        {result.recommended_rate !== undefined && (
          <div className="metric-row">
            <span className="metric-label">
              <span className="metric-icon">%</span>
              Recommended Rate
            </span>
            <span className="metric-value">{Number(result.recommended_rate).toFixed(2)}%</span>
          </div>
        )}

        {result.max_loan_amount !== undefined && (
          <div className="metric-row">
            <span className="metric-label">
              <span className="metric-icon">$</span>
              Max Loan Amount
            </span>
            <span className="metric-value">
              ${Number(result.max_loan_amount).toLocaleString()}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
