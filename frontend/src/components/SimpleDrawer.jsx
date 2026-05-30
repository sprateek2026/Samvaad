export default function SimpleDrawer({ isOpen, onClose, title, children }) {
  if (!isOpen) return null;

  return (
    <>
      {/* Grey Overlay - OUTSIDE drawer */}
      <div style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "rgba(0,0,0,0.4)",
        zIndex: 40,
        onClick: onClose
      }} />

      {/* Centered Modal Popup */}
      <div style={{
        position: "fixed",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
        width: "90%",
        maxWidth: "500px",
        maxHeight: "85vh",
        backgroundColor: "white",
        borderRadius: "12px",
        boxShadow: "0 25px 50px -12px rgba(0,0,0,0.25)",
        zIndex: 50,
        display: "flex",
        flexDirection: "column",
        overflow: "hidden"
      }}>
        {/* Header */}
        <div style={{
          padding: "1.5rem",
          borderBottom: "1px solid #e5e7eb",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexShrink: 0
        }}>
          <h2 style={{ fontSize: "1.125rem", fontWeight: 600, color: "#1f2937" }}>{title}</h2>
          <button
            onClick={onClose}
            style={{
              background: "none",
              border: "none",
              cursor: "pointer",
              fontSize: "1.5rem",
              color: "#9ca3af"
            }}
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div style={{
          flex: 1,
          overflowY: "auto",
          padding: "1.5rem"
        }}>
          {children}
        </div>
      </div>
    </>
  );
}
