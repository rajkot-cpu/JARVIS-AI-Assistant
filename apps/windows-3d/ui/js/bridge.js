// apps/windows-3d/ui/js/bridge.js
export async function api(name, ...args) {
  if (window.pywebview && window.pywebview.api && window.pywebview.api[name]) {
    return await window.pywebview.api[name](...args);
  }
  console.warn("bridge mock", name, args);
  if (name === "getStatus") {
    return { ok: true, data: { today: "2099-01-01", policy_ok: true, quiet_hours: false,
      root: "(mock)", headline: "SYSTEMS NOMINAL" } };
  }
  if (name === "getBrief") return { ok: true, data: { text: "(mock brief)" } };
  if (name === "getMute") return { ok: true, data: { muted: false } };
  return { ok: true, data: {} };
}
