/**
 * ALPHA6 Enterprise Terminal Client JavaScript
 * Minimalist Institutional Design, Real-Time Market Analytics & Native Candlestick Terminal.
 */

let radarChartInstance = null;
let equityChartInstance = null;
let currentChartSymbol = 'RELIANCE.NS';
let currentChartPeriod = '1y';
let searchDebounceTimer = null;
let currentSuggestions = [];
let selectedSuggestionIndex = -1;

// State tracker for lazy tab loading (prevents startup waterfall lag)
const tabLoaded = {
    'tab-screener': true,
    'tab-audit': false,
    'tab-chart': false,
    'tab-backtest': false,
    'tab-risk': false
};

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    // Universe dropdown toggle
    const univSelect = document.getElementById('screener-universe');
    if (univSelect) {
        univSelect.addEventListener('change', (e) => {
            const wrapper = document.getElementById('custom-tickers-wrapper');
            if (e.target.value === 'custom') {
                wrapper.classList.remove('hidden');
            } else {
                wrapper.classList.add('hidden');
            }
        });
    }

    // Initialize Autocomplete Search
    initSearchAutocomplete();

    // Initial load: Only execute the active Screener view!
    runScreener();

    // Responsive window resize for Plotly candlestick terminal
    window.addEventListener('resize', () => {
        const chartEl = document.getElementById('native-candlestick-chart');
        if (chartEl && window.Plotly) {
            Plotly.Plots.resize(chartEl);
        }
    });
});

// ==================== TAB SWITCHING (LAZY LOADING) ====================
function switchTab(tabId) {
    const tabs = ['tab-screener', 'tab-audit', 'tab-chart', 'tab-backtest', 'tab-risk'];
    const navs = ['nav-screener', 'nav-audit', 'nav-chart', 'nav-backtest', 'nav-risk'];

    tabs.forEach(t => {
        const el = document.getElementById(t);
        if (el) {
            if (t === tabId) {
                el.classList.remove('hidden');
            } else {
                el.classList.add('hidden');
            }
        }
    });

    navs.forEach(n => {
        const el = document.getElementById(n);
        if (el) {
            if (n === 'nav-' + tabId.replace('tab-', '')) {
                el.classList.add('active-tab');
            } else {
                el.classList.remove('active-tab');
            }
        }
    });

    // Lazy load each module on first activation
    if (tabId === 'tab-audit' && !tabLoaded['tab-audit']) {
        tabLoaded['tab-audit'] = true;
        executeAudit(currentChartSymbol || 'RELIANCE.NS');
    } else if (tabId === 'tab-chart' && !tabLoaded['tab-chart']) {
        tabLoaded['tab-chart'] = true;
        const sym = document.getElementById('live-symbol-input')?.value || currentChartSymbol;
        loadLiveChart(sym, currentChartPeriod);
    } else if (tabId === 'tab-backtest' && !tabLoaded['tab-backtest']) {
        tabLoaded['tab-backtest'] = true;
        runBacktest();
    } else if (tabId === 'tab-risk' && !tabLoaded['tab-risk']) {
        tabLoaded['tab-risk'] = true;
        calculateRiskPlan();
    }
}

// ==================== TAB 1: UNIVERSE SCREENER ====================
async function runScreener() {
    const universe = document.getElementById('screener-universe').value;
    const custom = document.getElementById('custom-tickers-input').value;
    const threshold = parseFloat(document.getElementById('screener-threshold').value) || 78.0;

    const btn = document.getElementById('btn-run-screener');
    btn.disabled = true;
    btn.innerHTML = `<span>Scanning...</span>`;

    const tbody = document.getElementById('screener-tbody');
    tbody.innerHTML = `<tr><td colspan="13" class="p-8 text-center text-neutral-400 font-mono">Running quantitative 6-pillar audit...</td></tr>`;

    try {
        let url = `/api/screen?universe=${universe}&threshold=${threshold}`;
        if (universe === 'custom' && custom) {
            url += `&custom_symbols=${encodeURIComponent(custom)}`;
        }

        const res = await fetch(url);
        if (!res.ok) {
            const errText = await res.text();
            throw new Error(`Server returned status ${res.status}: ${errText.slice(0, 80)}`);
        }
        const data = await res.json();

        // Update KPIs
        document.getElementById('kpi-total').innerText = data.total_scanned;
        document.getElementById('kpi-passed').innerText = data.high_conviction_count;
        const passRate = data.total_scanned > 0 ? ((data.high_conviction_count / data.total_scanned) * 100).toFixed(0) : 0;
        document.getElementById('kpi-pass-rate').innerText = `${passRate}% Pass Rate`;

        const avgScore = data.results.length > 0 
            ? (data.results.reduce((acc, r) => acc + r.composite_score, 0) / data.results.length).toFixed(1)
            : 0;
        document.getElementById('kpi-avg').innerText = `${avgScore}%`;

        const riskCount = data.results.filter(r => r.red_flag_count > 0).length;
        document.getElementById('kpi-risk').innerText = riskCount;

        // Render Top Picks Cards
        const topGrid = document.getElementById('top-picks-grid');
        topGrid.innerHTML = '';
        if (data.high_conviction.length > 0) {
            data.high_conviction.slice(0, 3).forEach(pick => {
                const card = document.createElement('div');
                card.className = 'bg-[#121212] border border-[#262626] hover:border-neutral-500 transition rounded-lg p-4 cursor-pointer';
                card.onclick = () => { executeAudit(pick.symbol); switchTab('tab-audit'); };
                card.innerHTML = `
                    <div class="flex justify-between items-center mb-1">
                        <span class="text-sm font-bold text-white font-mono">${pick.symbol}</span>
                        <span class="text-[11px] px-2 py-0.5 rounded bg-neutral-800 text-neutral-200 border border-neutral-700 font-mono font-bold">${pick.composite_score}% BUY</span>
                    </div>
                    <div class="text-xs text-neutral-400 mb-2 truncate">${pick.name}</div>
                    <div class="text-lg font-bold text-white font-mono mb-2">${pick.currency} ${parseFloat(pick.price).toFixed(2)}</div>
                    <div class="grid grid-cols-2 gap-1 text-[11px] font-mono text-neutral-300 pt-2 border-t border-[#262626]">
                        <div>OCF Quality: <b class="text-white">${pick.ocf_score}/100</b></div>
                        <div>Debt Health: <b class="text-white">${pick.debt_score}/100</b></div>
                    </div>
                `;
                topGrid.appendChild(card);
            });
        } else {
            topGrid.innerHTML = `<div class="col-span-3 p-3.5 rounded bg-[#121212] border border-[#262626] text-neutral-400 text-xs font-mono">No equities cleared the strict ${threshold}% threshold with zero red flags today. Capital is safely preserved.</div>`;
        }

        // Render Table Rows
        tbody.innerHTML = '';
        data.results.forEach(r => {
            const tr = document.createElement('tr');
            tr.className = 'hover:bg-[#1A1A1A] cursor-pointer transition';
            tr.onclick = () => { executeAudit(r.symbol); switchTab('tab-audit'); };

            const isPass = r.is_recommended;
            const hasFlags = r.red_flag_count > 0;
            const badgeClass = isPass 
                ? 'bg-white text-black font-semibold' 
                : (hasFlags ? 'bg-neutral-800 text-neutral-400 border border-neutral-700' : 'bg-neutral-900 text-neutral-300 border border-neutral-800');

            const scoreWeight = r.composite_score >= 78 ? 'text-white font-bold' : (r.composite_score >= 60 ? 'text-neutral-300' : 'text-neutral-500');

            tr.innerHTML = `
                <td class="p-3 font-bold text-white">${r.symbol}</td>
                <td class="p-3 font-sans font-normal text-neutral-300 truncate max-w-[180px]">${r.name}</td>
                <td class="p-3 font-mono">${r.currency} ${parseFloat(r.price).toFixed(2)}</td>
                <td class="p-3 font-mono ${scoreWeight}">${r.composite_score}%</td>
                <td class="p-3 font-mono text-neutral-400">${r.volume_score}</td>
                <td class="p-3 font-mono text-neutral-400">${r.sales_score}</td>
                <td class="p-3 font-mono text-neutral-400">${r.ocf_score}</td>
                <td class="p-3 font-mono text-neutral-400">${r.debt_score}</td>
                <td class="p-3 font-mono text-neutral-400">${r.pricing_score}</td>
                <td class="p-3 font-mono text-neutral-400">${r.skin_score}</td>
                <td class="p-3 font-mono text-neutral-400">${r.piotroski_f_score}/9</td>
                <td class="p-3 font-mono text-neutral-400">${r.altman_z_score}</td>
                <td class="p-3"><span class="text-[10px] px-2 py-0.5 rounded font-mono ${badgeClass}">${r.signal}</span></td>
            `;
            tbody.appendChild(tr);
        });

    } catch (e) {
        console.error(e);
        tbody.innerHTML = `<tr><td colspan="13" class="p-8 text-center text-neutral-400 font-mono">Error scanning universe: ${e.message}</td></tr>`;
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<span>Execute Screen</span>`;
    }
}

// ==================== TAB 2: FORENSIC 6-PILLAR AUDIT ====================
async function executeAudit(symbol) {
    if (!symbol) return;
    try {
        const res = await fetch(`/api/audit/${encodeURIComponent(symbol)}`);
        if (!res.ok) throw new Error('Symbol audit failed');
        const data = await res.json();
        const ev = data.evaluation;
        const p = ev.pillars;

        currentChartSymbol = ev.symbol;

        // Populate Header
        document.getElementById('audit-symbol').innerText = ev.symbol;
        document.getElementById('audit-company-name').innerText = `${ev.short_name} • ${ev.sector} • ${ev.currency} ${parseFloat(ev.current_price).toFixed(2)}`;
        document.getElementById('audit-composite-score').innerText = `${ev.composite_score}%`;

        const badge = document.getElementById('audit-signal-badge');
        badge.innerText = ev.signal;
        badge.className = ev.is_recommended 
            ? 'text-xs px-2.5 py-0.5 rounded font-mono font-bold bg-white text-black'
            : (ev.red_flags.length > 0 ? 'text-xs px-2.5 py-0.5 rounded font-mono font-medium bg-neutral-900 text-neutral-400 border border-neutral-800' : 'text-xs px-2.5 py-0.5 rounded font-mono font-medium bg-neutral-800 text-neutral-200 border border-neutral-700');

        document.getElementById('audit-piotroski').innerText = `${ev.piotroski_f_score} / 9`;
        document.getElementById('audit-altman').innerText = `${ev.altman_z_score} (${ev.altman_status.split(' ')[0]})`;

        // Render Radar Chart
        renderRadarChart(p, ev.symbol);

        // Render Pillar Breakdown Cards
        const breakdown = document.getElementById('audit-pillar-breakdown');
        breakdown.innerHTML = '';

        const pillarOrder = [
            { key: 'volume_momentum', title: '1. Volume & Momentum Growth' },
            { key: 'sales_growth', title: '2. Sales Revenue CAGR' },
            { key: 'ocf_quality', title: '3. Operating Cash Flow Quality' },
            { key: 'debt_solvency', title: '4. Debt & Solvency Health' },
            { key: 'pricing_power', title: '5. Pricing Power & Moat' },
            { key: 'skin_in_game', title: '6. Promoter / Insider Skin in Game' },
        ];

        if (ev.red_flags.length > 0) {
            const rfBox = document.createElement('div');
            rfBox.className = 'bg-[#141414] border-l-2 border-neutral-400 p-3 rounded text-xs text-neutral-300 font-mono space-y-1';
            rfBox.innerHTML = `<b>RISK SHIELD WARNINGS:</b>` + ev.red_flags.map(f => `<div>• ${f}</div>`).join('');
            breakdown.appendChild(rfBox);
        }

        pillarOrder.forEach(item => {
            const pol = p[item.key];
            const div = document.createElement('div');
            div.className = 'bg-[#0E0E0E] border border-[#262626] rounded p-3 space-y-1';
            
            div.innerHTML = `
                <div class="flex justify-between items-center">
                    <span class="text-xs font-medium text-white uppercase font-mono">${item.title}</span>
                    <span class="text-xs font-bold font-mono text-neutral-200">${pol.score}/100</span>
                </div>
                <div class="text-xs text-neutral-400 font-sans space-y-0.5">
                    ${pol.details.map(d => `<div>• ${d}</div>`).join('')}
                </div>
            `;
            breakdown.appendChild(div);
        });

        // Set symbol for other tabs
        document.getElementById('live-symbol-input').value = ev.symbol;
        document.getElementById('bt-symbol').value = ev.symbol;
        document.getElementById('risk-symbol').value = ev.symbol;

    } catch (e) {
        console.error(e);
    }
}

function renderRadarChart(pillars, symbol) {
    const ctx = document.getElementById('radarChart').getContext('2d');
    if (radarChartInstance) radarChartInstance.destroy();

    const dataValues = [
        pillars.volume_momentum.score,
        pillars.sales_growth.score,
        pillars.ocf_quality.score,
        pillars.debt_solvency.score,
        pillars.pricing_power.score,
        pillars.skin_in_game.score,
    ];

    radarChartInstance = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Volume Growth', 'Sales CAGR', 'OCF Quality', 'Debt Health', 'Pricing Power', 'Skin in Game'],
            datasets: [
                {
                    label: symbol,
                    data: dataValues,
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    borderColor: '#FFFFFF',
                    borderWidth: 1.5,
                    pointBackgroundColor: '#FFFFFF'
                },
                {
                    label: '78% Benchmark',
                    data: [78, 78, 78, 78, 78, 78],
                    borderColor: '#525252',
                    borderWidth: 1,
                    borderDash: [3, 3],
                    pointRadius: 0,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    min: 0,
                    max: 100,
                    grid: { color: '#262626' },
                    angleLines: { color: '#262626' },
                    ticks: { display: false },
                    pointLabels: {
                        color: '#A3A3A3',
                        font: { size: 10, family: 'Inter' }
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#A3A3A3', font: { family: 'Inter', size: 10 } }
                }
            }
        }
    });
}

// ==================== TAB 3: LIVE MARKET TECHNICAL TERMINAL ====================
function setChartPeriod(period) {
    currentChartPeriod = period;
    const periods = ['1mo', '3mo', '6mo', '1y', '2y'];
    periods.forEach(p => {
        const btn = document.getElementById(`btn-period-${p}`);
        if (btn) {
            if (p === period) {
                btn.className = 'chart-period-btn px-2.5 py-1 rounded bg-neutral-800 text-white font-bold transition';
            } else {
                btn.className = 'chart-period-btn px-2.5 py-1 rounded hover:text-white text-neutral-400 transition';
            }
        }
    });
    const sym = document.getElementById('live-symbol-input').value || currentChartSymbol;
    loadLiveChart(sym, period);
}

async function loadLiveChart(symbol, period = '1y') {
    if (!symbol) return;
    const cleanSym = symbol.trim().toUpperCase();
    currentChartSymbol = cleanSym;

    try {
        const res = await fetch(`/api/candles/${encodeURIComponent(cleanSym)}?period=${period}`);
        if (!res.ok) throw new Error('Failed to load live candlestick data');
        const data = await res.json();

        // Update live indicator badges
        document.getElementById('live-indicator-price').innerText = `${data.currency} ${parseFloat(data.current_price).toFixed(2)}`;
        document.getElementById('live-indicator-rsi').innerHTML = `<span class="${data.current_rsi >= 70 ? 'text-amber-400' : (data.current_rsi <= 30 ? 'text-emerald-400' : 'text-white')}">${data.current_rsi}</span> <span class="text-xs text-neutral-500 font-normal">(${data.current_rsi >= 70 ? 'Overbought' : (data.current_rsi <= 30 ? 'Oversold' : 'Neutral')})</span>`;
        document.getElementById('live-indicator-sma50').innerHTML = `${data.current_sma50 ? data.currency + ' ' + data.current_sma50 : 'N/A'} <span class="text-xs ${data.is_above_50dma ? 'text-emerald-400' : 'text-neutral-500'} font-normal">(${data.is_above_50dma ? 'Bullish' : 'Bearish'})</span>`;
        document.getElementById('live-indicator-sma200').innerHTML = `${data.current_sma200 ? data.currency + ' ' + data.current_sma200 : 'N/A'} <span class="text-xs ${data.is_above_200dma ? 'text-emerald-400' : 'text-neutral-500'} font-normal">(${data.is_above_200dma ? 'Bullish' : 'Bearish'})</span>`;

        // Build Candlestick Trace
        const candleTrace = {
            x: data.dates,
            open: data.open,
            high: data.high,
            low: data.low,
            close: data.close,
            type: 'candlestick',
            name: cleanSym,
            increasing: { line: { color: '#22C55E', width: 1 }, fillcolor: '#22C55E' },
            decreasing: { line: { color: '#EF4444', width: 1 }, fillcolor: '#EF4444' },
            yaxis: 'y1'
        };

        // Moving Average Traces
        const sma20Trace = {
            x: data.dates,
            y: data.sma20,
            type: 'scatter',
            mode: 'lines',
            name: '20 EMA',
            line: { color: '#38BDF8', width: 1.2 },
            yaxis: 'y1'
        };

        const sma50Trace = {
            x: data.dates,
            y: data.sma50,
            type: 'scatter',
            mode: 'lines',
            name: '50 SMA',
            line: { color: '#F59E0B', width: 1.2 },
            yaxis: 'y1'
        };

        const sma200Trace = {
            x: data.dates,
            y: data.sma200,
            type: 'scatter',
            mode: 'lines',
            name: '200 SMA',
            line: { color: '#A855F7', width: 1.2 },
            yaxis: 'y1'
        };

        // Volume Bar Colors (green if close >= open, red otherwise)
        const volumeColors = data.close.map((c, idx) => c >= data.open[idx] ? '#22C55E' : '#EF4444');
        const volumeTrace = {
            x: data.dates,
            y: data.volume,
            type: 'bar',
            name: 'Volume',
            marker: { color: volumeColors, opacity: 0.5 },
            yaxis: 'y2'
        };

        // RSI Trace
        const rsiTrace = {
            x: data.dates,
            y: data.rsi,
            type: 'scatter',
            mode: 'lines',
            name: 'RSI (14)',
            line: { color: '#FFFFFF', width: 1.2 },
            yaxis: 'y3'
        };

        const rsiUpper = {
            x: [data.dates[0], data.dates[data.dates.length - 1]],
            y: [70, 70],
            type: 'scatter',
            mode: 'lines',
            name: 'Overbought (70)',
            line: { color: '#737373', width: 1, dash: 'dot' },
            hoverinfo: 'none',
            yaxis: 'y3'
        };

        const rsiLower = {
            x: [data.dates[0], data.dates[data.dates.length - 1]],
            y: [30, 30],
            type: 'scatter',
            mode: 'lines',
            name: 'Oversold (30)',
            line: { color: '#737373', width: 1, dash: 'dot' },
            hoverinfo: 'none',
            yaxis: 'y3'
        };

        const traces = [candleTrace, sma20Trace, sma50Trace, sma200Trace, volumeTrace, rsiTrace, rsiUpper, rsiLower];

        const layout = {
            paper_bgcolor: '#121212',
            plot_bgcolor: '#121212',
            margin: { l: 50, r: 20, t: 30, b: 30 },
            dragmode: 'zoom',
            showlegend: true,
            legend: {
                orientation: 'h',
                x: 0,
                y: 1.08,
                font: { color: '#A3A3A3', size: 10, family: 'Inter' }
            },
            xaxis: {
                rangeslider: { visible: false },
                gridcolor: '#262626',
                tickfont: { color: '#737373', size: 10, family: 'JetBrains Mono' },
                linecolor: '#262626'
            },
            yaxis: {
                domain: [0.38, 1.0],
                gridcolor: '#262626',
                tickfont: { color: '#737373', size: 10, family: 'JetBrains Mono' },
                linecolor: '#262626',
                title: { text: `Price (${data.currency})`, font: { color: '#737373', size: 10 } }
            },
            yaxis2: {
                domain: [0.20, 0.35],
                gridcolor: '#262626',
                tickfont: { color: '#737373', size: 9, family: 'JetBrains Mono' },
                linecolor: '#262626',
                title: { text: 'Vol', font: { color: '#737373', size: 10 } },
                showgrid: false
            },
            yaxis3: {
                domain: [0.0, 0.17],
                range: [0, 100],
                gridcolor: '#262626',
                tickfont: { color: '#737373', size: 9, family: 'JetBrains Mono' },
                linecolor: '#262626',
                title: { text: 'RSI', font: { color: '#737373', size: 10 } },
                tickvals: [30, 70]
            }
        };

        const config = {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['lasso2d', 'select2d', 'autoScale2d']
        };

        Plotly.newPlot('live_candlestick_chart', traces, layout, config);

    } catch (e) {
        console.error(e);
        document.getElementById('live_candlestick_chart').innerHTML = `<div class="p-8 text-center text-neutral-400 font-mono text-xs">Error loading live market candles for ${cleanSym}: ${e.message}</div>`;
    }
}

// ==================== TAB 4: HISTORICAL BACKTESTER ====================
async function runBacktest() {
    const symbol = document.getElementById('bt-symbol').value || 'TCS.NS';
    const period = document.getElementById('bt-period').value || '2y';
    const capital = parseFloat(document.getElementById('bt-capital').value) || 100000;

    try {
        const res = await fetch(`/api/backtest?symbol=${encodeURIComponent(symbol)}&period=${period}&capital=${capital}`);
        if (!res.ok) throw new Error('Backtest failed');
        const data = await res.json();

        // Update KPI Metrics
        document.getElementById('bt-metric-return').innerText = `${data.stock_total_return}%`;
        document.getElementById('bt-metric-cagr').innerText = `${data.stock_cagr}%`;
        document.getElementById('bt-metric-sharpe').innerText = `${data.sharpe_ratio}`;
        document.getElementById('bt-metric-dd').innerText = `${data.max_drawdown_stock}%`;
        document.getElementById('bt-metric-alpha').innerText = `${data.alpha}%`;

        renderEquityChart(data.timeseries, symbol, data.benchmark_symbol);

    } catch (e) {
        console.error(e);
    }
}

function renderEquityChart(timeseries, symbol, benchmark) {
    const ctx = document.getElementById('equityChart').getContext('2d');
    if (equityChartInstance) equityChartInstance.destroy();

    const labels = timeseries.map(t => t.date);
    const stockValues = timeseries.map(t => t.stock_value);
    const bmValues = timeseries.map(t => t.benchmark_value);

    equityChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: `${symbol} Strategy`,
                    data: stockValues,
                    borderColor: '#FFFFFF',
                    borderWidth: 1.8,
                    fill: false,
                    pointRadius: 0
                },
                {
                    label: `Benchmark (${benchmark})`,
                    data: bmValues,
                    borderColor: '#525252',
                    borderWidth: 1.2,
                    borderDash: [3, 3],
                    fill: false,
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: { color: '#262626' },
                    ticks: { color: '#737373', maxTicksLimit: 8, font: { family: 'JetBrains Mono', size: 10 } }
                },
                y: {
                    grid: { color: '#262626' },
                    ticks: { color: '#737373', font: { family: 'JetBrains Mono', size: 10 } }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: { color: '#A3A3A3', font: { family: 'Inter', size: 11 } }
                }
            }
        }
    });
}

// ==================== TAB 5: POSITION SIZING & RISK ====================
async function calculateRiskPlan() {
    const symbol = document.getElementById('risk-symbol').value || 'RELIANCE.NS';
    const capital = parseFloat(document.getElementById('risk-capital').value) || 100000;
    const riskPct = parseFloat(document.getElementById('risk-pct').value) || 1.5;

    try {
        const res = await fetch(`/api/position-size?symbol=${encodeURIComponent(symbol)}&portfolio_size=${capital}&risk_pct=${riskPct}`);
        if (!res.ok) throw new Error('Risk plan failed');
        const plan = await res.json();

        const grid = document.getElementById('risk-results-grid');
        grid.innerHTML = `
            <div class="bg-[#121212] border border-[#262626] rounded-lg p-4 space-y-2">
                <div class="text-[11px] uppercase font-mono text-neutral-400">1. Position Sizing & Entry</div>
                <div class="text-xl font-bold font-mono text-white">${plan.currency} ${parseFloat(plan.current_price).toFixed(2)}</div>
                <div class="text-[11px] text-neutral-500">Market Price</div>
                <div class="pt-2 border-t border-[#262626] space-y-1 font-mono text-xs">
                    <div class="flex justify-between text-neutral-400"><span>Quantity:</span><b class="text-white">${plan.recommended_shares} Shares</b></div>
                    <div class="flex justify-between text-neutral-400"><span>Allocation:</span><b class="text-white">${plan.currency} ${plan.total_investment.toLocaleString()}</b></div>
                    <div class="flex justify-between text-neutral-400"><span>Portfolio Weight:</span><b class="text-white">${plan.portfolio_weight_pct}%</b></div>
                </div>
            </div>

            <div class="bg-[#121212] border border-[#262626] rounded-lg p-4 space-y-2">
                <div class="text-[11px] uppercase font-mono text-neutral-400">2. Downside Risk Shield</div>
                <div class="text-xl font-bold font-mono text-white">${plan.currency} ${parseFloat(plan.stop_loss).toFixed(2)}</div>
                <div class="text-[11px] text-neutral-500">2.0x ATR Stop Loss (${plan.stop_loss_pct}%)</div>
                <div class="pt-2 border-t border-[#262626] space-y-1 font-mono text-xs">
                    <div class="flex justify-between text-neutral-400"><span>Risk Capital:</span><b class="text-white">${plan.currency} ${plan.max_risk_capital.toLocaleString()}</b></div>
                    <div class="flex justify-between text-neutral-400"><span>Risk Envelope:</span><b class="text-white">Capped at ${riskPct}%</b></div>
                    <div class="flex justify-between text-neutral-400"><span>14-ATR Volatility:</span><b class="text-neutral-300">${plan.atr_14}</b></div>
                </div>
            </div>

            <div class="bg-[#121212] border border-[#262626] rounded-lg p-4 space-y-2">
                <div class="text-[11px] uppercase font-mono text-neutral-400">3. Asymmetric Profit Targets</div>
                <div class="text-xl font-bold font-mono text-white">${plan.currency} ${parseFloat(plan.target_2).toFixed(2)}</div>
                <div class="text-[11px] text-neutral-500">Target 2 (+${plan.target_2_upside_pct}%)</div>
                <div class="pt-2 border-t border-[#262626] space-y-1 font-mono text-xs">
                    <div class="flex justify-between text-neutral-400"><span>Target 1 (1:2 R:R):</span><b class="text-white">${plan.currency} ${plan.target_1} (+${plan.target_1_upside_pct}%)</b></div>
                    <div class="flex justify-between text-neutral-400"><span>Target 2 Gain:</span><b class="text-white">${plan.currency} ${plan.potential_gain_t2.toLocaleString()}</b></div>
                    <div class="flex justify-between text-neutral-400"><span>R:R Ratio:</span><b class="text-neutral-300">${plan.risk_reward_ratio}</b></div>
                </div>
            </div>
        `;

    } catch (e) {
        console.error(e);
    }
}

// ==================== LIVE INSTANT SEARCH AUTOCOMPLETE ====================
const LOCAL_CATALOG = [
    { symbol: 'RELIANCE.NS', name: 'Reliance Industries', sector: 'Energy / Telecom' },
    { symbol: 'TCS.NS', name: 'Tata Consultancy Services', sector: 'Information Technology' },
    { symbol: 'HDFCBANK.NS', name: 'HDFC Bank', sector: 'Financials / Banking' },
    { symbol: 'ICICIBANK.NS', name: 'ICICI Bank', sector: 'Financials / Banking' },
    { symbol: 'BHARTIARTL.NS', name: 'Bharti Airtel', sector: 'Telecommunications' },
    { symbol: 'INFY.NS', name: 'Infosys', sector: 'Information Technology' },
    { symbol: 'ITC.NS', name: 'ITC Limited', sector: 'Consumer FMCG' },
    { symbol: 'HINDUNILVR.NS', name: 'Hindustan Unilever', sector: 'Consumer FMCG' },
    { symbol: 'LT.NS', name: 'Larsen & Toubro', sector: 'Engineering & Capital Goods' },
    { symbol: 'SBIN.NS', name: 'State Bank of India', sector: 'Financials / PSU Bank' },
    { symbol: 'BAJFINANCE.NS', name: 'Bajaj Finance', sector: 'Financial Services' },
    { symbol: 'HCLTECH.NS', name: 'HCL Technologies', sector: 'Information Technology' },
    { symbol: 'MARUTI.NS', name: 'Maruti Suzuki', sector: 'Automobiles' },
    { symbol: 'SUNPHARMA.NS', name: 'Sun Pharmaceutical', sector: 'Healthcare / Pharma' },
    { symbol: 'TATACONSUM.NS', name: 'Tata Consumer Products', sector: 'Consumer FMCG' },
    { symbol: 'TATASTEEL.NS', name: 'Tata Steel', sector: 'Metals & Mining' },
    { symbol: 'TATAPOWER.NS', name: 'Tata Power', sector: 'Utilities / Power' },
    { symbol: 'TATAELXSI.NS', name: 'Tata Elxsi', sector: 'Information Technology' },
    { symbol: 'TITAN.NS', name: 'Titan Company', sector: 'Consumer Discretionary' },
    { symbol: 'M&M.NS', name: 'Mahindra & Mahindra', sector: 'Automobiles' },
    { symbol: 'BAJAJ-AUTO.NS', name: 'Bajaj Auto', sector: 'Automobiles' },
    { symbol: 'WIPRO.NS', name: 'Wipro', sector: 'Information Technology' },
    { symbol: 'ASIANPAINT.NS', name: 'Asian Paints', sector: 'Consumer Paints' },
    { symbol: 'HINDALCO.NS', name: 'Hindalco Industries', sector: 'Metals / Aluminium' },
    { symbol: 'CIPLA.NS', name: 'Cipla', sector: 'Healthcare / Pharma' },
    { symbol: 'DRREDDY.NS', name: 'Dr. Reddy Laboratories', sector: 'Healthcare / Pharma' },
    { symbol: 'PERSISTENT.NS', name: 'Persistent Systems', sector: 'Information Technology' },
    { symbol: 'HAL.NS', name: 'Hindustan Aeronautics', sector: 'Defense & Aerospace' },
    { symbol: 'BEL.NS', name: 'Bharat Electronics', sector: 'Defense & Aerospace' },
    { symbol: 'TRENT.NS', name: 'Trent Limited', sector: 'Retail / Consumer' },
    { symbol: 'ZOMATO.NS', name: 'Zomato Limited', sector: 'Internet / Food Tech' },
    { symbol: 'GOLDBEES.NS', name: 'Nippon Gold ETF', sector: 'Precious Metals (Gold)' },
    { symbol: 'SILVERBEES.NS', name: 'Nippon Silver ETF', sector: 'Precious Metals (Silver)' },
    { symbol: 'COALINDIA.NS', name: 'Coal India', sector: 'Energy / Mining' },
    { symbol: 'ONGC.NS', name: 'Oil & Natural Gas Corp', sector: 'Energy / Oil & Gas' },
    { symbol: 'NTPC.NS', name: 'NTPC Limited', sector: 'Utilities / Power' },
    { symbol: 'POWERGRID.NS', name: 'Power Grid Corporation', sector: 'Utilities / Power' }
];

function initSearchAutocomplete() {
    const input = document.getElementById('global-ticker-search');
    const dropdown = document.getElementById('search-suggestions');
    if (!input || !dropdown) return;

    input.addEventListener('input', (e) => {
        const val = e.target.value.trim().toLowerCase();
        selectedSuggestionIndex = -1;

        if (val.length < 1) {
            dropdown.innerHTML = '';
            dropdown.classList.add('hidden');
            return;
        }

        // 1. Instant 0ms local catalog match
        const localMatches = LOCAL_CATALOG.filter(s => 
            s.symbol.toLowerCase().includes(val) || 
            s.name.toLowerCase().includes(val) || 
            s.sector.toLowerCase().includes(val)
        ).slice(0, 8);

        if (localMatches.length > 0) {
            currentSuggestions = localMatches;
            renderSearchSuggestions(currentSuggestions);
        }

        // 2. Query backend for deep index / custom tickers with slight debounce
        clearTimeout(searchDebounceTimer);
        searchDebounceTimer = setTimeout(async () => {
            try {
                const res = await fetch(`/api/search?q=${encodeURIComponent(val)}`);
                if (!res.ok) return;
                const data = await res.json();
                if (data.results && data.results.length > 0) {
                    currentSuggestions = data.results;
                    renderSearchSuggestions(currentSuggestions);
                }
            } catch (err) {
                // Keep local suggestions
            }
        }, 120);
    });

    // Close dropdown on click outside
    document.addEventListener('click', (e) => {
        if (!input.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.classList.add('hidden');
        }
    });

    input.addEventListener('focus', () => {
        if (input.value.trim().length >= 1 && currentSuggestions.length > 0) {
            dropdown.classList.remove('hidden');
        }
    });
}

function renderSearchSuggestions(results) {
    const dropdown = document.getElementById('search-suggestions');
    if (!dropdown) return;

    if (!results || results.length === 0) {
        dropdown.innerHTML = '<div class="p-3 text-xs text-neutral-500 font-mono">No matching securities found.</div>';
        dropdown.classList.remove('hidden');
        return;
    }

    dropdown.innerHTML = '';
    results.forEach((item, idx) => {
        const div = document.createElement('div');
        div.id = `suggestion-item-${idx}`;
        div.className = 'p-2.5 hover:bg-[#202020] cursor-pointer flex justify-between items-center transition';
        div.onmousedown = () => selectSuggestion(item.symbol);
        div.innerHTML = `
            <div>
                <div class="text-xs font-bold text-white font-mono">${item.symbol}</div>
                <div class="text-[11px] text-neutral-400 truncate max-w-[200px]">${item.name}</div>
            </div>
            <span class="text-[10px] px-1.5 py-0.5 rounded bg-neutral-800 text-neutral-300 font-mono">${item.sector.split('/')[0].trim()}</span>
        `;
        dropdown.appendChild(div);
    });
    dropdown.classList.remove('hidden');
}

function selectSuggestion(symbol) {
    const input = document.getElementById('global-ticker-search');
    const dropdown = document.getElementById('search-suggestions');
    if (input) input.value = symbol;
    if (dropdown) dropdown.classList.add('hidden');
    executeAudit(symbol);
    switchTab('tab-audit');
}

function handleSearchKeydown(e) {
    const dropdown = document.getElementById('search-suggestions');
    const input = document.getElementById('global-ticker-search');
    if (!dropdown || dropdown.classList.contains('hidden') || currentSuggestions.length === 0) {
        if (e.key === 'Enter') {
            executeAudit(input.value);
            switchTab('tab-audit');
        }
        return;
    }

    if (e.key === 'ArrowDown') {
        e.preventDefault();
        selectedSuggestionIndex = Math.min(selectedSuggestionIndex + 1, currentSuggestions.length - 1);
        highlightSuggestion(selectedSuggestionIndex);
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        selectedSuggestionIndex = Math.max(selectedSuggestionIndex - 1, 0);
        highlightSuggestion(selectedSuggestionIndex);
    } else if (e.key === 'Enter') {
        e.preventDefault();
        if (selectedSuggestionIndex >= 0 && selectedSuggestionIndex < currentSuggestions.length) {
            selectSuggestion(currentSuggestions[selectedSuggestionIndex].symbol);
        } else {
            selectSuggestion(input.value);
        }
    } else if (e.key === 'Escape') {
        dropdown.classList.add('hidden');
    }
}

function highlightSuggestion(index) {
    currentSuggestions.forEach((_, idx) => {
        const el = document.getElementById(`suggestion-item-${idx}`);
        if (el) {
            if (idx === index) {
                el.classList.add('bg-[#262626]');
            } else {
                el.classList.remove('bg-[#262626]');
            }
        }
    });
}
