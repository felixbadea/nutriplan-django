// core/static/core/js/global.js

// HTMX: animație la swap
document.body.addEventListener('htmx:afterSwap', function(evt) {
    const result = document.getElementById('result');
    if (result) {
        result.style.opacity = '0';
        result.style.transform = 'translateY(20px)';
        setTimeout(() => {
            result.style.transition = 'all 0.6s ease';
            result.style.opacity = '1';
            result.style.transform = 'translateY(0)';
        }, 10);
    }
});

// Validare formular
document.addEventListener('submit', function(e) {
    const form = e.target;
    const ageInput = form.querySelector('[name="age"]');
    if (ageInput) {
        const age = parseInt(ageInput.value);
        if (isNaN(age) || age < 10 || age > 100) {
            alert('Vârsta trebuie să fie între 10 și 100 ani.');
            e.preventDefault();
        }
    }
});

// Tooltips + Macro desc + Loading + Alerts
document.addEventListener('DOMContentLoaded', function () {
    // Tooltips
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => new bootstrap.Tooltip(el));

    // Macro ratio description
    const select = document.querySelector('[name="macro_ratio"]');
    const descDiv = document.getElementById('macro-desc');
    const descText = document.getElementById('desc-text');

    if (select && descDiv && descText) {
        function updateDescription() {
            const selected = select.options[select.selectedIndex];
            const desc = selected?.dataset?.desc || "Alege un raport pentru a vedea detalii.";
            descText.textContent = desc;
            descDiv.style.display = desc && desc !== "Alege un raport pentru a vedea detalii." ? 'block' : 'none';
        }
        select.addEventListener('change', updateDescription);
        updateDescription();
    }

    // Loading
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', () => {
            const loading = document.getElementById('loading');
            if (loading) loading.style.display = 'block';
        });
    }

    // Auto-dismiss alerts
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => new bootstrap.Alert(alert).close(), 5000);
    });
});