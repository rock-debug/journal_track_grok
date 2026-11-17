// Live cursor coordinate readout in bottom-right corner (lab-notebook HUD)
document.addEventListener('DOMContentLoaded', () => {
    const coordsEl = document.getElementById('cursor-coords');
    if (coordsEl) {
        document.addEventListener('mousemove', (e) => {
            coordsEl.innerHTML = `x: ${e.clientX} &nbsp; y: ${e.clientY}`;
        }, { passive: true });
    }
});
