// core/static/core/js/dashboard.js
document.addEventListener('DOMContentLoaded', function () {
    const ctx = document.getElementById('bmiChart');
    if (!ctx) return;

    const labels = [
        {% for plan in plans %}
        "{{ plan.created_at|date:'d M' }}"{% if not forloop.last %}, {% endif %}
        {% empty %}
        "Fără date"
        {% endfor %}
    ];

    const data = [
        {% for plan in plans %}
        {{ plan.bmi|floatformat:1 }}{% if not forloop.last %}, {% endif %}
        {% empty %}
        0
        {% endfor %}
    ];

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'BMI',
                data: data,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true,
                pointRadius: 5,
                pointHoverRadius: 8,
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: false, min: 15, max: 40, ticks: { stepSize: 2 } } },
            animation: { duration: 1800, easing: 'easeOutQuart' }
        }
    });
});