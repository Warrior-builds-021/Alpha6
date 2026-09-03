/**
 * ALPHA6 Enterprise Terminal Client JavaScript
 * Connects to FastAPI endpoints and powers real-time institutional analytics.
 */

let radarChartInstance = null;
let equityChartInstance = null;

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    // Check if custom universe dropdown changes
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

    // Run initial screener on load
    runScreener();
    // Preload default audit
    executeAudit('RELIANCE.NS');
    // Preload backtest
    runBacktest();
    // Preload risk plan
    calculateRiskPlan();
});

// ==================== TAB SWITCHING ====================
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

    if (tabId === 'tab-chart') {
        const sym = document.getElementById('tv-symbol-input').value || 'NSE:RELIANCE';
        loadTradingView(sym);
    }
}

// ==================== TAB 1: UNIVERSE SCREENER ====================
async function runScreener() {
    const universe = document.getElementById('screener-universe').value;
    const custom = document.getElementById('custom-tickers-input').value;
    const threshold = parseFloat(document.getElementById('screener-threshold').value) || 78.0;

    const btn = document.getElementById('btn-run-screener');
    btn.disabled = true;
    btn.innerHTML = `<span>Auditing Universe...</span>`;

    const tbody = document.getElementById('screener-tbody');
    tbody.innerHTML = `<tr><td colspan="13" class="p-8 text-center text-sky-400 font-mono animate-pulse">Running multi-threaded 6-pillar forensic audit...</td></tr>`;

    try {
        let url = `/api/screen?universe=${universe}&threshold=${threshold}`;
        if (universe === 'custom' && custom) {
            url += `&custom_symbols=${encodeURIComponent(custom)}`;
        }

        const res = await fetch(url);
        const data = await res.json();

        // Update KPIs
        document.getElementById('kpi-total').innerText = data.total_scanned;
        document.getElementById('kpi-passed').innerText = data.high_conviction_count;
        const passRate = data.total_scanned > 0 ? ((data.high_conviction_count / data.total_scanned) * 100).toFixed(0) : 0;
        document.getElementById('kpi-pass-rate').innerText = `${passRate}% Selection Rate`;

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
                card.className = 'bg-[#0F172A] border border-[#1E293B] hover:border-emerald-500/50 transition rounded-xl p-4 cursor-pointer';
                card.onclick = () => { executeAudit(pick.symbol); switchTab('tab-audit'); };
                card.innerHTML = `
                    <div class="flex justify-between items-center mb-1">
                        <span class="text-base font-bold text-white font-mono">${pick.symbol}</span>
                        <span class="text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-mono font-bold">${pick.composite_score}% BUY</span>
                    </div>
                    <div class="text-xs text-slate-400 mb-3 truncate">${pick.name}</div>
                    <div class="text-xl font-bold text-white font-mono mb-2">${pick.currency} ${parseFloat(pick.price).toFixed(2)}</div>
                    <div class="grid grid-cols-2 gap-1 text-[11px] font-mono text-slate-300 pt-2 border-t border-[#1E293B]">
                        <div>OCF Quality: <b class="text-emerald-400">${pick.ocf_score}/100</b></div>
                        <div>Debt Health: <b class="text-emerald-400">${pick.debt_score}/100</b></div>
                    </div>
                `;
                topGrid.appendChild(card);
            });
        } else {
            topGrid.innerHTML = `<div class="col-span-3 p-4 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs font-mono">No equities cleared the strict ${threshold}% conviction threshold today with zero red flags. Capital is safely preserved.</div>`;
        }

        // Render Table Rows
        tbody.innerHTML = '';
        data.results.forEach(r => {
            const tr = document.createElement('tr');
            tr.className = 'hover:bg-[#1E293B]/40 cursor-pointer transition';
            tr.onclick = () => { executeAudit(r.symbol); switchTab('tab-audit'); };

            const isPass = r.is_recommended;
            const hasFlags = r.red_flag_count > 0;
            const badgeClass = isPass 
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' 
                : (hasFlags ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30' : 'bg-amber-500/10 text-amber-400 border border-amber-500/30');

            const scoreColor = r.composite_score >= 78 ? 'text-emerald-400 font-bold' : (r.composite_score >= 60 ? 'text-amber-400' : 'text-rose-400');

            tr.innerHTML = `
                <td class="p-3.5 font-bold text-sky-400">${r.symbol}</td>
                <td class="p-3.5 font-sans font-medium text-slate-200 truncate max-w-[180px]">${r.name}</td>
                <td class="p-3.5 font-mono">${r.currency} ${parseFloat(r.price).toFixed(2)}</td>
                <td class="p-3.5 font-mono ${scoreColor}">${r.composite_score}%</td>
                <td class="p-3.5 font-mono text-slate-300">${r.volume_score}</td>
                <td class="p-3.5 font-mono text-slate-300">${r.sales_score}</td>
                <td class="p-3.5 font-mono text-slate-300">${r.ocf_score}</td>
                <td class="p-3.5 font-mono text-slate-300">${r.debt_score}</td>
                <td class="p-3.5 font-mono text-slate-300">${r.pricing_score}</td>
                <td class="p-3.5 font-mono text-slate-300">${r.skin_score}</td>
                <td class="p-3.5 font-mono text-slate-300">${r.piotroski_f_score}/9</td>
                <td class="p-3.5 font-mono text-slate-300">${r.altman_z_score}</td>
                <td class="p-3.5"><span class="text-xs px-2 py-0.5 rounded font-mono font-bold ${badgeClass}">${r.signal}</span></td>
            `;
            tbody.appendChild(tr);
        });

    } catch (e) {
        console.error(e);
        tbody.innerHTML = `<tr><td colspan="13" class="p-8 text-center text-rose-400 font-mono">Error scanning universe: ${e.message}</td></tr>`;
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

        // Populate Header
        document.getElementById('audit-symbol').innerText = ev.symbol;
        document.getElementById('audit-company-name').innerText = `${ev.short_name} • ${ev.sector} • ${ev.currency} ${parseFloat(ev.current_price).toFixed(2)}`;
        document.getElementById('audit-composite-score').innerText = `${ev.composite_score}%`;

        const badge = document.getElementById('audit-signal-badge');
        badge.innerText = ev.signal;
        badge.className = ev.is_recommended 
            ? 'text-xs px-2.5 py-1 rounded-md font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
            : (ev.red_flags.length > 0 ? 'text-xs px-2.5 py-1 rounded-md font-mono font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30' : 'text-xs px-2.5 py-1 rounded-md font-mono font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30');

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

        // Red flags warning if any
        if (ev.red_flags.length > 0) {
            const rfBox = document.createElement('div');
            rfBox.className = 'bg-rose-500/10 border-l-4 border-rose-500 p-3 rounded text-xs text-rose-300 font-mono space-y-1';
            rfBox.innerHTML = `<b>CRITICAL RISK SHIELD WARNINGS:</b>` + ev.red_flags.map(f => `<div>• ${f}</div>`).join('');
            breakdown.appendChild(rfBox);
        }

        pillarOrder.forEach(item => {
            const pol = p[item.key];
            const div = document.createElement('div');
            div.className = 'bg-[#080C14] border border-[#1E293B] rounded-lg p-3.5 space-y-1.5';
            
            const scoreColor = pol.score >= 75 ? 'text-emerald-400' : (pol.score >= 50 ? 'text-amber-400' : 'text-rose-400');
            
            div.innerHTML = `
                <div class="flex justify-between items-center">
                    <span class="text-xs font-bold text-white uppercase font-mono">${item.title}</span>
                    <span class="text-sm font-black font-mono ${scoreColor}">${pol.score}/100</span>
                </div>
                <div class="text-xs text-slate-300 font-sans space-y-0.5">
                    ${pol.details.map(d => `<div>• ${d}</div>`).join('')}
                </div>
            `;
            breakdown.appendChild(div);
        });

        // Set symbol for other tabs
        document.getElementById('tv-symbol-input').value = data.tradingview_symbol;
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
                    backgroundColor: 'rgba(56, 189, 248, 0.2)',
                    borderColor: '#38BDF8',
                    borderWidth: 2,
                    pointBackgroundColor: '#38BDF8'
                },
                {
                    label: '78% Conviction Benchmark',
                    data: [78, 78, 78, 78, 78, 78],
                    borderColor: '#10B981',
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
                    grid: { color: '#1E293B' },
                    angleLines: { color: '#1E293B' },
                    ticks: { display: false },
                    pointLabels: {
                        color: '#94A3B8',
                        font: { size: 11, family: 'Inter' }
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#CBD5E1', font: { family: 'Inter', size: 11 } }
                }
            }
        }
    });
}

// ==================== TAB 3: TRADINGVIEW WIDGET ====================
function loadTradingView(symbol) {
    const container = document.getElementById('tradingview_chart');
    container.innerHTML = '';
    
    new TradingView.widget({
        "autosize": true,
        "symbol": symbol || "NSE:RELIANCE",
        "interval": "D",
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#0F172A",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "container_id": "tradingview_chart"
    });
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

        // Render Equity Chart
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
                    borderColor: '#34D399',
                    borderWidth: 2,
                    fill: false,
                    pointRadius: 0
                },
                {
                    label: `Benchmark (${benchmark})`,
                    data: bmValues,
                    borderColor: '#64748B',
                    borderWidth: 1.5,
                    borderDash: [4, 4],
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
                    grid: { color: '#1E293B' },
                    ticks: { color: '#64748B', maxTicksLimit: 8, font: { family: 'JetBrains Mono', size: 10 } }
                },
                y: {
                    grid: { color: '#1E293B' },
                    ticks: { color: '#64748B', font: { family: 'JetBrains Mono', size: 10 } }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: { color: '#CBD5E1', font: { family: 'Inter', size: 11 } }
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
            <div class="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 space-y-3">
                <div class="text-xs uppercase font-bold text-slate-400 font-mono">1. Entry & Position Sizing</div>
                <div class="text-2xl font-black font-mono text-white">${plan.currency} ${parseFloat(plan.current_price).toFixed(2)}</div>
                <div class="text-xs text-slate-400">Current Market Reference Price</div>
                <div class="pt-3 border-t border-[#1E293B] space-y-1.5 font-mono text-xs">
                    <div class="flex justify-between"><span>Recommended Quantity:</span><b class="text-sky-400 text-sm">${plan.recommended_shares} Shares</b></div>
                    <div class="flex justify-between"><span>Total Investment:</span><b class="text-white">${plan.currency} ${plan.total_investment.toLocaleString()}</b></div>
                    <div class="flex justify-between"><span>Portfolio Weight:</span><b class="text-white">${plan.portfolio_weight_pct}%</b></div>
                </div>
            </div>

            <div class="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 space-y-3">
                <div class="text-xs uppercase font-bold text-slate-400 font-mono">2. Downside Capital Shield</div>
                <div class="text-2xl font-black font-mono text-rose-400">${plan.currency} ${parseFloat(plan.stop_loss).toFixed(2)}</div>
                <div class="text-xs text-rose-400/80">Strict 2.0x ATR Stop Loss (${plan.stop_loss_pct}%)</div>
                <div class="pt-3 border-t border-[#1E293B] space-y-1.5 font-mono text-xs">
                    <div class="flex justify-between"><span>Max Capital at Risk:</span><b class="text-rose-400">${plan.currency} ${plan.max_risk_capital.toLocaleString()}</b></div>
                    <div class="flex justify-between"><span>Risk Percentage:</span><b class="text-rose-400">Strictly Capped at ${riskPct}%</b></div>
                    <div class="flex justify-between"><span>14-Period ATR:</span><b class="text-slate-300">${plan.atr_14}</b></div>
                </div>
            </div>

            <div class="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 space-y-3">
                <div class="text-xs uppercase font-bold text-slate-400 font-mono">3. Asymmetric Profit Targets</div>
                <div class="text-2xl font-black font-mono text-emerald-400">${plan.currency} ${parseFloat(plan.target_2).toFixed(2)}</div>
                <div class="text-xs text-emerald-400/80">Target 2 Upside (+${plan.target_2_upside_pct}%)</div>
                <div class="pt-3 border-t border-[#1E293B] space-y-1.5 font-mono text-xs">
                    <div class="flex justify-between"><span>Target 1 (1:2 R:R):</span><b class="text-emerald-400">${plan.currency} ${plan.target_1} (+${plan.target_1_upside_pct}%)</b></div>
                    <div class="flex justify-between"><span>Projected Gain (T2):</span><b class="text-emerald-400">${plan.currency} ${plan.potential_gain_t2.toLocaleString()}</b></div>
                    <div class="flex justify-between"><span>Risk-to-Reward:</span><b class="text-slate-300">${plan.risk_reward_ratio}</b></div>
                </div>
            </div>
        `;

    } catch (e) {
        console.error(e);
    }
}
