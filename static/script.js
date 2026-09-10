function initChart() {
    const canvas = document.getElementById("closeChart");
    if (!canvas) return;

    const dates = window.chart_dates || [];
    const closes = window.chart_closes || [];

    if (!dates.length || !closes.length) {
        canvas.style.display = "none";
        return;
    }

    canvas.width = canvas.offsetWidth || 500;
    canvas.height = 250;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const padding = { top: 20, right: 20, bottom: 40, left: 50 };
    const chartWidth = canvas.width - padding.left - padding.right;
    const chartHeight = canvas.height - padding.top - padding.bottom;

    const xMin = new Date(dates[0]);
    const xMax = new Date(dates[dates.length - 1]);
    const yMin = Math.min(...closes) * 0.95;
    const yMax = Math.max(...closes) * 1.05;

    const xRange = xMax - xMin || 1;
    const yRange = yMax - yMin || 1;

    function x(val) {
        return ((new Date(val) - xMin) / xRange) * chartWidth + padding.left;
    }

    function y(val) {
        return padding.top + chartHeight - ((val - yMin) / yRange) * chartHeight;
    }

    ctx.fillStyle = "#0d1a26";
    ctx.fillRect(padding.left - 2, padding.top - 2, chartWidth + 4, chartHeight + 4);

    ctx.strokeStyle = "#00d4aa";
    ctx.lineWidth = 2;

    ctx.beginPath();
    ctx.moveTo(x(dates[0]), y(closes[0]));
    for (let i = 1; i < dates.length; i++) {
        ctx.lineTo(x(dates[i]), y(closes[i]));
    }
    ctx.stroke();

    ctx.strokeStyle = "#1e3a50";
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);
    for (let i = 0; i < dates.length; i++) {
        const px = x(dates[i]);
        ctx.beginPath();
        ctx.moveTo(px, padding.top);
        ctx.lineTo(px, padding.top + chartHeight);
        ctx.stroke();
    }
    ctx.setLineDash([]);

    ctx.fillStyle = "#e0e7ef";
    ctx.font = "10px Segoe UI";
    ctx.textAlign = "center";

    const numXTicks = Math.max(1, Math.floor(dates.length / 3));
    for (let i = 0; i < dates.length; i += Math.max(1, Math.floor(dates.length / numXTicks))) {
        const d = dates[i];
        const px = x(d);
        ctx.fillText(d.substring(5), px, padding.top + chartHeight + 18);
    }

    for (let i = 0; i < closes.length; i++) {
        const px = x(dates[i]);
        const py = y(closes[i]);
        ctx.fillStyle = "#00d4aa";
        ctx.beginPath();
        ctx.arc(px, py, 2, 0, Math.PI * 2);
        ctx.fill();
    }
}

document.addEventListener("DOMContentLoaded", function() {
    initChart();

    const selector = document.getElementById("stock-selector");
    if (selector) {
        selector.addEventListener("change", function() {
            const symbol = this.value;
            if (!symbol) {
                window.location.href = "/";
                return;
            }
            fetch("/stock/" + symbol)
                .then(res => res.ok ? res.json() : res.text())
                .then(data => {
                    if (data && data.redirect) {
                        window.location.href = data.redirect;
                    } else if (data && data.html) {
                        document.body.innerHTML = data.html;
                        document.body.style.display = "block";
                        updatePage();
                    }
                })
                .catch(err => {
                    console.error("Error:", err);
                    document.body.innerHTML = '<div class="error-container"><div class="error-card"><h2>Error</h2><p>Failed to load stock detail</p><a href="/">Go Home</a></div></div>';
                });
        });
    }
});

function updatePage() {
    initChart();
}