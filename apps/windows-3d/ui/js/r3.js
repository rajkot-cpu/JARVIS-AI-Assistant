// apps/windows-3d/ui/js/r3.js — R3 confirm modal (title/body are fixed strings from app.js)
export function confirmR3({ title, body }) {
  return new Promise((resolve) => {
    const overlay = document.createElement("div");
    overlay.className = "r3-overlay";
    overlay.innerHTML = `<div class="r3-card"><h2>R3 // ${title}</h2><p>${body}</p>
      <div class="r3-row"><button class="ok">Confirm</button><button class="cancel">Cancel</button></div></div>`;
    document.body.appendChild(overlay);
    overlay.querySelector(".ok").onclick = () => { overlay.remove(); resolve(true); };
    overlay.querySelector(".cancel").onclick = () => { overlay.remove(); resolve(false); };
  });
}
