import { useEffect, useState } from "react";
import { predictLoan, getMetadata } from "../api/riskApi";
import ResultCard from "../components/ResultCard";

const DEFAULT_FORM = {
  age:               35,
  annual_income:     85000,
  employment_length: 5,
  home_ownership:    "RENT",
  loan_amount:       15000,
  loan_term:         36,
  interest_rate:     12.5,
  purpose:           "debt_consolidation",
  fico_score:        720,
  dti:               18.5,
  delinq_2yrs:       0,
  open_acc:          8,
  revol_util:        35,
  total_acc:         20,
  revol_bal:         5000,
};

type FieldDef = {
  name: keyof typeof DEFAULT_FORM;
  label: string;
  hint?: string;
  type: "number" | "select";
  min?: number;
  max?: number;
  step?: number;
  metaKey?: string;
  staticOptions?: string[];
};

const SECTIONS: { title: string; fields: FieldDef[] }[] = [
  {
    title: "Applicant Profile",
    fields: [
      { name: "age",               label: "Age",                   hint: "years",  type: "number", min: 18, max: 100 },
      { name: "annual_income",     label: "Annual Income",         hint: "USD",    type: "number", min: 0 },
      { name: "employment_length", label: "Employment Length",     hint: "years",  type: "number", min: 0, max: 40 },
      { name: "home_ownership",    label: "Home Ownership",        type: "select", metaKey: "home_ownership",
        staticOptions: ["RENT", "OWN", "MORTGAGE", "OTHER"] },
    ],
  },
  {
    title: "Loan Details",
    fields: [
      { name: "loan_amount",   label: "Loan Amount",    hint: "USD",    type: "number", min: 0 },
      { name: "loan_term",     label: "Term",           hint: "months", type: "number", min: 12, max: 60 },
      { name: "interest_rate", label: "Interest Rate",  hint: "%",      type: "number", min: 0, max: 40, step: 0.1 },
      { name: "purpose",       label: "Loan Purpose",   type: "select", metaKey: "purpose",
        staticOptions: ["debt_consolidation","credit_card","home_improvement","major_purchase","medical","other"] },
    ],
  },
  {
    title: "Credit Profile",
    fields: [
      { name: "fico_score",  label: "FICO Score",       hint: "300–850", type: "number", min: 300, max: 850 },
      { name: "dti",         label: "Debt-to-Income",   hint: "%",       type: "number", min: 0, max: 100, step: 0.1 },
      { name: "delinq_2yrs", label: "Delinquencies",    hint: "last 2yr",type: "number", min: 0 },
      { name: "open_acc",    label: "Open Accounts",                     type: "number", min: 0 },
    ],
  },
  {
    title: "Revolving Credit",
    fields: [
      { name: "revol_util", label: "Revolving Utilization", hint: "%",   type: "number", min: 0, max: 100, step: 0.1 },
      { name: "revol_bal",  label: "Revolving Balance",     hint: "USD", type: "number", min: 0 },
      { name: "total_acc",  label: "Total Accounts",                     type: "number", min: 0 },
    ],
  },
];

export default function Assessment() {
  const [metadata, setMetadata] = useState<any>(null);
  const [result,   setResult]   = useState<any>(null);
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState<string | null>(null);
  const [formData, setFormData] = useState(DEFAULT_FORM);

  useEffect(() => {
    getMetadata()
      .then((res) => setMetadata(res.data))
      .catch(() => {/* silent – we fall back to staticOptions */});
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "number" ? parseFloat(value) || 0 : value,
    }));
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await predictLoan(formData);
      setResult(res.data);
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ??
        err?.message ??
        "Could not reach the API. Make sure the backend is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <div className="page-eyebrow">Risk Evaluation</div>
        <h1 className="page-title">Credit Assessment</h1>
        <p className="page-subtitle">Enter applicant details to generate an instant risk decision.</p>
      </div>

      {error && (
        <div className="error-banner">
          ⚠ {error}
        </div>
      )}

      <div className="assessment-layout">
        {/* Form */}
        <div className="form-panel">
          {SECTIONS.map((section) => (
            <div key={section.title} className="form-section">
              <div className="form-section-title">{section.title}</div>
              <div className="form-grid">
                {section.fields.map((field) => {
                  const options =
                    (field.metaKey && metadata?.[field.metaKey]) ??
                    field.staticOptions ??
                    [];

                  return (
                    <div key={field.name} className="form-field">
                      <label className="form-label" htmlFor={field.name}>
                        {field.label}
                        {field.hint && (
                          <span className="label-hint"> · {field.hint}</span>
                        )}
                      </label>

                      {field.type === "number" ? (
                        <input
                          id={field.name}
                          className="form-input"
                          type="number"
                          name={field.name}
                          value={formData[field.name] as number}
                          min={field.min}
                          max={field.max}
                          step={field.step ?? 1}
                          onChange={handleChange}
                        />
                      ) : (
                        <div className="form-select-wrap">
                          <select
                            id={field.name}
                            className="form-select"
                            name={field.name}
                            value={formData[field.name] as string}
                            onChange={handleChange}
                          >
                            {options.map((opt: string) => (
                              <option key={opt} value={opt}>
                                {opt.replace(/_/g, " ")}
                              </option>
                            ))}
                          </select>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}

          {/* Submit */}
          <div className="form-section">
            <button
              className="submit-btn"
              onClick={handleSubmit}
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="spinner" />
                  Analyzing…
                </>
              ) : (
                <>◎ Run Assessment</>
              )}
            </button>
          </div>
        </div>

        {/* Result */}
        <ResultCard result={result} />
      </div>
    </div>
  );
}
