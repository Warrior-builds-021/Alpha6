/**
 * ALPHA6 Enterprise Terminal Client JavaScript
 * Investo.in Dark Mode Aesthetic, Real-Time Market Analytics & Native Candlestick Terminal.
 */

let radarChartInstance = null;
let equityChartInstance = null;
let currentChartSymbol = 'RELIANCE.NS';
let currentChartPeriod = '1y';
let searchDebounceTimer = null;
let currentSuggestions = [];
let selectedSuggestionIndex = -1;

// Screener state for client-side filtering and sorting
let rawScreenerData = [];
let currentSortColumn = 'composite_score';
let currentSortAsc = false;
let currentFilterText = '';

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
    // 1. Start live market indices ticker
    fetchMarketIndices();
    setInterval(fetchMarketIndices, 30000); // 30s refresh

    // 2. Universe dropdown toggle
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

    // 3. Initialize Autocomplete Search with 0ms Catalog & ARIA
    initSearchAutocomplete();

    // 4. Initial load: Only execute the active Screener view!
    runScreener();

    // 5. Responsive window resize for Plotly candlestick terminal (Fixed DOM ID)
    window.addEventListener('resize', () => {
        const chartEl = document.getElementById('live_candlestick_chart');
        if (chartEl && window.Plotly && chartEl.data) {
            Plotly.Plots.resize(chartEl);
        }
    });
});

// ==================== LIVE MARKET INDICES TELEMETRY ====================
async function fetchMarketIndices() {
    try {
        const res = await fetch('/api/market-indices');
        if (!res.ok) return;
        const data = await res.json();
        if (!data.indices || data.indices.length === 0) return;

        data.indices.forEach(idx => {
            const isSensex = idx.symbol === '^BSESN';
            const priceEl = document.getElementById(isSensex ? 'sensex-price' : 'nifty-price');
            const changeEl = document.getElementById(isSensex ? 'sensex-change' : 'nifty-change');

            if (priceEl && changeEl) {
                priceEl.innerText = Number(idx.price).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
                const isPositive = idx.change >= 0;
                const sign = isPositive ? '+' : '';
                changeEl.innerText = `${sign}${idx.percent_change.toFixed(2)}%`;

                if (isPositive) {
                    changeEl.className = 'px-1.5 py-0.2 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-mono';
                } else {
                    changeEl.className = 'px-1.5 py-0.2 rounded text-[10px] font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30 font-mono';
                }
            }
        });
    } catch (e) {
        console.warn('Market indices fetch note:', e);
    }
}

// ==================== TAB SWITCHING (LAZY LOADING & RESIZE FIX) ====================
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

    // Lazy load or resize each module on activation
    if (tabId === 'tab-audit') {
        if (!tabLoaded['tab-audit']) {
            tabLoaded['tab-audit'] = true;
            executeAudit(currentChartSymbol || 'RELIANCE.NS');
        }
    } else if (tabId === 'tab-chart') {
        if (!tabLoaded['tab-chart']) {
            tabLoaded['tab-chart'] = true;
            const sym = document.getElementById('live-symbol-input')?.value || currentChartSymbol;
            loadLiveChart(sym, currentChartPeriod);
        } else {
            // Fix Plotly canvas resize on hidden tab reactivation
            setTimeout(() => {
                const chartEl = document.getElementById('live_candlestick_chart');
                if (chartEl && window.Plotly && chartEl.data) {
                    Plotly.Plots.resize(chartEl);
                }
            }, 50);
        }
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
    tbody.innerHTML = `<tr><td colspan="13" class="p-8 text-center text-purple-300 font-mono">Running quantitative 6-pillar institutional audit...</td></tr>`;

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
        rawScreenerData = data.results || [];

        // Populate KPI Cards
        const total = data.total_scanned || rawScreenerData.length;
        const passed = data.high_conviction_count || 0;
        const passRate = total > 0 ? ((passed / total) * 100).toFixed(1) : 0;
        
        let avgScore = 0;
        let redFlagsTotal = 0;
        if (rawScreenerData.length > 0) {
            const sumScore = rawScreenerData.reduce((acc, curr) => acc + curr.composite_score, 0);
            avgScore = (sumScore / rawScreenerData.length).toFixed(1);
            redFlagsTotal = rawScreenerData.reduce((acc, curr) => acc + (curr.red_flag_count > 0 ? 1 : 0), 0);
        }

        document.getElementById('kpi-total').innerText = total;
        document.getElementById('kpi-passed').innerText = passed;
        document.getElementById('kpi-pass-rate').innerText = `${passRate}% of Universe`;
        document.getElementById('kpi-avg').innerText = `${avgScore}%`;
        document.getElementById('kpi-risk').innerText = redFlagsTotal;

        // Render Top Picks Cards
        renderTopPicks(data.high_conviction || rawScreenerData.filter(s => s.is_recommended));

        // Render Ranking Matrix Table
        renderScreenerTable();

    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="13" class="p-8 text-center text-rose-400 font-mono">
            <div class="flex flex-col items-center justify-center gap-2">
                <span>Error running screen: ${e.message}</span>
                <button onclick="runScreener()" class="mt-2 px-4 py-1.5 text-xs bg-purple-600/30 hover:bg-purple-600/50 border border-purple-500/40 text-purple-200 rounded-lg transition font-mono">↻ Retry Screen</button>
            </div>
        </td></tr>`;
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<span>Execute Screen</span>`;
    }
}

function renderTopPicks(picks) {
    const grid = document.getElementById('top-picks-grid');
    grid.innerHTML = '';

    if (!picks || picks.length === 0) {
        grid.innerHTML = `<div class="col-span-3 glass-card rounded-xl p-6 text-center text-neutral-400 font-mono text-xs">No stocks met the institutional conviction threshold in this scan.</div>`;
        return;
    }

    picks.slice(0, 6).forEach(s => {
        const card = document.createElement('div');
        card.className = 'glass-card rounded-xl p-4 cursor-pointer hover:border-purple-500/50 transition relative overflow-hidden group';
        card.onclick = () => {
            executeAudit(s.symbol);
            switchTab('tab-audit');
        };

        const peRatio = s.valuation?.pe_ratio ? `${s.valuation.pe_ratio}x` : 'N/A';
        card.innerHTML = `
            <div class="flex justify-between items-start">
                <div>
                    <span class="text-sm font-bold font-mono text-white group-hover:text-purple-300 transition">${s.symbol}</span>
                    <p class="text-xs text-neutral-400 truncate max-w-[180px]">${s.name}</p>
                </div>
                <span class="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">${s.signal}</span>
            </div>
            <div class="mt-3 flex items-baseline justify-between border-t border-white/5 pt-2 font-mono">
                <div>
                    <span class="text-[10px] text-neutral-500">PRICE:</span>
                    <span class="text-xs font-bold text-white ml-1">${s.currency} ${parseFloat(s.price).toFixed(2)}</span>
                </div>
                <div>
                    <span class="text-[10px] text-neutral-500">P/E:</span>
                    <span class="text-xs text-purple-300 ml-1 font-semibold">${peRatio}</span>
                </div>
                <div>
                    <span class="text-[10px] text-neutral-500">SCORE:</span>
                    <span class="text-sm font-extrabold text-white ml-1 bg-gradient-to-r from-purple-400 to-indigo-300 bg-clip-text text-transparent">${s.composite_score}%</span>
                </div>
            </div>
        `;
        grid.appendChild(card);
    });
}

function filterScreenerTable(text) {
    currentFilterText = (text || '').trim().toLowerCase();
    renderScreenerTable();
}

function sortScreenerTable(colKey) {
    if (currentSortColumn === colKey) {
        currentSortAsc = !currentSortAsc;
    } else {
        currentSortColumn = colKey;
        currentSortAsc = false; // default descending for metrics
    }
    renderScreenerTable();
}

function renderScreenerTable() {
    const tbody = document.getElementById('screener-tbody');
    const badge = document.getElementById('matrix-count-badge');
    if (!tbody) return;

    // Filter
    let filtered = rawScreenerData.filter(item => {
        if (!currentFilterText) return true;
        return (
            item.symbol.toLowerCase().includes(currentFilterText) ||
            item.name.toLowerCase().includes(currentFilterText) ||
            (item.sector && item.sector.toLowerCase().includes(currentFilterText))
        );
    });

    // Sort
    filtered.sort((a, b) => {
        let valA = a[currentSortColumn];
        let valB = b[currentSortColumn];

        if (typeof valA === 'string') valA = valA.toLowerCase();
        if (typeof valB === 'string') valB = valB.toLowerCase();
        if (valA == null) valA = 0;
        if (valB == null) valB = 0;

        if (valA < valB) return currentSortAsc ? -1 : 1;
        if (valA > valB) return currentSortAsc ? 1 : -1;
        return 0;
    });

    if (badge) {
        badge.innerText = `(${filtered.length} of ${rawScreenerData.length} shown)`;
    }

    // Update sort arrow icons
    const cols = ['symbol', 'name', 'price', 'composite_score', 'volume_score', 'sales_score', 'ocf_score', 'debt_score', 'pricing_score', 'skin_score', 'piotroski_f_score', 'altman_z_score'];
    cols.forEach(c => {
        const icon = document.getElementById(`sort-icon-${c}`);
        if (icon) {
            if (c === currentSortColumn) {
                icon.innerText = currentSortAsc ? '▲' : '▼';
                icon.className = 'text-purple-400 font-bold';
            } else {
                icon.innerText = '↕';
                icon.className = 'text-neutral-500 font-normal';
            }
        }
    });

    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="13" class="p-8 text-center text-neutral-500 font-mono">No securities match the search filter.</td></tr>`;
        return;
    }

    tbody.innerHTML = '';
    filtered.forEach(s => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-purple-950/20 cursor-pointer transition select-none';
        tr.onclick = () => {
            executeAudit(s.symbol);
            switchTab('tab-audit');
        };

        const signalBadgeClass = s.is_recommended
            ? 'px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
            : (s.red_flag_count > 0 
                ? 'px-2 py-0.5 rounded text-[10px] font-medium bg-rose-500/20 text-rose-400 border border-rose-500/30' 
                : 'px-2 py-0.5 rounded text-[10px] font-medium bg-neutral-800 text-neutral-400');

        tr.innerHTML = `
            <td class="p-3.5 font-bold text-white">${s.symbol}</td>
            <td class="p-3.5 text-neutral-300 font-sans truncate max-w-[160px]">${s.name}</td>
            <td class="p-3.5 text-white">${s.currency} ${parseFloat(s.price).toFixed(2)}</td>
            <td class="p-3.5 font-extrabold text-transparent bg-gradient-to-r from-purple-300 to-indigo-200 bg-clip-text">${s.composite_score}%</td>
            <td class="p-3.5 ${s.volume_score >= 70 ? 'text-emerald-400' : 'text-neutral-400'}">${s.volume_score}</td>
            <td class="p-3.5 ${s.sales_score >= 70 ? 'text-emerald-400' : 'text-neutral-400'}">${s.sales_score}</td>
            <td class="p-3.5 ${s.ocf_score >= 70 ? 'text-emerald-400' : 'text-neutral-400'}">${s.ocf_score}</td>
            <td class="p-3.5 ${s.debt_score >= 70 ? 'text-emerald-400' : 'text-neutral-400'}">${s.debt_score}</td>
            <td class="p-3.5 ${s.pricing_score >= 70 ? 'text-emerald-400' : 'text-neutral-400'}">${s.pricing_score}</td>
            <td class="p-3.5 ${s.skin_score >= 70 ? 'text-emerald-400' : 'text-neutral-400'}">${s.skin_score}</td>
            <td class="p-3.5">${s.piotroski_f_score}/9</td>
            <td class="p-3.5">${s.altman_z_score}</td>
            <td class="p-3.5"><span class="${signalBadgeClass}">${s.signal}</span></td>
        `;
        tbody.appendChild(tr);
    });
}

// ==================== TAB 2: FORENSIC 6-PILLAR AUDIT ====================
let cachedPiotroskiDetails = [];

async function executeAudit(symbol) {
    if (!symbol) return;
    try {
        const res = await fetch(`/api/audit/${encodeURIComponent(symbol)}`);
        if (!res.ok) throw new Error('Symbol audit failed');
        const data = await res.json();
        const ev = data.evaluation;
        const p = ev.pillars;

        currentChartSymbol = ev.symbol;

        // 1. Populate Header
        document.getElementById('audit-symbol').innerText = ev.symbol;
        document.getElementById('audit-company-name').innerText = `${ev.short_name} • ${ev.sector} • ${ev.currency} ${parseFloat(ev.current_price).toFixed(2)}`;
        document.getElementById('audit-composite-score').innerText = `${ev.composite_score}%`;

        const badge = document.getElementById('audit-signal-badge');
        badge.innerText = ev.signal;
        badge.className = ev.is_recommended 
            ? 'text-xs px-2.5 py-0.5 rounded font-mono font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
            : (ev.red_flags.length > 0 
                ? 'text-xs px-2.5 py-0.5 rounded font-mono font-medium bg-rose-500/20 text-rose-400 border border-rose-500/30' 
                : 'text-xs px-2.5 py-0.5 rounded font-mono font-medium bg-neutral-800 text-neutral-300 border border-neutral-700');

        document.getElementById('audit-piotroski').innerText = `${ev.piotroski_f_score} / 9`;
        document.getElementById('audit-altman').innerText = `${ev.altman_z_score} (${ev.altman_status.split(' ')[0]})`;

        // 2. Populate Valuation Multiples Card
        const val = ev.valuation || {};
        const peVal = val.pe_ratio != null ? `${val.pe_ratio}x` : 'N/A';
        const pbVal = val.pb_ratio != null ? `${val.pb_ratio}x` : 'N/A';
        const pegVal = val.peg_ratio != null ? `${val.peg_ratio}x` : 'N/A';
        const evVal = val.ev_ebitda != null ? `${val.ev_ebitda}x` : 'N/A';

        document.getElementById('val-pe-val').innerText = peVal;
        document.getElementById('val-pb-val').innerText = pbVal;
        document.getElementById('val-peg-val').innerText = pegVal;
        document.getElementById('val-ev-val').innerText = evVal;

        // Contextual Tags for Valuation
        const setValTag = (id, valNum, thresholds, labels) => {
            const el = document.getElementById(id);
            if (!el) return;
            if (valNum == null || isNaN(valNum)) {
                el.innerText = 'Fair / Standard';
                el.className = 'text-[10px] mt-1 px-1.5 py-0.5 rounded inline-block font-semibold bg-neutral-800 text-neutral-400';
                return;
            }
            if (valNum <= thresholds[0]) {
                el.innerText = labels[0];
                el.className = 'text-[10px] mt-1 px-1.5 py-0.5 rounded inline-block font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30';
            } else if (valNum <= thresholds[1]) {
                el.innerText = labels[1];
                el.className = 'text-[10px] mt-1 px-1.5 py-0.5 rounded inline-block font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30';
            } else {
                el.innerText = labels[2];
                el.className = 'text-[10px] mt-1 px-1.5 py-0.5 rounded inline-block font-semibold bg-purple-500/20 text-purple-300 border border-purple-500/30';
            }
        };

        setValTag('val-pe-tag', val.pe_ratio, [22, 40], ['Value Multiple', 'Reasonable', 'Growth Premium']);
        setValTag('val-pb-tag', val.pb_ratio, [3.0, 7.0], ['Attractive Book', 'Standard Book', 'Asset-Light / High ROE']);
        setValTag('val-peg-tag', val.peg_ratio, [1.0, 1.5], ['Undervalued Growth', 'Fair Growth', 'High PEG']);
        setValTag('val-ev-tag', val.ev_ebitda, [14, 25], ['Sound Enterprise', 'Moderate Multiplier', 'Extended']);

        // 3. Piotroski Itemized Checklist Breakdown
        cachedPiotroskiDetails = ev.piotroski_details || [];
        renderPiotroskiDetails();

        // 4. Render Radar Chart with Investo.in Brand Colors
        renderRadarChart(p, ev.symbol);

        // 5. Render Pillar Breakdown Cards
        const breakdown = document.getElementById('audit-pillar-breakdown');
        breakdown.innerHTML = '';

        const pillarOrder = [
            { key: 'volume_momentum', title: '1. Volume & Momentum Growth (15%)' },
            { key: 'sales_growth', title: '2. Sales Revenue CAGR (20%)' },
            { key: 'ocf_quality', title: '3. Operating Cash Flow Quality (25%)' },
            { key: 'debt_solvency', title: '4. Debt & Solvency Health (15%)' },
            { key: 'pricing_power', title: '5. Pricing Power & Moat (15%)' },
            { key: 'skin_in_game', title: '6. Promoter / Insider Skin in Game (10%)' },
        ];

        if (ev.red_flags && ev.red_flags.length > 0) {
            const rfBox = document.createElement('div');
            rfBox.className = 'bg-rose-950/40 border-l-4 border-rose-500 p-3 rounded-lg text-xs text-rose-200 font-mono space-y-1 shadow-sm';
            rfBox.innerHTML = `<b>RISK SHIELD CAPITAL PRESERVATION WARNINGS:</b>` + ev.red_flags.map(f => `<div>• ${f}</div>`).join('');
            breakdown.appendChild(rfBox);
        }

        pillarOrder.forEach(item => {
            const pol = p[item.key];
            const div = document.createElement('div');
            div.className = 'bg-[#0B0F19]/80 border border-white/5 rounded-lg p-3 space-y-1.5 hover:border-purple-500/30 transition';
            
            const scoreColor = pol.score >= 78 ? 'text-emerald-400' : (pol.score >= 60 ? 'text-purple-300' : 'text-neutral-400');
            div.innerHTML = `
                <div class="flex justify-between items-center">
                    <span class="text-xs font-semibold text-white uppercase font-mono">${item.title}</span>
                    <span class="text-xs font-extrabold font-mono ${scoreColor}">${pol.score}/100</span>
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
        console.error('Audit execution error:', e);
    }
}

function togglePiotroskiDetails() {
    const list = document.getElementById('piotroski-details-list');
    const btn = document.getElementById('piotroski-toggle-btn');
    if (!list || !btn) return;

    if (list.classList.contains('hidden')) {
        list.classList.remove('hidden');
        btn.innerText = '[Collapse ▲]';
    } else {
        list.classList.add('hidden');
        btn.innerText = '[Details ▼]';
    }
}

function renderPiotroskiDetails() {
    const list = document.getElementById('piotroski-details-list');
    if (!list) return;
    list.innerHTML = '';

    if (!cachedPiotroskiDetails || cachedPiotroskiDetails.length === 0) {
        list.innerHTML = `<div class="text-neutral-500 text-[10px]">No criteria details available.</div>`;
        return;
    }

    cachedPiotroskiDetails.forEach(item => {
        const isPass = item.toLowerCase().includes('[pass]') || item.includes('Pass') || item.includes('✓');
        const div = document.createElement('div');
        div.className = 'flex items-center justify-between py-1 border-b border-white/5 text-[10px]';
        div.innerHTML = `
            <span class="text-neutral-300">${item.replace(/\[PASS\]|\[FAIL\]/g, '').trim()}</span>
            <span class="font-bold ${isPass ? 'text-emerald-400' : 'text-rose-400'}">${isPass ? 'PASS ✓' : 'FAIL ✗'}</span>
        `;
        list.appendChild(div);
    });
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
                    backgroundColor: 'rgba(105, 67, 255, 0.25)',
                    borderColor: '#6943FF',
                    borderWidth: 2,
                    pointBackgroundColor: '#BA1B9A',
                    pointBorderColor: '#FFFFFF',
                    pointBorderWidth: 1.5,
                    pointRadius: 4,
                    pointHoverRadius: 6
                },
                {
                    label: '78% Conviction Benchmark',
                    data: [78, 78, 78, 78, 78, 78],
                    borderColor: 'rgba(186, 27, 154, 0.5)',
                    borderWidth: 1.5,
                    borderDash: [4, 4],
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
                    grid: { color: 'rgba(105, 67, 255, 0.12)' },
                    angleLines: { color: 'rgba(105, 67, 255, 0.18)' },
                    ticks: { display: false },
                    pointLabels: {
                        color: '#CBD5E1',
                        font: { size: 10, family: 'Inter', weight: '500' }
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#94A3B8', font: { family: 'Inter', size: 10 } }
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
                btn.className = 'chart-period-btn px-2.5 py-1 rounded bg-[#6943FF] text-white font-bold transition';
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

        // Investo.in Branded Moving Average Traces
        const sma20Trace = {
            x: data.dates,
            y: data.sma20,
            type: 'scatter',
            mode: 'lines',
            name: '20 EMA (Purple)',
            line: { color: '#6943FF', width: 1.5 },
            yaxis: 'y1'
        };

        const sma50Trace = {
            x: data.dates,
            y: data.sma50,
            type: 'scatter',
            mode: 'lines',
            name: '50 SMA (Indigo)',
            line: { color: '#4556DA', width: 1.5 },
            yaxis: 'y1'
        };

        const sma200Trace = {
            x: data.dates,
            y: data.sma200,
            type: 'scatter',
            mode: 'lines',
            name: '200 SMA (Magenta)',
            line: { color: '#BA1B9A', width: 1.5 },
            yaxis: 'y1'
        };

        // Volume Bar Colors (green if close >= open, red otherwise)
        const volumeColors = data.close.map((c, idx) => c >= data.open[idx] ? 'rgba(34, 197, 94, 0.45)' : 'rgba(239, 68, 68, 0.45)');
        const volumeTrace = {
            x: data.dates,
            y: data.volume,
            type: 'bar',
            name: 'Volume',
            marker: { color: volumeColors },
            yaxis: 'y2'
        };

        // 14-Period RSI Trace
        const rsiTrace = {
            x: data.dates,
            y: data.rsi,
            type: 'scatter',
            mode: 'lines',
            name: 'RSI (14)',
            line: { color: '#A855F7', width: 1.4 },
            yaxis: 'y3'
        };

        const rsiUpper = {
            x: [data.dates[0], data.dates[data.dates.length - 1]],
            y: [70, 70],
            type: 'scatter',
            mode: 'lines',
            name: 'Overbought (70)',
            line: { color: 'rgba(244, 63, 94, 0.7)', width: 1, dash: 'dot' },
            hoverinfo: 'none',
            yaxis: 'y3'
        };

        const rsiLower = {
            x: [data.dates[0], data.dates[data.dates.length - 1]],
            y: [30, 30],
            type: 'scatter',
            mode: 'lines',
            name: 'Oversold (30)',
            line: { color: 'rgba(34, 197, 94, 0.7)', width: 1, dash: 'dot' },
            hoverinfo: 'none',
            yaxis: 'y3'
        };

        const traces = [candleTrace, sma20Trace, sma50Trace, sma200Trace, volumeTrace, rsiTrace, rsiUpper, rsiLower];

        // Obsidian Layout with Investo.in Dark Styling
        const layout = {
            paper_bgcolor: '#07080D',
            plot_bgcolor: '#07080D',
            margin: { l: 55, r: 25, t: 30, b: 30 },
            dragmode: 'zoom',
            showlegend: true,
            legend: {
                orientation: 'h',
                x: 0,
                y: 1.08,
                font: { color: '#CBD5E1', size: 10, family: 'Inter' }
            },
            xaxis: {
                rangeslider: { visible: false },
                gridcolor: 'rgba(105, 67, 255, 0.08)',
                tickfont: { color: '#64748B', size: 10, family: 'JetBrains Mono' },
                linecolor: 'rgba(105, 67, 255, 0.18)'
            },
            yaxis: {
                domain: [0.38, 1.0],
                gridcolor: 'rgba(105, 67, 255, 0.08)',
                tickfont: { color: '#64748B', size: 10, family: 'JetBrains Mono' },
                linecolor: 'rgba(105, 67, 255, 0.18)',
                title: { text: `Price (${data.currency})`, font: { color: '#94A3B8', size: 10 } }
            },
            yaxis2: {
                domain: [0.20, 0.35],
                gridcolor: 'rgba(105, 67, 255, 0.08)',
                tickfont: { color: '#64748B', size: 9, family: 'JetBrains Mono' },
                linecolor: 'rgba(105, 67, 255, 0.18)',
                title: { text: 'Vol', font: { color: '#94A3B8', size: 10 } },
                showgrid: false
            },
            yaxis3: {
                domain: [0.0, 0.16],
                range: [0, 100],
                gridcolor: 'rgba(105, 67, 255, 0.08)',
                tickfont: { color: '#64748B', size: 9, family: 'JetBrains Mono' },
                linecolor: 'rgba(105, 67, 255, 0.18)',
                title: { text: 'RSI', font: { color: '#94A3B8', size: 10 } }
            }
        };

        const config = {
            responsive: true,
            displayModeBar: false
        };

        Plotly.newPlot('live_candlestick_chart', traces, layout, config);

    } catch (e) {
        console.error('Candlestick load error:', e);
    }
}

// ==================== TAB 4: HISTORICAL BACKTESTER ====================
async function runBacktest() {
    const symbol = document.getElementById('bt-symbol').value.trim();
    const period = document.getElementById('bt-period').value;
    const capital = parseFloat(document.getElementById('bt-capital').value) || 100000.0;

    try {
        const res = await fetch(`/api/backtest?symbol=${encodeURIComponent(symbol)}&period=${period}&capital=${capital}`);
        if (!res.ok) throw new Error('Backtest execution failed');
        const data = await res.json();

        // Metrics populate
        const retColor = data.total_return_pct >= 0 ? 'text-emerald-400' : 'text-rose-400';
        const sign = data.total_return_pct >= 0 ? '+' : '';
        document.getElementById('bt-metric-return').innerHTML = `<span class="${retColor}">${sign}${data.total_return_pct.toFixed(2)}%</span>`;
        document.getElementById('bt-metric-cagr').innerText = `${data.cagr_pct.toFixed(2)}%`;
        document.getElementById('bt-metric-sharpe').innerText = data.sharpe_ratio.toFixed(2);
        document.getElementById('bt-metric-dd').innerText = `${data.max_drawdown_pct.toFixed(2)}%`;

        const alphaSign = data.alpha_vs_benchmark >= 0 ? '+' : '';
        const alphaColor = data.alpha_vs_benchmark >= 0 ? 'text-emerald-400' : 'text-rose-400';
        document.getElementById('bt-metric-alpha').innerHTML = `<span class="${alphaColor}">${alphaSign}${data.alpha_vs_benchmark.toFixed(2)}%</span>`;

        // Render Chart.js Equity Curve with Purple Brand Gradient
        const ctx = document.getElementById('equityChart').getContext('2d');
        if (equityChartInstance) equityChartInstance.destroy();

        const dates = data.timeseries.map(d => d.date);
        const stockVals = data.timeseries.map(d => d.stock_value);
        const benchVals = data.timeseries.map(d => d.benchmark_value);

        // Gradient Area Fill
        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'rgba(105, 67, 255, 0.35)');
        gradient.addColorStop(1, 'rgba(105, 67, 255, 0.0)');

        equityChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [
                    {
                        label: `${symbol} Portfolio`,
                        data: stockVals,
                        borderColor: '#6943FF',
                        borderWidth: 2,
                        backgroundColor: gradient,
                        fill: true,
                        tension: 0.1,
                        pointRadius: 0
                    },
                    {
                        label: 'Nifty 50 Benchmark',
                        data: benchVals,
                        borderColor: '#4556DA',
                        borderWidth: 1.5,
                        borderDash: [4, 4],
                        fill: false,
                        tension: 0.1,
                        pointRadius: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                scales: {
                    x: {
                        grid: { color: 'rgba(105, 67, 255, 0.08)' },
                        ticks: { color: '#64748B', font: { family: 'JetBrains Mono', size: 9 }, maxTicksLimit: 8 }
                    },
                    y: {
                        grid: { color: 'rgba(105, 67, 255, 0.08)' },
                        ticks: { color: '#64748B', font: { family: 'JetBrains Mono', size: 10 } }
                    }
                },
                plugins: {
                    legend: {
                        labels: { color: '#CBD5E1', font: { family: 'Inter', size: 11 } }
                    }
                }
            }
        });

    } catch (e) {
        console.error('Backtest error:', e);
    }
}

// ==================== TAB 5: POSITION SIZING & RISK SHIELD ====================
async function calculateRiskPlan() {
    const symbol = document.getElementById('risk-symbol').value.trim();
    const cap = parseFloat(document.getElementById('risk-capital').value) || 100000.0;
    const risk = parseFloat(document.getElementById('risk-pct').value) || 1.5;

    try {
        const res = await fetch(`/api/position-size?symbol=${encodeURIComponent(symbol)}&portfolio_size=${cap}&risk_pct=${risk}`);
        if (!res.ok) throw new Error('Position size calculation failed');
        const plan = await res.json();

        const grid = document.getElementById('risk-results-grid');
        grid.innerHTML = `
            <!-- Allocation Card -->
            <div class="glass-card rounded-xl p-4 space-y-3">
                <div class="flex justify-between items-center border-b border-white/5 pb-2">
                    <span class="text-xs font-bold font-mono text-white">POSITION ALLOCATION</span>
                    <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-[#6943FF]/20 text-purple-300 border border-[#6943FF]/30 font-mono">${plan.currency}</span>
                </div>
                <div class="space-y-2 font-mono text-xs">
                    <div class="flex justify-between text-neutral-400"><span>Target Entry:</span><b class="text-white">${plan.currency} ${plan.entry_price.toFixed(2)}</b></div>
                    <div class="flex justify-between text-neutral-400"><span>Order Quantity:</span><b class="text-emerald-400 font-extrabold text-sm">${plan.recommended_shares} Shares</b></div>
                    <div class="flex justify-between text-neutral-400"><span>Position Capital:</span><b class="text-white">${plan.currency} ${plan.total_investment.toLocaleString('en-IN', {minimumFractionDigits: 2})}</b></div>
                    <div class="flex justify-between text-neutral-400"><span>Portfolio Weight:</span><b class="text-purple-300 font-bold">${plan.portfolio_weight_pct}%</b></div>
                </div>
            </div>

            <!-- ATR Risk Boundaries -->
            <div class="glass-card rounded-xl p-4 space-y-3 border-rose-500/20">
                <div class="flex justify-between items-center border-b border-white/5 pb-2">
                    <span class="text-xs font-bold font-mono text-rose-300">DOWNSIDE PROTECTION</span>
                    <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30 font-mono">2.0x ATR</span>
                </div>
                <div class="space-y-2 font-mono text-xs">
                    <div class="flex justify-between text-neutral-400"><span>14-Period ATR:</span><b class="text-neutral-300">${plan.currency} ${plan.atr_value.toFixed(2)}</b></div>
                    <div class="flex justify-between text-neutral-400"><span>Strict Stop Loss:</span><b class="text-rose-400 font-extrabold">${plan.currency} ${plan.stop_loss.toFixed(2)}</b></div>
                    <div class="flex justify-between text-neutral-400"><span>Max Risk Amount:</span><b class="text-rose-300">${plan.currency} ${plan.risk_amount.toFixed(2)} (${plan.risk_pct}%)</b></div>
                    <div class="flex justify-between text-neutral-400"><span>Risk per Share:</span><b class="text-neutral-300">${plan.currency} ${plan.risk_per_share.toFixed(2)}</b></div>
                </div>
            </div>

            <!-- Asymmetric Profit Targets -->
            <div class="glass-card rounded-xl p-4 space-y-3 border-emerald-500/20">
                <div class="flex justify-between items-center border-b border-white/5 pb-2">
                    <span class="text-xs font-bold font-mono text-emerald-300">ASYMMETRIC TARGETS</span>
                    <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-mono">1:2 & 1:3.5 R:R</span>
                </div>
                <div class="space-y-2 font-mono text-xs">
                    <div class="flex justify-between text-neutral-400"><span>Target 1 (1:2 R:R):</span><b class="text-emerald-400 font-bold">${plan.currency} ${plan.target_1.toFixed(2)}</b></div>
                    <div class="flex justify-between text-neutral-400"><span>Target 2 (1:3.5 R:R):</span><b class="text-emerald-300 font-bold">${plan.currency} ${plan.target_2.toFixed(2)}</b></div>
                    <div class="flex justify-between text-neutral-400"><span>Upside Expectancy:</span><b class="text-emerald-400">+${((plan.target_1 - plan.entry_price) / plan.entry_price * 100).toFixed(1)}%</b></div>
                    <div class="flex justify-between text-neutral-400"><span>Risk/Reward Meter:</span><b class="text-purple-300">${plan.risk_reward_ratio}</b></div>
                </div>
            </div>
        `;

    } catch (e) {
        console.error('Risk plan error:', e);
    }
}

// ==================== 0MS INSTANT SEARCH AUTOCOMPLETE (150+ UNIVERSE) ====================
const LOCAL_CATALOG = [
    // NIFTY 50 (50 Blue-Chips)
    { symbol: 'RELIANCE.NS', name: 'Reliance Industries', sector: 'Energy / Retail / Telecom' },
    { symbol: 'TCS.NS', name: 'Tata Consultancy Services', sector: 'Information Technology' },
    { symbol: 'HDFCBANK.NS', name: 'HDFC Bank', sector: 'Financials / Banking' },
    { symbol: 'ICICIBANK.NS', name: 'ICICI Bank', sector: 'Financials / Banking' },
    { symbol: 'BHARTIARTL.NS', name: 'Bharti Airtel', sector: 'Telecommunications' },
    { symbol: 'INFY.NS', name: 'Infosys', sector: 'Information Technology' },
    { symbol: 'ITC.NS', name: 'ITC Limited', sector: 'Consumer FMCG' },
    { symbol: 'HINDUNILVR.NS', name: 'Hindustan Unilever', sector: 'Consumer FMCG' },
    { symbol: 'LT.NS', name: 'Larsen & Toubro', sector: 'Engineering & Capital Goods' },
    { symbol: 'SBIN.NS', name: 'State Bank of India', sector: 'Financials / PSU Bank' },
    { symbol: 'BAJFINANCE.NS', name: 'Bajaj Finance', sector: 'Financial Services (NBFC)' },
    { symbol: 'HCLTECH.NS', name: 'HCL Technologies', sector: 'Information Technology' },
    { symbol: 'MARUTI.NS', name: 'Maruti Suzuki', sector: 'Automobiles' },
    { symbol: 'SUNPHARMA.NS', name: 'Sun Pharmaceutical', sector: 'Healthcare / Pharma' },
    { symbol: 'ADANIENT.NS', name: 'Adani Enterprises', sector: 'Metals & Mining / Energy' },
    { symbol: 'TATACONSUM.NS', name: 'Tata Consumer Products', sector: 'Consumer FMCG' },
    { symbol: 'AXISBANK.NS', name: 'Axis Bank', sector: 'Financials / Banking' },
    { symbol: 'NTPC.NS', name: 'NTPC Limited', sector: 'Utilities / Power' },
    { symbol: 'ONGC.NS', name: 'Oil & Natural Gas Corp', sector: 'Energy / Oil & Gas' },
    { symbol: 'TITAN.NS', name: 'Titan Company', sector: 'Consumer Discretionary' },
    { symbol: 'KOTAKBANK.NS', name: 'Kotak Mahindra Bank', sector: 'Financials / Banking' },
    { symbol: 'M&M.NS', name: 'Mahindra & Mahindra', sector: 'Automobiles' },
    { symbol: 'ADANIPORTS.NS', name: 'Adani Ports & SEZ', sector: 'Infrastructure / Ports' },
    { symbol: 'COALINDIA.NS', name: 'Coal India', sector: 'Energy / Mining' },
    { symbol: 'BAJAJ-AUTO.NS', name: 'Bajaj Auto', sector: 'Automobiles' },
    { symbol: 'ULTRACEMCO.NS', name: 'UltraTech Cement', sector: 'Materials / Cement' },
    { symbol: 'POWERGRID.NS', name: 'Power Grid Corporation', sector: 'Utilities / Power' },
    { symbol: 'WIPRO.NS', name: 'Wipro', sector: 'Information Technology' },
    { symbol: 'ASIANPAINT.NS', name: 'Asian Paints', sector: 'Consumer Paints' },
    { symbol: 'NESTLEIND.NS', name: 'Nestle India', sector: 'Consumer FMCG' },
    { symbol: 'JSWSTEEL.NS', name: 'JSW Steel', sector: 'Metals & Mining' },
    { symbol: 'TATASTEEL.NS', name: 'Tata Steel', sector: 'Metals & Mining' },
    { symbol: 'GRASIM.NS', name: 'Grasim Industries', sector: 'Materials / Diversified' },
    { symbol: 'TECHM.NS', name: 'Tech Mahindra', sector: 'Information Technology' },
    { symbol: 'HINDALCO.NS', name: 'Hindalco Industries', sector: 'Metals / Aluminium' },
    { symbol: 'CIPLA.NS', name: 'Cipla', sector: 'Healthcare / Pharma' },
    { symbol: 'EICHERMOT.NS', name: 'Eicher Motors', sector: 'Automobiles' },
    { symbol: 'SBILIFE.NS', name: 'SBI Life Insurance', sector: 'Financials / Insurance' },
    { symbol: 'DRREDDY.NS', name: "Dr. Reddy's Laboratories", sector: 'Healthcare / Pharma' },
    { symbol: 'BRITANNIA.NS', name: 'Britannia Industries', sector: 'Consumer FMCG' },
    { symbol: 'PERSISTENT.NS', name: 'Persistent Systems', sector: 'Information Technology' },
    { symbol: 'HEROMOTOCO.NS', name: 'Hero MotoCorp', sector: 'Automobiles' },
    { symbol: 'APOLLOHOSP.NS', name: 'Apollo Hospitals', sector: 'Healthcare / Hospitals' },
    { symbol: 'BPCL.NS', name: 'Bharat Petroleum Corp', sector: 'Energy / Refining' },
    { symbol: 'SHRIRAMFIN.NS', name: 'Shriram Finance', sector: 'Financial Services (NBFC)' },
    { symbol: 'BEL.NS', name: 'Bharat Electronics', sector: 'Defense & Aerospace' },
    { symbol: 'TRENT.NS', name: 'Trent Limited', sector: 'Retail / Consumer' },
    { symbol: 'DIVISLAB.NS', name: "Divi's Laboratories", sector: 'Healthcare / Pharma' },
    { symbol: 'INDUSINDBK.NS', name: 'IndusInd Bank', sector: 'Financials / Banking' },
    { symbol: 'BAJAJFINSV.NS', name: 'Bajaj Finserv', sector: 'Financial Services' },

    // NIFTY NEXT 50 (50 Large / Midcaps)
    { symbol: 'HAL.NS', name: 'Hindustan Aeronautics', sector: 'Defense & Aerospace' },
    { symbol: 'VARUN.NS', name: 'Varun Beverages', sector: 'Consumer FMCG' },
    { symbol: 'ZOMATO.NS', name: 'Zomato Limited', sector: 'Internet / Food Tech' },
    { symbol: 'JIOFIN.NS', name: 'Jio Financial Services', sector: 'Financial Services' },
    { symbol: 'CHOLAFIN.NS', name: 'Cholamandalam Investment', sector: 'Financial Services' },
    { symbol: 'DLF.NS', name: 'DLF Limited', sector: 'Real Estate' },
    { symbol: 'GAIL.NS', name: 'GAIL India', sector: 'Energy / Natural Gas' },
    { symbol: 'GODREJCP.NS', name: 'Godrej Consumer Products', sector: 'Consumer FMCG' },
    { symbol: 'INDIGO.NS', name: 'InterGlobe Aviation (IndiGo)', sector: 'Aviation / Transport' },
    { symbol: 'IRCTC.NS', name: 'IRCTC Limited', sector: 'Railways / Tourism' },
    { symbol: 'MOTHERSON.NS', name: 'Samvardhana Motherson', sector: 'Auto Ancillary' },
    { symbol: 'PIDILITIND.NS', name: 'Pidilite Industries', sector: 'Specialty Chemicals' },
    { symbol: 'POLYCAB.NS', name: 'Polycab India', sector: 'Cables & Electricals' },
    { symbol: 'PNB.NS', name: 'Punjab National Bank', sector: 'Financials / PSU Bank' },
    { symbol: 'RECLTD.NS', name: 'REC Limited', sector: 'Financials / Power Finance' },
    { symbol: 'SIEMENS.NS', name: 'Siemens India', sector: 'Engineering & Capital Goods' },
    { symbol: 'TVSMOTOR.NS', name: 'TVS Motor Company', sector: 'Automobiles' },
    { symbol: 'VEDL.NS', name: 'Vedanta Limited', sector: 'Metals & Mining' },
    { symbol: 'BHEL.NS', name: 'Bharat Heavy Electricals', sector: 'Capital Goods' },
    { symbol: 'CANBK.NS', name: 'Canara Bank', sector: 'Financials / PSU Bank' },
    { symbol: 'DABUR.NS', name: 'Dabur India', sector: 'Consumer FMCG' },
    { symbol: 'HAVELLS.NS', name: 'Havells India', sector: 'Consumer Electricals' },
    { symbol: 'ICICIGI.NS', name: 'ICICI Lombard General Ins', sector: 'Financials / Insurance' },
    { symbol: 'ICICIPRULI.NS', name: 'ICICI Prudential Life', sector: 'Financials / Insurance' },
    { symbol: 'IOC.NS', name: 'Indian Oil Corporation', sector: 'Energy / Refining' },
    { symbol: 'NAUKRI.NS', name: 'Info Edge (Naukri)', sector: 'Internet / Recruitment' },
    { symbol: 'PFC.NS', name: 'Power Finance Corporation', sector: 'Financials / Power Finance' },
    { symbol: 'SRF.NS', name: 'SRF Limited', sector: 'Specialty Chemicals' },
    { symbol: 'TATAPOWER.NS', name: 'Tata Power Company', sector: 'Utilities / Power' },
    { symbol: 'ABB.NS', name: 'ABB India', sector: 'Capital Goods / Automation' },
    { symbol: 'ADANIGREEN.NS', name: 'Adani Green Energy', sector: 'Renewable Energy' },
    { symbol: 'ADANIPOWER.NS', name: 'Adani Power', sector: 'Utilities / Power' },
    { symbol: 'AMBUJACEM.NS', name: 'Ambuja Cements', sector: 'Materials / Cement' },
    { symbol: 'BANKBARODA.NS', name: 'Bank of Baroda', sector: 'Financials / PSU Bank' },
    { symbol: 'BOSCHLTD.NS', name: 'Bosch Limited', sector: 'Auto Ancillary' },
    { symbol: 'CGPOWER.NS', name: 'CG Power and Industrial', sector: 'Capital Goods / Electricals' },
    { symbol: 'COLPAL.NS', name: 'Colgate-Palmolive India', sector: 'Consumer FMCG' },
    { symbol: 'HDFCLIFE.NS', name: 'HDFC Life Insurance', sector: 'Financials / Insurance' },
    { symbol: 'LICI.NS', name: 'Life Insurance Corp (LIC)', sector: 'Financials / Insurance' },
    { symbol: 'MARICO.NS', name: 'Marico Limited', sector: 'Consumer FMCG' },
    { symbol: 'MAXHEALTH.NS', name: 'Max Healthcare Institute', sector: 'Healthcare / Hospitals' },
    { symbol: 'NHPC.NS', name: 'NHPC Limited', sector: 'Utilities / Hydro Power' },
    { symbol: 'SBICARD.NS', name: 'SBI Cards & Payment', sector: 'Financial Services' },
    { symbol: 'TORNTPOWER.NS', name: 'Torrent Power', sector: 'Utilities / Power' },
    { symbol: 'TORNTPHARM.NS', name: 'Torrent Pharmaceuticals', sector: 'Healthcare / Pharma' },
    { symbol: 'MCDOWELL-N.NS', name: 'United Spirits', sector: 'Consumer / Beverages' },
    { symbol: 'BERGEPAINT.NS', name: 'Berger Paints', sector: 'Consumer Paints' },
    { symbol: 'ZYDUSLIFE.NS', name: 'Zydus Lifesciences', sector: 'Healthcare / Pharma' },
    { symbol: 'SOLARINDS.NS', name: 'Solar Industries', sector: 'Industrial Explosives' },

    // INDIAN COMMODITIES, METALS & ENERGY (MCX / NSE)
    { symbol: 'GOLDBEES.NS', name: 'Nippon Gold ETF', sector: 'Precious Metals (Gold)' },
    { symbol: 'SILVERBEES.NS', name: 'Nippon Silver ETF', sector: 'Precious Metals (Silver)' },
    { symbol: 'SETFGOLD.NS', name: 'SBI Gold ETF', sector: 'Precious Metals (Gold)' },
    { symbol: 'AXISGOLD.NS', name: 'Axis Gold ETF', sector: 'Precious Metals (Gold)' },
    { symbol: 'NATIONALUM.NS', name: 'National Aluminium Co (NALCO)', sector: 'Base Metals (Aluminium)' },
    { symbol: 'JINDALSTEL.NS', name: 'Jindal Steel & Power', sector: 'Base Metals (Steel)' },
    { symbol: 'NMDC.NS', name: 'NMDC Limited', sector: 'Mining (Iron Ore)' },
    { symbol: 'SAIL.NS', name: 'Steel Authority of India', sector: 'Base Metals (Steel)' },
    { symbol: 'HINDZINC.NS', name: 'Hindustan Zinc', sector: 'Base Metals (Zinc/Lead/Silver)' },
    { symbol: 'MOIL.NS', name: 'MOIL Limited', sector: 'Mining (Manganese)' },
    { symbol: 'HPCL.NS', name: 'Hindustan Petroleum Corp', sector: 'Energy (Refining & Fuels)' },
    { symbol: 'OIL.NS', name: 'Oil India Limited', sector: 'Energy (Crude Oil Exploration)' },
    { symbol: 'PETRONET.NS', name: 'Petronet LNG', sector: 'Energy (LNG Terminal)' },
    { symbol: 'IGL.NS', name: 'Indraprastha Gas', sector: 'Energy (City Gas Distribution)' },
    { symbol: 'MGL.NS', name: 'Mahanagar Gas', sector: 'Energy (City Gas Distribution)' },
    { symbol: 'GUJGASLTD.NS', name: 'Gujarat Gas Limited', sector: 'Energy (Industrial Gas)' },
    { symbol: 'COROMANDEL.NS', name: 'Coromandel International', sector: 'Agri (Fertilizers & Nutrients)' },
    { symbol: 'DEEPAKNTR.NS', name: 'Deepak Nitrite', sector: 'Chemicals / Commodity Intermediates' },
    { symbol: 'PIIND.NS', name: 'PI Industries', sector: 'Agri (Agrochem & CSM)' },
    { symbol: 'TATACHEM.NS', name: 'Tata Chemicals', sector: 'Chemicals (Soda Ash & Agri)' },
    { symbol: 'CHAMBLFERT.NS', name: 'Chambal Fertilisers', sector: 'Agri (Urea & Fertilizers)' },
    { symbol: 'GNFC.NS', name: 'Gujarat Narmada Valley Fert', sector: 'Agri (Fertilizers & Chemicals)' },
    { symbol: 'BALRAMCHIN.NS', name: 'Balrampur Chini Mills', sector: 'Agri (Sugar & Ethanol)' },
    { symbol: 'EIDPARRY.NS', name: 'E.I.D. Parry', sector: 'Agri (Sugar, Bio & Nutraceuticals)' },

    // HIGH-ROCE MIDCAP & SMALLCAP COMPOUNDERS
    { symbol: 'DIXON.NS', name: 'Dixon Technologies', sector: 'Electronics Manufacturing (EMS)' },
    { symbol: 'KAYNES.NS', name: 'Kaynes Technology', sector: 'Electronics Manufacturing (EMS)' },
    { symbol: 'KPITTECH.NS', name: 'KPIT Technologies', sector: 'Automotive Embedded Software' },
    { symbol: 'COFORGE.NS', name: 'Coforge Limited', sector: 'Information Technology' },
    { symbol: 'TATAELXSI.NS', name: 'Tata Elxsi', sector: 'Design & Technology Software' },
    { symbol: 'CYIENT.NS', name: 'Cyient Limited', sector: 'Engineering & Technology' },
    { symbol: 'SONACOMS.NS', name: 'Sona BLW Precision Forgings', sector: 'Auto Components / EV Driveline' },
    { symbol: 'SUZLON.NS', name: 'Suzlon Energy', sector: 'Renewable Wind Energy' },
    { symbol: 'MAZDOCK.NS', name: 'Mazagon Dock Shipbuilders', sector: 'Defense / Naval Shipbuilding' },
    { symbol: 'COCHINSHIP.NS', name: 'Cochin Shipyard', sector: 'Defense / Commercial Shipbuilding' },
    { symbol: 'BDL.NS', name: 'Bharat Dynamics', sector: 'Defense Missiles & Systems' },
    { symbol: 'ASTRAL.NS', name: 'Astral Limited', sector: 'Building Materials (Pipes/Adhesives)' },
    { symbol: 'SUPREMEIND.NS', name: 'Supreme Industries', sector: 'Plastic Products & Piping' },
    { symbol: 'KEI.NS', name: 'KEI Industries', sector: 'Cables & EPC' },
    { symbol: 'CDSL.NS', name: 'Central Depository Services', sector: 'Capital Markets Infrastructure' },
    { symbol: 'BSE.NS', name: 'BSE Limited', sector: 'Stock Exchange Infrastructure' },
    { symbol: 'ANGELONE.NS', name: 'Angel One Limited', sector: 'Retail Fintech & Brokerage' },
    { symbol: 'MCX.NS', name: 'Multi Commodity Exchange', sector: 'Commodity Exchange Infrastructure' },
    { symbol: 'CAMS.NS', name: 'Computer Age Management', sector: 'Mutual Fund Registrar & Transfer' },
    { symbol: 'KIMS.NS', name: 'Krishna Institute of Med Sci', sector: 'Healthcare / Hospitals' },
    { symbol: 'MEDANTA.NS', name: 'Global Health (Medanta)', sector: 'Healthcare / Super Specialty' },
    { symbol: 'JYOTHYLAB.NS', name: 'Jyothy Labs', sector: 'Consumer FMCG' },
    { symbol: 'RADICO.NS', name: 'Radico Khaitan', sector: 'Consumer / Alcoholic Beverages' },
    { symbol: 'BIKAJI.NS', name: 'Bikaji Foods International', sector: 'Packaged Foods & Snacks' },
    { symbol: 'AIAENG.NS', name: 'AIA Engineering', sector: 'Industrial Grinding Media' },
    { symbol: 'TIMKEN.NS', name: 'Timken India', sector: 'Industrial Bearings' },
    { symbol: 'SCHAEFFLER.NS', name: 'Schaeffler India', sector: 'Precision Bearings' },
    { symbol: 'APLAPOLLO.NS', name: 'APL Apollo Tubes', sector: 'Structural Steel Tubes' },
    { symbol: 'JUBLFOOD.NS', name: 'Jubilant FoodWorks', sector: 'Quick Service Restaurants' },
    { symbol: 'DEVYANI.NS', name: 'Devyani International', sector: 'Quick Service Restaurants' }
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
            input.setAttribute('aria-expanded', 'false');
            return;
        }

        // 1. Instant 0ms local catalog match across all 150+ stocks
        const localMatches = LOCAL_CATALOG.filter(s => 
            s.symbol.toLowerCase().includes(val) || 
            s.name.toLowerCase().includes(val) || 
            s.sector.toLowerCase().includes(val)
        ).slice(0, 10);

        if (localMatches.length > 0) {
            currentSuggestions = localMatches;
            renderSearchSuggestions(currentSuggestions);
        }

        // 2. Query backend for deep index / custom tickers with debouncing
        clearTimeout(searchDebounceTimer);
        searchDebounceTimer = setTimeout(async () => {
            try {
                const res = await fetch(`/api/search?q=${encodeURIComponent(val)}`);
                if (!res.ok) return;
                const data = await res.json();
                if (data.results && data.results.length > 0) {
                    // Merge avoiding duplicates
                    const existingSyms = new Set(localMatches.map(m => m.symbol));
                    const newMatches = data.results.filter(r => !existingSyms.has(r.symbol));
                    currentSuggestions = [...localMatches, ...newMatches].slice(0, 10);
                    renderSearchSuggestions(currentSuggestions);
                }
            } catch (err) {
                // Keep local suggestions on network lag
            }
        }, 120);
    });

    // Close dropdown on click outside
    document.addEventListener('click', (e) => {
        if (!input.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.classList.add('hidden');
            input.setAttribute('aria-expanded', 'false');
        }
    });

    input.addEventListener('focus', () => {
        if (input.value.trim().length >= 1 && currentSuggestions.length > 0) {
            dropdown.classList.remove('hidden');
            input.setAttribute('aria-expanded', 'true');
        }
    });
}

function renderSearchSuggestions(results) {
    const dropdown = document.getElementById('search-suggestions');
    const input = document.getElementById('global-ticker-search');
    if (!dropdown) return;

    if (!results || results.length === 0) {
        dropdown.innerHTML = '<div class="p-3 text-xs text-neutral-400 font-mono">No matching securities found.</div>';
        dropdown.classList.remove('hidden');
        if (input) input.setAttribute('aria-expanded', 'true');
        return;
    }

    dropdown.innerHTML = '';
    results.forEach((item, idx) => {
        const div = document.createElement('div');
        div.id = `suggestion-item-${idx}`;
        div.setAttribute('role', 'option');
        div.setAttribute('aria-selected', 'false');
        div.className = 'p-2.5 hover:bg-[#6943FF]/20 cursor-pointer flex justify-between items-center transition';
        div.onmousedown = () => selectSuggestion(item.symbol);
        div.innerHTML = `
            <div>
                <div class="text-xs font-bold text-white font-mono">${item.symbol}</div>
                <div class="text-[11px] text-neutral-400 truncate max-w-[200px]">${item.name}</div>
            </div>
            <span class="text-[10px] px-1.5 py-0.5 rounded bg-[#6943FF]/20 text-purple-300 font-mono border border-[rgba(105,67,255,0.3)]">${item.sector.split('/')[0].trim()}</span>
        `;
        dropdown.appendChild(div);
    });

    dropdown.classList.remove('hidden');
    if (input) input.setAttribute('aria-expanded', 'true');
}

function selectSuggestion(symbol) {
    const input = document.getElementById('global-ticker-search');
    const dropdown = document.getElementById('search-suggestions');
    if (input) {
        input.value = symbol;
        input.setAttribute('aria-expanded', 'false');
    }
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
        if (input) input.setAttribute('aria-expanded', 'false');
    }
}

function highlightSuggestion(index) {
    const input = document.getElementById('global-ticker-search');
    currentSuggestions.forEach((_, idx) => {
        const el = document.getElementById(`suggestion-item-${idx}`);
        if (el) {
            if (idx === index) {
                el.classList.add('bg-[#6943FF]/30');
                el.setAttribute('aria-selected', 'true');
                if (input) input.setAttribute('aria-activedescendant', `suggestion-item-${idx}`);
                // Scroll into view so highlighted item stays visible in scroll container
                el.scrollIntoView({ block: 'nearest' });
            } else {
                el.classList.remove('bg-[#6943FF]/30');
                el.setAttribute('aria-selected', 'false');
            }
        }
    });
}
