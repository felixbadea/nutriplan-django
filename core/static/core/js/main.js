// main.js
document.addEventListener('DOMContentLoaded', function () {
    // Tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(el => new bootstrap.Tooltip(el));

    // Macro ratio description (generate.html)
    const macroSelect = document.querySelector('[name="macro_ratio"]');
    const descDiv = document.getElementById('macro-desc');
    const descText = document.getElementById('desc-text');

    if (macroSelect && descDiv && descText) {
        function updateDescription() {
            const selected = macroSelect.options[macroSelect.selectedIndex];
            const desc = selected?.dataset.desc || "Alege un raport pentru a vedea detalii.";
            descText.textContent = desc;
            descDiv.style.display = desc && desc !== "Alege un raport pentru a vedea detalii." ? 'block' : 'none';
        }
        macroSelect.addEventListener('change', updateDescription);
        updateDescription();
    }

    // Loading spinner on form submit
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function () {
            const loading = document.getElementById('loading');
            if (loading) loading.style.display = 'block';
        });
    }

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});