"""
EV Auto Comp Sales Tracker - Dashboard Generator
Generates a beautiful, EV Auto branded HTML dashboard with charts.
Shows daily, monthly, and yearly sales rankings vs competitors.
"""

import os
import json
from datetime import datetime, timedelta
from compare import load_sales_history, get_monthly_summary, get_yearly_summary
from config import DATA_DIR


def generate_dashboard(date_str=None, daily_sales_detail=None):
    """Generate the full HTML dashboard.

    Args:
        date_str: Date string YYYY-MM-DD
        daily_sales_detail: Optional dict from compute_daily_sales() with VIN-level detail
    """
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')

    history = load_sales_history()
    today = datetime.strptime(date_str, '%Y-%m-%d')
    monthly = get_monthly_summary(history, today.year, today.month)
    yearly = get_yearly_summary(history, today.year)

    # Get today's data
    today_data = None
    for record in history['daily']:
        if record['date'] == date_str:
            today_data = record
            break

    # Build VIN detail data for the modal
    vin_detail = {}
    if daily_sales_detail:
        for dk, data in daily_sales_detail.items():
            vin_detail[dk] = {
                'name': data.get('name', dk),
                'tesla_sold': data.get('tesla', {}).get('sold_vins', []),
                'rivian_sold': data.get('rivian', {}).get('sold_vins', []),
                'tesla_inventory': data.get('tesla', {}).get('current_inventory', 0),
                'rivian_inventory': data.get('rivian', {}).get('current_inventory', 0),
            }

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EV Auto - Competitive Sales Dashboard</title>
    <style>
        /* EV Auto Brand: Helvetica Neue Â· Citron Â· Jetstream Â· Midnight */

        :root {{
            --ev-midnight: #1A1A1A;
            --ev-citron: #CDFC41;
            --ev-jetstream: #F5F5F2;
            --ev-white: #FFFFFF;
            --ev-border: #E4E4E0;
            --ev-text: #1A1A1A;
            --ev-text-muted: #6B6B6B;
            --ev-card: #FFFFFF;
            --ev-highlight-bg: rgba(205, 252, 65, 0.08);
            --ev-gold: #CDFC41;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            background: var(--ev-jetstream);
            color: var(--ev-text);
            min-height: 100vh;
            -webkit-font-smoothing: antialiased;
        }}

        .header {{
            background: var(--ev-midnight);
            padding: 24px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .logo {{
            display: flex;
            align-items: center;
            gap: 14px;
        }}

        .logo-icon {{
            width: 44px;
            height: 44px;
            background: var(--ev-citron);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            font-weight: 800;
            color: var(--ev-midnight);
            letter-spacing: -1px;
        }}

        .logo-text {{
            font-size: 22px;
            font-weight: 700;
            color: var(--ev-white);
            letter-spacing: -0.5px;
        }}

        .logo-text span {{
            color: var(--ev-citron);
        }}

        .header-meta {{
            text-align: right;
            color: #999;
            font-size: 13px;
        }}

        .header-meta .date {{
            font-size: 17px;
            color: var(--ev-white);
            font-weight: 600;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px 30px;
        }}

        .section-title {{
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .section-title .badge {{
            background: var(--ev-citron);
            color: var(--ev-midnight);
            font-size: 11px;
            font-weight: 700;
            padding: 3px 10px;
            border-radius: 20px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        /* KPI Cards */
        .kpi-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 40px;
        }}

        .kpi-card {{
            background: var(--ev-card);
            border: 1px solid var(--ev-border);
            border-radius: 10px;
            padding: 22px;
            position: relative;
            overflow: hidden;
        }}

        .kpi-card.highlight {{
            border-color: var(--ev-citron);
            border-width: 2px;
            background: var(--ev-highlight-bg);
        }}

        .kpi-label {{
            font-size: 11px;
            color: var(--ev-text-muted);
            text-transform: uppercase;
            letter-spacing: 1.2px;
            margin-bottom: 10px;
            font-weight: 500;
        }}

        .kpi-value {{
            font-size: 38px;
            font-weight: 800;
            line-height: 1;
            color: var(--ev-midnight);
        }}

        .kpi-card.highlight .kpi-value {{
            color: var(--ev-midnight);
        }}

        .kpi-sub {{
            font-size: 13px;
            color: var(--ev-text-muted);
            margin-top: 8px;
        }}

        /* Rankings Table */
        .rankings-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }}

        @media (max-width: 1000px) {{
            .rankings-grid {{ grid-template-columns: 1fr; }}
        }}

        .ranking-card {{
            background: var(--ev-card);
            border: 1px solid var(--ev-border);
            border-radius: 10px;
            overflow: hidden;
        }}

        .ranking-header {{
            padding: 16px 20px;
            background: var(--ev-midnight);
            color: var(--ev-white);
            font-weight: 700;
            font-size: 15px;
            letter-spacing: -0.2px;
        }}

        .ranking-table {{
            width: 100%;
            border-collapse: collapse;
        }}

        .ranking-table th {{
            text-align: left;
            padding: 10px 20px;
            font-size: 10px;
            color: var(--ev-text-muted);
            text-transform: uppercase;
            letter-spacing: 1.2px;
            border-bottom: 1px solid var(--ev-border);
            font-weight: 600;
        }}

        .ranking-table td {{
            padding: 12px 20px;
            font-size: 14px;
            border-bottom: 1px solid var(--ev-border);
            color: var(--ev-text);
        }}

        .ranking-table tr:last-child td {{
            border-bottom: none;
        }}

        .ranking-table tr.is-us {{
            background: var(--ev-highlight-bg);
        }}

        .ranking-table tr.is-us td {{
            font-weight: 700;
        }}

        .rank-num {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 26px;
            height: 26px;
            border-radius: 50%;
            background: var(--ev-jetstream);
            font-size: 12px;
            font-weight: 700;
            color: var(--ev-text);
        }}

        .rank-1 {{ background: var(--ev-citron); color: var(--ev-midnight); }}
        .rank-2 {{ background: #E0E0E0; color: var(--ev-midnight); }}
        .rank-3 {{ background: #D4C4A8; color: var(--ev-midnight); }}

        .is-us .rank-num {{
            box-shadow: 0 0 0 2px var(--ev-citron);
        }}

        .dealer-name {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .us-badge {{
            background: var(--ev-midnight);
            color: var(--ev-citron);
            font-size: 9px;
            font-weight: 800;
            padding: 2px 7px;
            border-radius: 3px;
            letter-spacing: 0.8px;
        }}

        /* Footer */
        .footer {{
            text-align: center;
            padding: 24px;
            color: var(--ev-text-muted);
            font-size: 12px;
            border-top: 1px solid var(--ev-border);
            margin-top: 30px;
        }}

        .footer a {{
            color: var(--ev-midnight);
            text-decoration: none;
            font-weight: 600;
        }}

        .no-data {{
            text-align: center;
            padding: 40px;
            color: var(--ev-text-muted);
            font-style: italic;
        }}

        /* Tab switcher */
        .tabs {{
            display: flex;
            gap: 4px;
            margin-bottom: 24px;
            background: var(--ev-white);
            border-radius: 8px;
            padding: 4px;
            border: 1px solid var(--ev-border);
            width: fit-content;
        }}
        .tab {{
            padding: 8px 22px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            color: var(--ev-text-muted);
            transition: all 0.2s;
        }}
        .tab.active {{
            background: var(--ev-midnight);
            color: var(--ev-citron);
            font-weight: 700;
        }}
        .tab:hover:not(.active) {{
            color: var(--ev-text);
            background: var(--ev-jetstream);
        }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}

        /* Clickable sold numbers */
        .sold-count {{
            cursor: pointer;
            color: var(--ev-midnight);
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 4px;
            transition: all 0.15s;
            display: inline-block;
        }}
        .sold-count:hover {{
            background: var(--ev-citron);
            color: var(--ev-midnight);
        }}
        .sold-count::after {{
            content: ' â';
            font-size: 11px;
            opacity: 0;
            transition: opacity 0.15s;
        }}
        .sold-count:hover::after {{
            opacity: 0.6;
        }}

        /* Detail Modal */
        .modal-overlay {{
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(26, 26, 26, 0.5);
            backdrop-filter: blur(4px);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }}
        .modal-overlay.active {{
            display: flex;
        }}
        .modal {{
            background: var(--ev-white);
            border-radius: 12px;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
        }}
        .modal-header {{
            background: var(--ev-midnight);
            color: var(--ev-white);
            padding: 20px 24px;
            border-radius: 12px 12px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .modal-header h3 {{
            font-size: 18px;
            font-weight: 700;
        }}
        .modal-close {{
            background: none;
            border: none;
            color: #999;
            font-size: 24px;
            cursor: pointer;
            padding: 0 4px;
            line-height: 1;
        }}
        .modal-close:hover {{
            color: var(--ev-citron);
        }}
        .modal-body {{
            padding: 24px;
        }}
        .modal-section {{
            margin-bottom: 20px;
        }}
        .modal-section:last-child {{
            margin-bottom: 0;
        }}
        .modal-section-title {{
            font-size: 13px;
            font-weight: 700;
            color: var(--ev-text-muted);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        .vin-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }}
        .vin-tag {{
            background: var(--ev-jetstream);
            border: 1px solid var(--ev-border);
            padding: 4px 10px;
            border-radius: 4px;
            font-family: 'SF Mono', 'Menlo', monospace;
            font-size: 12px;
            color: var(--ev-midnight);
            letter-spacing: 0.3px;
        }}
        .vin-empty {{
            color: var(--ev-text-muted);
            font-style: italic;
            font-size: 13px;
        }}
        .modal-stat {{
            display: inline-block;
            background: var(--ev-highlight-bg);
            border: 1px solid var(--ev-citron);
            padding: 6px 14px;
            border-radius: 6px;
            font-weight: 700;
            font-size: 14px;
            margin-right: 10px;
            margin-bottom: 8px;
        }}
    </style>
</head>
<body>

<div class="header">
    <div class="logo">
        <div class="logo-icon">EV</div>
        <div class="logo-text"><span>EV</span> Auto</div>
    </div>
    <div class="header-meta">
        <div class="date">{today.strftime('%B %d, %Y')}</div>
        <div>Competitive Sales Dashboard</div>
        <div>Updated daily at 8:00 AM</div>
    </div>
</div>

<div class="container">
"""

    # KPI Cards
    ev_auto_today = today_data['dealers'].get('ev_auto', {}) if today_data else {}
    ev_auto_monthly = monthly.get('ev_auto', {})
    ev_auto_yearly = yearly.get('ev_auto', {})
    total_competitors_today = sum(
        d.get('total_sold', 0) for k, d in (today_data['dealers'] if today_data else {}).items() if k != 'ev_auto'
    )

    html += f"""
    <div class="kpi-row">
        <div class="kpi-card highlight">
            <div class="kpi-label">EV Auto Sales Today</div>
            <div class="kpi-value">{ev_auto_today.get('total_sold', 0)}</div>
            <div class="kpi-sub">Tesla: {ev_auto_today.get('tesla_sold', 0)} Â· Rivian: {ev_auto_today.get('rivian_sold', 0)}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Competitors Avg Today</div>
            <div class="kpi-value">{total_competitors_today // max(len([k for k in (today_data['dealers'] if today_data else {}) if k != 'ev_auto']), 1)}</div>
            <div class="kpi-sub">Total across {len([k for k in (today_data['dealers'] if today_data else {}) if k != 'ev_auto'])} competitors: {total_competitors_today}</div>
        </div>
        <div class="kpi-card highlight">
            <div class="kpi-label">EV Auto MTD</div>
            <div class="kpi-value">{ev_auto_monthly.get('total_sold', 0)}</div>
            <div class="kpi-sub">Tesla: {ev_auto_monthly.get('tesla_sold', 0)} Â· Rivian: {ev_auto_monthly.get('rivian_sold', 0)}</div>
        </div>
        <div class="kpi-card highlight">
            <div class="kpi-label">EV Auto YTD</div>
            <div class="kpi-value">{ev_auto_yearly.get('total_sold', 0)}</div>
            <div class="kpi-sub">Tesla: {ev_auto_yearly.get('tesla_sold', 0)} Â· Rivian: {ev_auto_yearly.get('rivian_sold', 0)}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">EV Auto Current Stock</div>
            <div class="kpi-value">{ev_auto_today.get('tesla_inventory', 0) + ev_auto_today.get('rivian_inventory', 0)}</div>
            <div class="kpi-sub">Tesla: {ev_auto_today.get('tesla_inventory', 0)} Â· Rivian: {ev_auto_today.get('rivian_inventory', 0)}</div>
        </div>
    </div>
"""

    # Tab Switcher
    html += """
    <div class="tabs">
        <div class="tab active" onclick="switchTab('daily')">Daily</div>
        <div class="tab" onclick="switchTab('monthly')">Monthly</div>
        <div class="tab" onclick="switchTab('yearly')">Yearly</div>
    </div>
"""

    # Generate ranking tables for each period
    for period_key, period_label, period_data in [
        ('daily', "Today's Sales", today_data['dealers'] if today_data else {}),
        ('monthly', f"{today.strftime('%B %Y')} Sales", monthly),
        ('yearly', f"{today.year} Sales (YTD)", yearly),
    ]:
        # Sort dealers by total sold descending
        sorted_dealers = sorted(
            period_data.items(),
            key=lambda x: x[1].get('total_sold', 0),
            reverse=True
        )

        active = ' active' if period_key == 'daily' else ''
        html += f"""
    <div class="tab-content{active}" id="tab-{period_key}">
        <div class="rankings-grid">
            <div class="ranking-card">
                <div class="ranking-header">ð Overall Ranking â {period_label}</div>
                <table class="ranking-table">
                    <tr><th>#</th><th>Dealer</th><th>Total Sold</th></tr>
"""
        for rank, (dk, dd) in enumerate(sorted_dealers, 1):
            is_us = 'is-us' if dd.get('is_us') else ''
            rank_class = f'rank-{rank}' if rank <= 3 else ''
            us_badge = '<span class="us-badge">US</span>' if dd.get('is_us') else ''
            sold_val = dd.get('total_sold', 0)
            click_attr = f'onclick="showDetail(\'{dk}\', \'all\')"' if period_key == 'daily' and sold_val > 0 else ''
            sold_class = 'sold-count' if period_key == 'daily' and sold_val > 0 else ''
            html += f"""                    <tr class="{is_us}">
                        <td><span class="rank-num {rank_class}">{rank}</span></td>
                        <td><span class="dealer-name">{dd.get('name', dk)} {us_badge}</span></td>
                        <td><span class="{sold_class}" {click_attr}>{sold_val}</span></td>
                    </tr>
"""
        html += """                </table>
            </div>
"""
        # Tesla ranking
        sorted_tesla = sorted(period_data.items(), key=lambda x: x[1].get('tesla_sold', 0), reverse=True)
        html += f"""
            <div class="ranking-card">
                <div class="ranking-header">â¡ Tesla Ranking â {period_label}</div>
                <table class="ranking-table">
                    <tr><th>#</th><th>Dealer</th><th>Tesla Sold</th></tr>
"""
        for rank, (dk, dd) in enumerate(sorted_tesla, 1):
            is_us = 'is-us' if dd.get('is_us') else ''
            rank_class = f'rank-{rank}' if rank <= 3 else ''
            us_badge = '<span class="us-badge">US</span>' if dd.get('is_us') else ''
            sold_val = dd.get('tesla_sold', 0)
            click_attr = f'onclick="showDetail(\'{dk}\', \'tesla\')"' if period_key == 'daily' and sold_val > 0 else ''
            sold_class = 'sold-count' if period_key == 'daily' and sold_val > 0 else ''
            html += f"""                    <tr class="{is_us}">
                        <td><span class="rank-num {rank_class}">{rank}</span></td>
                        <td><span class="dealer-name">{dd.get('name', dk)} {us_badge}</span></td>
                        <td><span class="{sold_class}" {click_attr}>{sold_val}</span></td>
                    </tr>
"""
        html += """                </table>
            </div>
"""
        # Rivian ranking
        sorted_rivian = sorted(period_data.items(), key=lambda x: x[1].get('rivian_sold', 0), reverse=True)
        html += f"""
            <div class="ranking-card">
                <div class="ranking-header">ð Rivian Ranking â {period_label}</div>
                <table class="ranking-table">
                    <tr><th>#</th><th>Dealer</th><th>Rivian Sold</th></tr>
"""
        for rank, (dk, dd) in enumerate(sorted_rivian, 1):
            is_us = 'is-us' if dd.get('is_us') else ''
            rank_class = f'rank-{rank}' if rank <= 3 else ''
            us_badge = '<span class="us-badge">US</span>' if dd.get('is_us') else ''
            sold_val = dd.get('rivian_sold', 0)
            click_attr = f'onclick="showDetail(\'{dk}\', \'rivian\')"' if period_key == 'daily' and sold_val > 0 else ''
            sold_class = 'sold-count' if period_key == 'daily' and sold_val > 0 else ''
            html += f"""                    <tr class="{is_us}">
                        <td><span class="rank-num {rank_class}">{rank}</span></td>
                        <td><span class="dealer-name">{dd.get('name', dk)} {us_badge}</span></td>
                        <td><span class="{sold_class}" {click_attr}>{sold_val}</span></td>
                    </tr>
"""
        html += """                </table>
            </div>
        </div>
    </div>
"""

    # Embed VIN detail data as JSON
    vin_detail_json = json.dumps(vin_detail)

    html += f"""
</div>

<!-- Detail Modal -->
<div class="modal-overlay" id="detailModal" onclick="if(event.target===this)closeModal()">
    <div class="modal">
        <div class="modal-header">
            <h3 id="modalTitle">Dealer Detail</h3>
            <button class="modal-close" onclick="closeModal()">&times;</button>
        </div>
        <div class="modal-body" id="modalBody"></div>
    </div>
</div>

<div class="footer">
    <a href="https://www.evauto.com">EV Auto</a> Â· Competitive Sales Dashboard Â· Data refreshed daily at 8:00 AM<br>
    VIN-based tracking: vehicles removed from inventory day-over-day = estimated sales
</div>

<script>
    const vinData = {vin_detail_json};

    // Tab switching
    function switchTab(tabName) {{
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
        document.querySelector(`#tab-${{tabName}}`).classList.add('active');
        event.target.classList.add('active');
    }}

    // Detail modal
    function showDetail(dealerKey, makeFilter) {{
        const dealer = vinData[dealerKey];
        if (!dealer) return;

        const modal = document.getElementById('detailModal');
        const title = document.getElementById('modalTitle');
        const body = document.getElementById('modalBody');

        title.textContent = dealer.name + ' â Sold Today';

        let html = '';

        // Stats row
        const teslaCount = dealer.tesla_sold ? dealer.tesla_sold.length : 0;
        const rivianCount = dealer.rivian_sold ? dealer.rivian_sold.length : 0;
        html += '<div style="margin-bottom:20px">';
        html += '<span class="modal-stat">Tesla Sold: ' + teslaCount + '</span>';
        html += '<span class="modal-stat">Rivian Sold: ' + rivianCount + '</span>';
        html += '<span class="modal-stat">Current Tesla Inv: ' + (dealer.tesla_inventory || 0) + '</span>';
        html += '<span class="modal-stat">Current Rivian Inv: ' + (dealer.rivian_inventory || 0) + '</span>';
        html += '</div>';

        if (makeFilter === 'all' || makeFilter === 'tesla') {{
            html += '<div class="modal-section">';
            html += '<div class="modal-section-title">Tesla VINs Sold</div>';
            if (dealer.tesla_sold && dealer.tesla_sold.length > 0) {{
                html += '<div class="vin-list">';
                dealer.tesla_sold.forEach(vin => {{
                    html += '<span class="vin-tag">' + vin + '</span>';
                }});
                html += '</div>';
            }} else {{
                html += '<div class="vin-empty">No Tesla VINs sold today</div>';
            }}
            html += '</div>';
        }}

        if (makeFilter === 'all' || makeFilter === 'rivian') {{
            html += '<div class="modal-section">';
            html += '<div class="modal-section-title">Rivian VINs Sold</div>';
            if (dealer.rivian_sold && dealer.rivian_sold.length > 0) {{
                html += '<div class="vin-list">';
                dealer.rivian_sold.forEach(vin => {{
                    html += '<span class="vin-tag">' + vin + '</span>';
                }});
                html += '</div>';
            }} else {{
                html += '<div class="vin-empty">No Rivian VINs sold today</div>';
            }}
            html += '</div>';
        }}

        body.innerHTML = html;
        modal.classList.add('active');
    }}

    function closeModal() {{
        document.getElementById('detailModal').classList.remove('active');
    }}

    document.addEventListener('keydown', e => {{
        if (e.key === 'Escape') closeModal();
    }});
</script>

</body>
</html>"""

    # Save dashboard
    os.makedirs(DATA_DIR, exist_ok=True)
    dashboard_path = os.path.join(DATA_DIR, "dashboard.html")
    with open(dashboard_path, 'w') as f:
        f.write(html)

    return dashboard_path


if __name__ == '__main__':
    path = generate_dashboard()
    print(f"Dashboard generated: {path}")
