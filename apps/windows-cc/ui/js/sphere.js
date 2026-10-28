// apps/windows-cc/ui/js/sphere.js — decorative canvas driven by health score
export function drawSphere(canvas, healthOk = 0.5) {
  const ctx = canvas.getContext("2d");
  const w = canvas.width, h = canvas.height;
  const cx = w / 2, cy = h / 2;
  const r = Math.min(w, h) * 0.32;
  ctx.clearRect(0, 0, w, h);
  const glow = Math.max(0.25, Math.min(1, healthOk));
  ctx.strokeStyle = `rgba(56,212,255,${0.35 + glow * 0.45})`;
  ctx.lineWidth = 1.5;
  for (let i = 0; i < 8; i++) {
    ctx.beginPath();
    ctx.ellipse(cx, cy, r, r * (0.35 + i * 0.08), (i * Math.PI) / 8, 0, Math.PI * 2);
    ctx.stroke();
  }
  ctx.beginPath();
  ctx.arc(cx, cy, r * 0.55, 0, Math.PI * 2);
  ctx.strokeStyle = `rgba(61,255,154,${0.2 + glow * 0.5})`;
  ctx.stroke();
}
