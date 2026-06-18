import { useEffect, useState } from "react";
import { getModelInfo } from "../api/riskApi";

const PLACEHOLDER = {
  model_type: "Gradient Boosting Classifier",
  version: "2.1.4",
  trained_on: "2024-11-15",
  training_samples: 84_532,
  features_count: 15,
  accuracy: 0.876,
  roc_auc: 0.923,
  precision: 0.841,
  recall: 0.812,
  f1_score: 0.826,
  feature_importance: {
    fico_score: 0.24,
    dti: 0.18,
    annual_income: 0.15,
    loan_amount: 0.12,
    revol_util: 0.09,
    employment_length: 0.07,
    interest_rate: 0.06,
    delinq_2yrs: 0.05,
    open_acc: 0.04,
  },
};

const FEATURES = [
  "age","annual_income","employment_length","home_ownership",
  "loan_amount","loan_term","interest_rate","purpose",
  "fico_score","dti","delinq_2yrs","open_acc",
  "revol_util","total_acc","revol_bal",
];

const PERF_METRICS = [
  { key: "accuracy",  label: "Accuracy",   scale: 100 },
  { key: "roc_auc",   label: "ROC-AUC",    scale: 100 },
  { key: "precision", label: "Precision",  scale: 100 },
  { key: "recall",    label: "Recall",     scale: 100 },
  { key: "f1_score",  label: "F1 Score",   scale: 100 },
];

export default function ModelInfo() {
  const [info, setInfo] = useState<any>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    getModelInfo()
      .then((res) => setInfo(res.data))
      .catch(() => setInfo(PLACEHOLDER));

    const t = setTimeout(() => setMounted(true), 120);
    return () => clearTimeout(t);
  }, []);

  const data = info ?? PLACEHOLDER;

  const topFeatures = data.feature_importance
    ? Object.entries(data.feature_importance)
        .sort((a: any, b: any) => b[1] - a[1])
        .slice(0, 6)
    : [];

  return (
    <div>
      <div className="page-header">
        <div className="page-eyebrow">ML Model</div>
        <h1 className="page-title">Model Information</h1>
        <p className="page-subtitle">Gradient Boosting Classifier · Production v{data.version ?? "—"}</p>
      </div>

      <div className="model-layout">
        {/* Left column */}
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          {/* Metadata */}
          <div className="model-panel">
            <div className="model-panel-header">
              <span className="model-panel-title">Model Details</span>
              <span className="panel-badge">v{data.version ?? "—"}</span>
            </div>
            <div className="model-panel-body">
              {[
                ["Type",             data.model_type],
                ["Version",          data.version],
                ["Trained On",       data.trained_on],
                ["Training Samples", data.training_samples?.toLocaleString()],
                ["Feature Count",    data.features_count],
              ].map(([key, val]) => (
                <div key={key as string} className="info-row">
                  <span className="info-key">{key}</span>
                  <span className="info-val">{val ?? "—"}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Feature list */}
          <div className="model-panel">
            <div className="model-panel-header">
              <span className="model-panel-title">Input Features</span>
              <span className="panel-badge">{FEATURES.length} features</span>
            </div>
            <div className="model-panel-body">
              <div className="tag-list">
                {FEATURES.map((f) => (
                  <span key={f} className="feature-tag">{f}</span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Right column */}
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          {/* Performance */}
          <div className="model-panel">
            <div className="model-panel-header">
              <span className="model-panel-title">Performance Metrics</span>
              <span className="panel-badge">Test set</span>
            </div>
            <div className="model-panel-body">
              {PERF_METRICS.map(({ key, label, scale }) => {
                const raw = data[key];
                const val = raw !== undefined ? raw * scale : null;
                return (
                  <div key={key} className="perf-bar-row">
                    <div className="perf-bar-header">
                      <span className="perf-metric-name">{label}</span>
                      <span className="perf-metric-val">
                        {val !== null ? `${val.toFixed(1)}%` : "—"}
                      </span>
                    </div>
                    <div className="perf-track">
                      <div
                        className="perf-fill"
                        style={{ width: mounted && val !== null ? `${val}%` : "0%" }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Feature importance */}
          {topFeatures.length > 0 && (
            <div className="model-panel">
              <div className="model-panel-header">
                <span className="model-panel-title">Feature Importance</span>
                <span className="panel-badge">Top {topFeatures.length}</span>
              </div>
              <div className="model-panel-body">
                {topFeatures.map(([name, val]: any) => (
                  <div key={name} className="perf-bar-row">
                    <div className="perf-bar-header">
                      <span className="perf-metric-name" style={{ fontFamily: "var(--font-mono)", fontSize: 12 }}>
                        {name}
                      </span>
                      <span className="perf-metric-val">
                        {(val * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="perf-track">
                      <div
                        className="perf-fill"
                        style={{
                          width: mounted ? `${val * 100}%` : "0%",
                          background: "linear-gradient(90deg, #22d3ee, #10b981)",
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
