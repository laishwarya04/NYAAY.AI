// App.jsx
import React, { useState, useEffect } from "react";

const API_BASE = "http://127.0.0.1:8000";

const styles = {
  page: {
    fontFamily:
      "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    background:
      "radial-gradient(circle at top, #0f172a 0, #020617 45%, #000 100%)",
    margin: 0,
    padding: 0,
    minHeight: "100vh",
    width: "100vw",
    color: "#e5e7eb",
    boxSizing: "border-box",
    overflowX: "hidden",
  },
  container: {
    width: "100%",
    maxWidth: "100%",
    padding: "16px",
    boxSizing: "border-box",
  },
  card: {
    width: "100%",
    maxWidth: "100%",
    background: "rgba(15, 23, 42, 0.96)",
    backdropFilter: "blur(18px)",
    borderRadius: "18px",
    border: "1px solid rgba(148, 163, 184, 0.35)",
    padding: "20px 18px",
    boxShadow:
      "0 24px 60px rgba(15,23,42,0.75), 0 0 0 1px rgba(15,23,42,0.6)",
    boxSizing: "border-box",
  },
  h1: {
    fontSize: "28px",
    fontWeight: 700,
    textAlign: "center",
    marginBottom: "4px",
    color: "#60a5fa",
    letterSpacing: "0.03em",
  },
  subtitle: {
    textAlign: "center",
    color: "#9ca3af",
    marginBottom: "18px",
    fontSize: "13px",
  },
  pillRow: {
    display: "flex",
    justifyContent: "center",
    gap: "8px",
    marginBottom: "16px",
    flexWrap: "wrap",
  },
  pill: {
    fontSize: "10px",
    textTransform: "uppercase",
    letterSpacing: "0.12em",
    padding: "3px 9px",
    borderRadius: "999px",
    background: "rgba(15,23,42,0.9)",
    border: "1px solid rgba(96,165,250,0.5)",
    color: "#bfdbfe",
  },
  mainGridBase: {
    display: "grid",
    gap: "16px",
    alignItems: "flex-start",
    width: "100%",
    boxSizing: "border-box",
  },
  leftColumn: {
    display: "flex",
    flexDirection: "column",
    gap: "10px",
  },
  rightColumn: {
    display: "flex",
    flexDirection: "column",
    gap: "10px",
  },
  label: {
    fontSize: "12px",
    color: "#9ca3af",
    marginBottom: "4px",
  },
  textarea: {
    width: "100%",
    minHeight: "120px",
    padding: "10px 12px",
    borderRadius: "10px",
    border: "1px solid rgba(75,85,99,0.8)",
    background: "rgba(15,23,42,0.9)",
    color: "#e5e7eb",
    fontSize: "14px",
    resize: "vertical",
    boxSizing: "border-box",
    outline: "none",
  },
  input: {
    width: "100%",
    padding: "8px 10px",
    borderRadius: "8px",
    border: "1px solid rgba(55,65,81,0.9)",
    background: "rgba(15,23,42,0.9)",
    color: "#e5e7eb",
    fontSize: "13px",
    boxSizing: "border-box",
    outline: "none",
  },
  buttonPrimary: {
    background:
      "linear-gradient(135deg, #2563eb 0%, #1d4ed8 35%, #4f46e5 100%)",
    color: "#f9fafb",
    padding: "9px 16px",
    border: "none",
    borderRadius: "999px",
    fontSize: "13px",
    fontWeight: 600,
    cursor: "pointer",
    display: "inline-flex",
    alignItems: "center",
    gap: "6px",
    marginTop: "10px",
  },
  buttonSecondary: {
    background: "rgba(15,23,42,0.7)",
    color: "#e5e7eb",
    padding: "8px 14px",
    borderRadius: "999px",
    border: "1px solid rgba(55,65,81,0.9)",
    fontSize: "13px",
    cursor: "pointer",
    display: "inline-flex",
    alignItems: "center",
    gap: "6px",
    marginTop: "8px",
  },
  buttonDisabled: {
    opacity: 0.6,
    cursor: "not-allowed",
  },
  smallHint: {
    fontSize: "11px",
    color: "#9ca3af",
    marginTop: "4px",
  },
  section: {
    marginTop: "6px",
    padding: "12px",
    background:
      "radial-gradient(circle at top, rgba(30,64,175,0.3), rgba(15,23,42,0.95))",
    borderRadius: "14px",
    border: "1px solid rgba(55,65,81,0.9)",
  },
  sectionTitle: {
    fontSize: "11px",
    textTransform: "uppercase",
    letterSpacing: "0.16em",
    color: "#9ca3af",
    marginBottom: "4px",
  },
  sectionHeading: {
    fontSize: "14px",
    fontWeight: 600,
    color: "#e5e7eb",
    marginBottom: "6px",
  },
  tag: {
    display: "inline-block",
    padding: "3px 8px",
    borderRadius: "999px",
    background: "rgba(15,23,42,0.9)",
    border: "1px solid rgba(75,85,99,0.8)",
    color: "#e5e7eb",
    fontSize: "11px",
    marginRight: "6px",
    marginBottom: "4px",
  },
  ipcCard: {
    background: "rgba(15,23,42,0.92)",
    borderRadius: "10px",
    padding: "10px",
    border: "1px solid rgba(37,99,235,0.6)",
    marginTop: "8px",
    fontSize: "13px",
  },
  pre: {
    whiteSpace: "pre-wrap",
    margin: 0,
    fontFamily:
      "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace",
    fontSize: "12px",
    color: "#e5e7eb",
  },
  actionsList: {
    paddingLeft: "18px",
    fontSize: "13px",
    color: "#e5e7eb",
    margin: 0,
  },
  error: {
    marginTop: "8px",
    padding: "6px 8px",
    borderRadius: "8px",
    background: "rgba(153,27,27,0.15)",
    border: "1px solid rgba(248,113,113,0.4)",
    color: "#fecaca",
    fontSize: "12px",
  },
  disclaimer: {
    fontSize: "11px",
    color: "#9ca3af",
  },
};

function App() {
  const [legalQuery, setLegalQuery] = useState("");
  const [file, setFile] = useState(null);
  const [ocrText, setOcrText] = useState("");
  const [loadingOcr, setLoadingOcr] = useState(false);
  const [loadingAnalyze, setLoadingAnalyze] = useState(false);
  const [fillingTemplate, setFillingTemplate] = useState(false);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const [isNarrow, setIsNarrow] = useState(false);

  useEffect(() => {
    const handleResize = () => {
      setIsNarrow(window.innerWidth < 960);
    };
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const [templateForm, setTemplateForm] = useState({
    full_name: "",
    address: "",
    opposite_party_name: "",
    opposite_party_address: "",
    date: "",
    mobile_number: "",
    email_id: "",
    signature: "",
  });

  const handleFileChange = (e) => {
    setFile(e.target.files[0] || null);
  };

  const uploadDocument = async () => {
    setError("");
    if (!file) {
      setError("Please select a file first.");
      return;
    }

    try {
      setLoadingOcr(true);
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`${API_BASE}/api/ocr`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "OCR failed");
      }

      const data = await res.json();
      setOcrText(data.document_text || "");
    } catch (err) {
      setError(err.message || "Error uploading document");
    } finally {
      setLoadingOcr(false);
    }
  };

  const getAnalysis = async () => {
    setError("");
    if (!legalQuery && !ocrText) {
      setError("Please enter a legal issue or extract text from a document.");
      return;
    }

    try {
      setLoadingAnalyze(true);
      const body = {
        user_query: legalQuery || "",
        document_text: ocrText.trim() !== "" ? ocrText : null,
      };

      const res = await fetch(`${API_BASE}/api/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Analysis failed");
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err.message || "Error calling analysis API");
    } finally {
      setLoadingAnalyze(false);
    }
  };

  const handleTemplateChange = (field, value) => {
    setTemplateForm((prev) => ({ ...prev, [field]: value }));
  };

  const fillTemplate = async () => {
    if (!result) {
      setError("Please get guidance first.");
      return;
    }
    setError("");
    setFillingTemplate(true);
    try {
      const res = await fetch(`${API_BASE}/api/fill-template`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          template_text: result.complaint_template,
          full_name: templateForm.full_name,
          address: templateForm.address,
          opposite_party_name: templateForm.opposite_party_name,
          opposite_party_address: templateForm.opposite_party_address,
          date: templateForm.date,
          mobile_number: templateForm.mobile_number,
          email_id: templateForm.email_id,
          signature: templateForm.signature,
        }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Failed to fill template");
      }

      const data = await res.json();
      setResult((prev) => ({
        ...prev,
        complaint_template: data.filled_template,
      }));
    } catch (err) {
      setError(err.message || "Error filling template");
    } finally {
      setFillingTemplate(false);
    }
  };

  const downloadPdf = async () => {
    if (!result) {
      setError("Generate a template first.");
      return;
    }

    setError("");
    setDownloadingPdf(true);
    try {
      const res = await fetch(`${API_BASE}/api/download-pdf`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          issue_summary: result.issue_summary,
          complaint_template: result.complaint_template,
        }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Failed to download PDF");
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "nyayai_complaint.pdf";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message || "Error downloading PDF");
    } finally {
      setDownloadingPdf(false);
    }
  };

  const mainGridStyle = {
  display: "flex",
  flexDirection: "column",
  gap: "16px",
  width: "100%",
};

  return (
    <div style={styles.page}>
      <div style={styles.container}>
        <div style={styles.card}>
          <h1 style={styles.h1}>NYAAYA.AI</h1>
          <p style={styles.subtitle}>
            AI-powered legal information &amp; document understanding for Indian
            law.
          </p>

          <div style={styles.pillRow}>
            <span style={styles.pill}>Tenancy</span>
            <span style={styles.pill}>Consumer</span>
            <span style={styles.pill}>Cybercrime</span>
            <span style={styles.pill}>Employment</span>
            <span style={styles.pill}>IPC &amp; Rights</span>
          </div>

          <div style={mainGridStyle}>
            {/* LEFT COLUMN */}
            
              <div>
                <p style={styles.label}>Describe your legal issue</p>
                <textarea
                  style={styles.textarea}
                  placeholder="Example: My landlord is refusing to return my security deposit even after I vacated the flat..."
                  value={legalQuery}
                  onChange={(e) => setLegalQuery(e.target.value)}
                />
                <button
                  style={{
                    ...styles.buttonPrimary,
                    ...(loadingAnalyze ? styles.buttonDisabled : {}),
                  }}
                  onClick={getAnalysis}
                  disabled={loadingAnalyze}
                >
                  {loadingAnalyze ? "Getting guidance..." : "Get Guidance"}
                </button>
              </div>

              <div>
                <p style={{ ...styles.label, marginTop: "8px" }}>
                  Or upload a document (agreement, notice, FIR, bill etc.) for
                  OCR
                </p>
                <input
                  type="file"
                  onChange={handleFileChange}
                  style={{ fontSize: "12px", color: "#e5e7eb" }}
                />
                <br />
                <button
                  style={{
                    ...styles.buttonSecondary,
                    ...(loadingOcr ? styles.buttonDisabled : {}),
                  }}
                  onClick={uploadDocument}
                  disabled={loadingOcr}
                >
                  {loadingOcr ? "Extracting text..." : "Extract Text with OCR"}
                </button>
                <div style={styles.smallHint}>
                  Best results with clear JPG/PNG scans of typed documents.
                </div>
              </div>

              {ocrText && (
                <div style={styles.section}>
                  <div style={styles.sectionTitle}>OCR EXTRACTED TEXT</div>
                  <pre style={styles.pre}>{ocrText}</pre>
                </div>
              )}

              {error && !result && (
                <div style={styles.error}>⚠ {error}</div>
              )}
          

            
              {result ? (
                <>
                  <div style={styles.section}>
                    <div style={styles.sectionTitle}>ISSUE SUMMARY</div>
                    <div style={styles.sectionHeading}>
                      What this seems about
                    </div>
                    <p style={{ fontSize: "13px", color: "#e5e7eb" }}>
                      {result.issue_summary}
                    </p>
                  </div>

                  <div style={styles.section}>
                    <div style={styles.sectionTitle}>CLASSIFICATION</div>
                    <p style={{ fontSize: "13px" }}>
                      <b>Category:</b> {result.classification?.category}
                    </p>
                    <p style={{ fontSize: "13px" }}>
                      <b>Sub-Category:</b>{" "}
                      {result.classification?.sub_category || "—"}
                    </p>
                    <p style={{ fontSize: "13px" }}>
                      <b>Tags:</b>{" "}
                      {(result.classification?.tags || []).length ? (
                        result.classification.tags.map((t, i) => (
                          <span key={i} style={styles.tag}>
                            {t}
                          </span>
                        ))
                      ) : (
                        "—"
                      )}
                    </p>
                  </div>

                  {result.document_analysis &&
                    result.document_analysis.document_type && (
                      <div style={styles.section}>
                        <div style={styles.sectionTitle}>
                          DOCUMENT ANALYSIS
                        </div>
                        <p style={{ fontSize: "13px" }}>
                          <b>Document Type:</b>{" "}
                          {result.document_analysis.document_type}
                        </p>
                        <p style={styles.smallHint}>Summary Points:</p>
                        <ul style={styles.actionsList}>
                          {(
                            result.document_analysis.summary_points || []
                          ).map((p, idx) => (
                            <li key={idx}>{p}</li>
                          ))}
                        </ul>
                        <p style={styles.smallHint}>Red Flags:</p>
                        <ul style={styles.actionsList}>
                          {(result.document_analysis.red_flags || []).map(
                            (f, idx) => (
                              <li key={idx} style={{ color: "#f97373" }}>
                                ⚠ {f}
                              </li>
                            )
                          )}
                        </ul>
                      </div>
                    )}

                  <div style={styles.section}>
                    <div style={styles.sectionTitle}>
                      RELEVANT LAWS &amp; RIGHTS
                    </div>
                    {(result.rights_and_laws || []).length ? (
                      result.rights_and_laws.map((law, idx) => (
                        <div key={idx} style={styles.ipcCard}>
                          <div style={{ fontWeight: 600 }}>
                            {law.act} – {law.section}
                          </div>
                          <div>
                            <b>Title:</b> {law.title}
                          </div>
                          <div>
                            <b>Description:</b> {law.description}
                          </div>
                          <div>
                            <b>Punishment:</b> {law.punishment || "N/A"}
                          </div>
                          <div>
                            <b>Cognizable:</b> {law.cognizable || "N/A"}
                          </div>
                          <div>
                            <b>Bailable:</b> {law.bailable || "N/A"}
                          </div>
                          <div>
                            <b>Court:</b> {law.court || "N/A"}
                          </div>
                          {law.url && (
                            <div>
                              <b>Source:</b>{" "}
                              <a
                                href={law.url}
                                target="_blank"
                                rel="noreferrer"
                                style={{ color: "#93c5fd" }}
                              >
                                {law.url}
                              </a>
                            </div>
                          )}
                        </div>
                      ))
                    ) : (
                      <p style={{ fontSize: "13px" }}>
                        No specific IPC sections matched from the dataset.
                      </p>
                    )}
                  </div>

                  <div style={styles.section}>
                    <div style={styles.sectionTitle}>STEP-BY-STEP ACTIONS</div>
                    <ul style={styles.actionsList}>
                      {(result.actions || []).map((a, idx) => (
                        <li key={idx}>{a}</li>
                      ))}
                    </ul>
                  </div>

                  <div style={styles.section}>
                    <div style={styles.sectionTitle}>COMPLAINT TEMPLATE</div>
                    <p style={styles.smallHint}>
                      Fill your details below and click <b>Fill Template</b>.
                      Placeholders like [FULL NAME], [FULL ADDRESS], [OPPOSITE
                      PARTY NAME] will be replaced.
                    </p>

                    <div
                      style={{
                        display: "grid",
                        gridTemplateColumns: isNarrow
                          ? "minmax(0, 1fr)"
                          : "1fr 1fr",
                        gap: "8px",
                        margin: "8px 0 10px",
                      }}
                    >
                      <input
                        style={styles.input}
                        placeholder="Your Full Name"
                        value={templateForm.full_name}
                        onChange={(e) =>
                          handleTemplateChange("full_name", e.target.value)
                        }
                      />
                      <input
                        style={styles.input}
                        placeholder="Your Address"
                        value={templateForm.address}
                        onChange={(e) =>
                          handleTemplateChange("address", e.target.value)
                        }
                      />
                      <input
                        style={styles.input}
                        placeholder="Opposite Party Name"
                        value={templateForm.opposite_party_name}
                        onChange={(e) =>
                          handleTemplateChange(
                            "opposite_party_name",
                            e.target.value
                          )
                        }
                      />
                      <input
                        style={styles.input}
                        placeholder="Opposite Party Address"
                        value={templateForm.opposite_party_address}
                        onChange={(e) =>
                          handleTemplateChange(
                            "opposite_party_address",
                            e.target.value
                          )
                        }
                      />
                      <input
                        style={styles.input}
                        placeholder="Date (e.g. 03-12-2025)"
                        value={templateForm.date}
                        onChange={(e) =>
                          handleTemplateChange("date", e.target.value)
                        }
                      />
                      <input
                        style={styles.input}
                        placeholder="Mobile Number"
                        value={templateForm.mobile_number}
                        onChange={(e) =>
                          handleTemplateChange(
                            "mobile_number",
                            e.target.value
                          )
                        }
                      />
                      <input
                        style={styles.input}
                        placeholder="Email ID"
                        value={templateForm.email_id}
                        onChange={(e) =>
                          handleTemplateChange("email_id", e.target.value)
                        }
                      />
                      <input
                        style={styles.input}
                        placeholder="Signature (name as you sign)"
                        value={templateForm.signature}
                        onChange={(e) =>
                          handleTemplateChange("signature", e.target.value)
                        }
                      />
                    </div>

                    <div
                      style={{
                        display: "flex",
                        gap: "8px",
                        flexWrap: "wrap",
                        marginBottom: "8px",
                      }}
                    >
                      <button
                        style={{
                          ...styles.buttonPrimary,
                          ...(fillingTemplate ? styles.buttonDisabled : {}),
                          marginTop: 0,
                        }}
                        onClick={fillTemplate}
                        disabled={fillingTemplate}
                      >
                        {fillingTemplate ? "Filling Template..." : "Fill Template"}
                      </button>
                      <button
                        style={{
                          ...styles.buttonSecondary,
                          ...(downloadingPdf ? styles.buttonDisabled : {}),
                          marginTop: 0,
                        }}
                        onClick={downloadPdf}
                        disabled={downloadingPdf}
                      >
                        {downloadingPdf ? "Downloading..." : "Download PDF"}
                      </button>
                    </div>

                    <p
                      style={{
                        ...styles.smallHint,
                        marginTop: "4px",
                        marginBottom: "4px",
                      }}
                    >
                      Preview
                    </p>
                    <pre style={styles.pre}>{result.complaint_template}</pre>
                  </div>

                  <div style={styles.section}>
                    <div style={styles.sectionTitle}>DISCLAIMER</div>
                    <p style={styles.disclaimer}>{result.disclaimer}</p>
                  </div>
                </>
              ) : (
                <div style={styles.section}>
                  <div style={styles.sectionTitle}>HOW IT WORKS</div>
                  <p style={{ fontSize: "13px", color: "#e5e7eb" }}>
                    1. Describe your issue or upload a legal document.
                    <br />
                    2. NYAAYA.AI classifies the matter, uses your IPC dataset and
                    other Acts, and generates:
                  </p>
                  <ul style={styles.actionsList}>
                    <li>Issue summary &amp; legal category</li>
                    <li>Relevant IPC &amp; Indian law sections</li>
                    <li>Step-by-step action guidance (informational only)</li>
                    <li>Editable complaint / notice template</li>
                  </ul>
                  <p style={styles.disclaimer}>
                    This is informational assistance only and is not a
                    substitute for advice from a qualified advocate.
                  </p>
                </div>
              )}

              {error && result && (
                <div style={styles.error}>⚠ {error}</div>
              )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
