// Centralized MapLibre style source.
//
// When VITE_MAPTILER_API_KEY is configured (set it in Vercel/host env and in
// local .env), we use MapTiler's streets style. If the key is missing — e.g.
// the env var wasn't added to the deployment — we fall back to OpenFreeMap,
// which needs no API key, so maps still render instead of showing blank tiles.
const MAPTILER_KEY = import.meta.env.VITE_MAPTILER_API_KEY;

export const MAP_STYLE = MAPTILER_KEY
  ? `https://api.maptiler.com/maps/streets/style.json?key=${MAPTILER_KEY}`
  : "https://tiles.openfreemap.org/styles/liberty";

console.log("[map] style source:", MAPTILER_KEY ? "MapTiler" : "OpenFreeMap (no key)");
