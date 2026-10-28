// apps/windows-cc/ui/js/bridge.js
export async function call(method, ...args) {
  try {
    if (window.pywebview && window.pywebview.api && typeof window.pywebview.api[method] === "function") {
      return await window.pywebview.api[method](...args);
    }
  } catch (e) {
    return { ok: false, error: String(e) };
  }
  return { ok: false, error: "offline" };
}
