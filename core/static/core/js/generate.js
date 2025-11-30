// core/static/core/js/generate.js
document.addEventListener('DOMContentLoaded', function () {
    const select = document.querySelector('[name="macro_ratio"]');
    const descDiv = document.getElementById('macro-desc');
    const descText = document.getElementById('desc-text');
    const fiberInfo = document.getElementById('fiber-info');

    function updateDescription() {
        const selected = select.options[select.selectedIndex];
        const desc = selected?.dataset?.desc || "";
        const fiber = selected?.dataset?.fiber || "14g / 1000 kcal";
        const name = selected?.text.split(' (')[0] || "";

        if (desc && name) {
            descText.innerHTML = `<strong>${name}:</strong> ${desc}`;
            fiberInfo.textContent = fiber;
            descDiv.style.display = 'block';
        } else {
            descDiv.style.display = 'none';
        }
    }

    select.addEventListener('change', updateDescription);
    updateDescription();
});