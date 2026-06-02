// Centralized MapLibre style source.
//
// When VITE_MAPTILER_API_KEY is configured (set it in Vercel/host env and in
// local .env), we use MapTiler's streets style. If the key is missing — e.g.
// the env var wasn't added to the deployment — we fall back to OpenFreeMap,
// which needs no API key, so maps still render instead of showing blank tiles.
const MAPTILER_KEY = import.meta.env.VITE_MAPTILER_API_KEY;

// Keyless fallback that needs no API key and no domain whitelist — always works.
export const FALLBACK_MAP_STYLE = "https://tiles.openfreemap.org/styles/liberty";

export const MAP_STYLE = MAPTILER_KEY
  ? `https://api.maptiler.com/maps/streets/style.json?key=${MAPTILER_KEY}`
  : FALLBACK_MAP_STYLE;

console.log("[map] style source:", MAPTILER_KEY ? "MapTiler" : "OpenFreeMap (no key)");

// Attaches a guard so that if the preferred style fails to load (e.g. MapTiler
// returns 403 because the key is invalid or the current domain isn't whitelisted),
// the map swaps to the keyless OpenFreeMap style. Without this the base tiles
// stay blank AND the "load" event never fires, so overlay markers never appear.
// Call once, right after `new maplibregl.Map(...)`. Returns the map for chaining.
export function withStyleFallback(map) {
  if (MAP_STYLE === FALLBACK_MAP_STYLE) return map; // already keyless, nothing to fall back to
  let swapped = false;
  map.on("error", (e) => {
    if (swapped) return;
    const msg = String(e?.error?.message || e?.error || "");
    // Style/sprite/glyphs fetch failures or any 4xx/5xx from the tile provider
    if (/style|sprite|glyph|source|fetch|ajax|40\d|50\d/i.test(msg)) {
      swapped = true;
      console.warn("[map] preferred style failed, falling back to OpenFreeMap:", msg);
      try { map.setStyle(FALLBACK_MAP_STYLE); } catch (err) { console.error("[map] fallback failed", err); }
    }
  });
  return map;
}
