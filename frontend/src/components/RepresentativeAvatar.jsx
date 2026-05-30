import { useState } from "react";

export default function RepresentativeAvatar({
  photoPath,
  name,
  type = "corporator",
  size = "md",
  showHover = true,
  className = ""
}) {
  const [imageError, setImageError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Size mappings
  const sizeClasses = {
    sm: "w-10 h-10",      // 40x40px - list view
    md: "w-16 h-16",      // 64x64px - card view (enhanced)
    lg: "w-20 h-20",      // 80x80px - KYC modal
    xl: "w-32 h-32"       // 128x128px - premium KYC view
  };

  // Get initials from name
  function getInitials(fullName) {
    if (!fullName) return "?";
    const parts = fullName.trim().split(" ");
    if (parts.length >= 2) {
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    }
    return fullName.charAt(0).toUpperCase();
  }

  // Format photo URL
  function getPhotoUrl(path) {
    if (!path) return null;
    if (path.startsWith("http")) return path;
    return `http://localhost:8000/${path}`;
  }

  const photoUrl = !imageError ? getPhotoUrl(photoPath) : null;
  const initials = getInitials(name);
  const sizeClass = sizeClasses[size] || sizeClasses.md;
  const hoverClass = showHover ? "group-hover:scale-105 transition-transform duration-200" : "";

  return (
    <div className={`relative ${className}`}>
      {photoUrl ? (
        <>
          {isLoading && (
            <div className={`${sizeClass} rounded-full bg-gray-200 animate-pulse absolute inset-0`} />
          )}
          <img
            src={photoUrl}
            alt={name || type}
            className={`${sizeClass} rounded-full object-cover border-2 border-gray-200 ring-2 ring-offset-2 ring-indigo-200 ${hoverClass}`}
            onLoad={() => setIsLoading(false)}
            onError={() => {
              setImageError(true);
              setIsLoading(false);
            }}
          />
        </>
      ) : (
        <div
          className={`${sizeClass} rounded-full bg-gradient-to-br from-indigo-400 to-indigo-600 flex items-center justify-center border-2 border-gray-200 ring-2 ring-offset-2 ring-indigo-200 ${hoverClass}`}
          title={name || type}
        >
          <span className="text-white font-semibold" style={{
            fontSize: size === "sm" ? "0.75rem" : size === "md" ? "0.875rem" : size === "lg" ? "1rem" : "1.5rem"
          }}>
            {initials}
          </span>
        </div>
      )}
    </div>
  );
}
