// app.js - HTMX + animații

document.body.addEventListener('htmx:afterSwap', function(evt) {
    // Adaugă animație la rezultat
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
    if (form.querySelector('[name="age"]')) {
        const age = form.querySelector('[name="age"]').value;
        if (age < 10 || age > 100) {
            alert('Vârsta trebuie să fie între 10 și 100 ani.');
            e.preventDefault();
        }
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const select = document.querySelector('[name="macro_ratio"]');
    const descDiv = document.getElementById('macro-desc');
    const descText = document.getElementById('desc-text');

    function updateDescription() {
        const selected = select.options[select.selectedIndex];
        const desc = selected.dataset.desc || "Alege un raport pentru a vedea detalii.";
        descText.textContent = desc;
        descDiv.style.display = desc ? 'block' : 'none';
    }

    select.addEventListener('change', updateDescription);
    updateDescription(); // la încărcare
});