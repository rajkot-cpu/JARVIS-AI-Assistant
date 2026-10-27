// apps/windows-3d/ui/js/scene.js — Phase 1 holographic desk (visual shell)
import * as THREE from "../vendor/three.module.min.js";
import { CSS2DRenderer, CSS2DObject } from "../vendor/CSS2DRenderer.js";
import { OrbitControls } from "../vendor/OrbitControls.js";

const BG = 0x04070b, CYAN = 0x38d4ff;
const ACTIONS = ["sessionStart", "workdayDry", "workdayReal", "toggleMute"];

function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text != null) e.textContent = text;
  return e;
}

export function createDesk(containerEl) {
  const listeners = [];
  const emit = (name) => { if (ACTIONS.includes(name)) listeners.forEach((cb) => cb(name)); };

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(BG);
  scene.fog = new THREE.Fog(BG, 12, 40);

  const w = () => containerEl.clientWidth || window.innerWidth;
  const h = () => containerEl.clientHeight || window.innerHeight;
  const camera = new THREE.PerspectiveCamera(50, w() / h(), 0.1, 100);
  camera.position.set(0, 2.0, 11);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(w(), h());
  containerEl.appendChild(renderer.domElement);

  const labels = new CSS2DRenderer();
  labels.setSize(w(), h());
  labels.domElement.className = "css2d-layer";
  containerEl.appendChild(labels.domElement);

  // Faint floor grid + soft glow discs under plates
  const grid = new THREE.GridHelper(40, 40, CYAN, CYAN);
  grid.material.transparent = true; grid.material.opacity = 0.08;
  grid.position.y = -2;
  scene.add(grid);
  const glowMat = new THREE.MeshBasicMaterial({ color: CYAN, transparent: true, opacity: 0.045, depthWrite: false });
  function glow(x, z, r) {
    const m = new THREE.Mesh(new THREE.CircleGeometry(r, 48), glowMat);
    m.rotation.x = -Math.PI / 2; m.position.set(x, -1.98, z); scene.add(m);
  }

  // Status plate (center-front)
  const status = el("div", "plate status-plate");
  status.append(el("div", "plate-title", "J.A.R.V.I.S · STATUS"));
  const headline = el("div", "headline", "…");
  const strip = el("div", "strip", "");
  const statusErr = el("div", "status-error", "");
  status.append(headline, strip, statusErr);

  // Brief plate (right)
  const brief = el("div", "plate brief-plate");
  brief.append(el("div", "plate-title", "TODAY'S BRIEF"));
  const briefText = el("div", "brief-text empty", "No brief for today.");
  brief.append(briefText);

  // Actions plate (left/lower)
  const actions = el("div", "plate actions-plate");
  actions.append(el("div", "plate-title", "ACTIONS"));
  const mk = (label, cls, action) => {
    const b = el("button", "btn " + cls, label);
    b.type = "button"; b.dataset.action = action;
    b.addEventListener("click", (e) => { e.stopPropagation(); emit(action); });
    actions.append(b); return b;
  };
  mk("SESSION START", "", "sessionStart");
  mk("DRY-RUN WORKDAY", "primary", "workdayDry");
  mk("START WORKDAY (R3)", "filled", "workdayReal");
  const muteRow = el("label", "mute-row");
  const muteBox = document.createElement("input"); muteBox.type = "checkbox";
  muteBox.addEventListener("change", (e) => { e.stopPropagation(); emit("toggleMute"); });
  muteRow.append(muteBox, el("span", null, "MUTE"));
  actions.append(muteRow);

  // Keep plate interactions from driving orbit
  [status, brief, actions].forEach((p) => p.addEventListener("pointerdown", (e) => e.stopPropagation()));

  const place = (node, x, y, z) => { const o = new CSS2DObject(node); o.position.set(x, y, z); scene.add(o); return o; };
  place(status, 0, 0.3, 1.5);   glow(0, 1.5, 2.2);
  place(brief, 5.6, 1.9, -1);   glow(5.2, -1, 1.6);
  place(actions, -5.6, -1.0, 0); glow(-5.2, 0, 1.4);

  const controls = new OrbitControls(camera, labels.domElement);
  labels.domElement.style.pointerEvents = "auto";
  controls.enableDamping = true; controls.dampingFactor = 0.06;
  controls.enablePan = false;
  controls.minDistance = 5; controls.maxDistance = 16;
  controls.maxPolarAngle = Math.PI * 0.55;
  controls.autoRotate = true; controls.autoRotateSpeed = 0.25; // slow drift, no strobes
  controls.addEventListener("start", () => { controls.autoRotate = false; });

  function resize() {
    camera.aspect = w() / h(); camera.updateProjectionMatrix();
    renderer.setSize(w(), h()); labels.setSize(w(), h());
  }
  window.addEventListener("resize", resize);

  let running = true;
  (function loop() {
    if (!running) return;
    requestAnimationFrame(loop);
    controls.update();
    renderer.render(scene, camera);
    labels.render(scene, camera);
  })();

  return {
    setStatus(s = {}) {
      headline.textContent = s.headline || "—";
      headline.classList.toggle("quiet", !!s.quiet_hours && !s.error);
      headline.classList.toggle("danger", !!s.error || s.policy_ok === false);
      strip.replaceChildren(
        document.createTextNode(`DATE ${s.today || "—"} · POLICY `),
        el("span", s.policy_ok ? "ok" : "bad", s.policy_ok ? "OK" : "NOT APPROVED"),
        document.createTextNode(" · QUIET "),
        el("span", s.quiet_hours ? "gold" : "", s.quiet_hours ? "ON" : "OFF"),
        document.createTextNode(` · ROOT ${s.root || "—"}`),
      );
      statusErr.textContent = s.error || "";
    },
    setBrief(text) {
      const t = (text || "").trim();
      briefText.textContent = t || "No brief for today.";
      briefText.classList.toggle("empty", !t);
    },
    setMuteUi(muted) { muteBox.checked = !!muted; },
    onAction(cb) { if (typeof cb === "function") listeners.push(cb); },
    dispose() { running = false; window.removeEventListener("resize", resize); controls.dispose(); renderer.dispose(); },
  };
}
