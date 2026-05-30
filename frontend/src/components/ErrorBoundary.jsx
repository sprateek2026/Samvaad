import { Component } from "react";

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error("[ErrorBoundary] Render error:", error, info.componentStack);
  }

  handleRetry = () => {
    this.setState({ error: null });
    // Hard reload as a fallback when soft retry isn't enough
    if (this.retryCount >= 1) {
      window.location.reload();
    }
    this.retryCount = (this.retryCount || 0) + 1;
  };

  render() {
    if (!this.state.error) return this.props.children;

    return (
      <div style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "#f4f6fb",
        fontFamily: "Inter, sans-serif",
        padding: "24px",
      }}>
        <div style={{
          background: "#fff",
          borderRadius: "16px",
          padding: "40px 36px",
          maxWidth: "440px",
          width: "100%",
          boxShadow: "0 4px 24px rgba(0,0,0,0.08)",
          textAlign: "center",
        }}>
          <div style={{ fontSize: "40px", marginBottom: "16px" }}>⚠️</div>
          <h2 style={{ margin: "0 0 8px", fontSize: "1.25rem", fontWeight: 700, color: "#111827" }}>
            Something went wrong
          </h2>
          <p style={{ margin: "0 0 24px", fontSize: "0.875rem", color: "#6b7280", lineHeight: 1.6 }}>
            The application encountered an unexpected error. This is usually resolved by retrying.
          </p>
          <details style={{ marginBottom: "24px", textAlign: "left" }}>
            <summary style={{ cursor: "pointer", fontSize: "0.75rem", color: "#9ca3af", userSelect: "none" }}>
              Technical details
            </summary>
            <pre style={{
              marginTop: "8px",
              padding: "12px",
              background: "#f9fafb",
              borderRadius: "8px",
              fontSize: "0.7rem",
              color: "#374151",
              overflowX: "auto",
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
            }}>
              {this.state.error?.message}
            </pre>
          </details>
          <div style={{ display: "flex", gap: "12px" }}>
            <button
              onClick={this.handleRetry}
              style={{
                flex: 1,
                padding: "10px 20px",
                background: "#f97316",
                color: "#fff",
                border: "none",
                borderRadius: "8px",
                fontWeight: 600,
                fontSize: "0.875rem",
                cursor: "pointer",
              }}
            >
              Try again
            </button>
            <button
              onClick={() => window.location.reload()}
              style={{
                flex: 1,
                padding: "10px 20px",
                background: "#f3f4f6",
                color: "#374151",
                border: "none",
                borderRadius: "8px",
                fontWeight: 600,
                fontSize: "0.875rem",
                cursor: "pointer",
              }}
            >
              Reload page
            </button>
          </div>
        </div>
      </div>
    );
  }
}
