// apps/windows-3d/ui/js/app.js — wires desk to bridge
import { createDesk } from "./scene.js";
import { api } from "./bridge.js";
import { confirmR3 } from "./r3.js";

const banner = document.getElementById("banner");
function setBanner(msg, kind = "danger") {
  banner.textContent = msg || "";
  banner.classList.toggle("show", !!msg);
  banner.classList.toggle("danger", !!msg && kind === "danger");
  banner.classList.toggle("info", !!msg && kind === "info");
}

let desk;
try { desk = createDesk(document.getElementById("desk")); }
catch (e) { setBanner("3D init failed: " + e.message); throw e; }
window.jarvisDesk = desk;

let muted = false;

async function refreshStatus() {
  const s = await api("getStatus");
  s.ok ? desk.setStatus(s.data) : desk.setStatus({ headline: "STATUS UNAVAILABLE", error: s.error });
}
async function refreshMute() {
  const m = await api("getMute");
  if (m.ok) muted = !!m.data.muted;
  desk.setMuteUi(muted);
}
async function refresh() {
  await refreshStatus();
  const b = await api("getBrief"); if (b.ok) desk.setBrief(b.data.text);
  await refreshMute();
}

const errText = (r, what) => `${what} failed: ${r && r.error ? r.error : "unknown error"}`;

const handlers = {
  async sessionStart() {
    const r = await api("sessionStart");
    r.ok ? setBanner("Session started", "info") : setBanner(errText(r, "Session start"));
    await refresh();
  },
  async workdayDry() {
    const r = await api("workday", true);
    r.ok ? setBanner("Dry-run workday complete", "info") : setBanner(errText(r, "Dry-run workday"));
    await refreshStatus();
  },
  async workdayReal() {
    const ok = await confirmR3({
      title: "Start Workday",
      body: "This runs the real (non-dry) workday and will launch allowlisted apps. Continue?",
    });
    if (!ok) { setBanner("Start Workday cancelled", "info"); return; }
    const r = await api("workday", false);
    r.ok ? setBanner("Workday started", "info") : setBanner(errText(r, "Start Workday"));
    await refreshStatus();
  },
  async toggleMute() {
    const want = !muted;
    const r = await api("setMute", want);
    if (r.ok) {
      muted = r.data && typeof r.data.muted === "boolean" ? r.data.muted : want;
      setBanner("");
    } else {
      setBanner(errText(r, "Mute"));
    }
    desk.setMuteUi(muted); // host result wins; revert on failure
    await refreshStatus();
  },
};

let busy = false;
desk.onAction(async (a) => {
  if (busy) { if (a === "toggleMute") desk.setMuteUi(muted); return; }
  busy = true;
  try { await handlers[a](); }
  catch (e) { setBanner(String(e)); desk.setMuteUi(muted); }
  finally { busy = false; }
});

refresh().catch((e) => setBanner(String(e)));
window.addEventListener("pywebviewready", () => refresh().catch((e) => setBanner(String(e))));
