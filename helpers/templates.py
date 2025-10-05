"""HTML templates for SWOT DCIF Engine."""

import json
from typing import List
from .models import RunSummary, SWOTItem


FORM_HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>SWOT DCIF Engine (v2)</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 980px; margin: 0 auto; padding: 24px; background:#f7f7f7;}
    h1 { color:#222; }
    h2 { color:#444; margin-top:28px; }
    .card { background:#fff; border-radius:8px; padding:20px; box-shadow:0 2px 8px rgba(0,0,0,0.06); margin-bottom:20px; }
    label { display:block; font-weight:bold; margin:10px 0 6px; color:#333;}
    input[type=text], textarea { width:100%; padding:10px; border:1px solid #ddd; border-radius:6px; box-sizing:border-box; }
    textarea { min-height:90px; }
    .grid { display:grid; gap:12px; grid-template-columns: 1fr 1fr; }
    .btn { background:#2d7a46; color:#fff; border:none; padding:12px 18px; border-radius:6px; cursor:pointer; font-size:16px; }
    .btn:hover { background:#25663a; }
    .muted { color:#666; font-size:14px;}
    .small { font-size:12px; color:#777;}
    .status { display:none; margin-top:12px; padding:10px; border-radius:6px;}
    .loading { display:block; background:#fff3cd; color:#856404;}
    .error { display:block; background:#f8d7da; color:#721c24;}
  </style>
  <script>
    function onSubmit(evt){
      evt.preventDefault();
      const form = evt.target;
      const status = document.getElementById('status');
      status.className = 'status loading';
      status.textContent = 'Running DCIF analysis with AI…';
      const btn = document.getElementById('submitBtn');
      btn.disabled = true; btn.textContent = 'Analyzing…';

      const fd = new FormData(form);
      fetch('/analyze', { method:'POST', body: fd })
        .then(r => { if(!r.ok) throw new Error('Network error'); return r.text(); })
        .then(html => { document.open(); document.write(html); document.close(); })
        .catch(err => {
          status.className = 'status error';
          status.textContent = 'Error: ' + err.message;
          btn.disabled = false; btn.textContent = 'Analyze';
        });
    }

    function togglePrefill(checked){
      if(checked){
        document.getElementsByName('company_name')[0].value = 'Zen Software';
        document.getElementsByName('desired_outcomes')[0].value = 'increase downloads for Bodybuilding Diet App on iOS';

        document.getElementsByName('layer_canonical')[0].value = 'Premium bodybuilding diet app designed by seasoned competition professionals (Bodybuilding, Physique, Figure, Bikini). Core value prop: "Training happens in the gym, Growth is in the kitchen." Target: dedicated serious athletes only. Features: 400k+ food database with High Carb/Protein/Fat categorization, weekly macro cycling (carbs/protein/fat), meal timing optimization, progress visualization with automated analysis, customizable meal plans. Freemium model: Free download with IAP ($9.99/month, $49.99/6mo, $79.99/year). Recently added AI Chat functionality (Dec 2024 v3.0.6) for expert guidance. Multi-platform: iPhone, iPad, iPod touch, Mac (M1+), Apple Vision. Requires iOS 15.0+. Privacy-focused: usage data collected but not linked to user identity.';

        document.getElementsByName('layer_corpus')[0].value = 'Bodybuilding diet apps market highly competitive with established players. Direct competitors: "Bodybuilding Diet & Meal Plan" app, Gaintrain Bulking Meal Planner, MyFitnessPal (50M+ downloads), Lose It!, Cronometer. App Store category: Health & Fitness (highly saturated). Our app rated 4.7/5 stars but only 23 ratings total - critically low social proof. Positive review themes: "easy to use," "macros are accurate," "developer responsive," "already showing results" (2lbs lost in 1 week claim). Users appreciate customization and food library comprehensiveness. Market trend: AI-driven nutrition gaining traction (we added AI chat Dec 2024). Users seek accountability tools and progress tracking. Fitness app market shows high churn - 68% abandon within 30 days industry-wide. App size 115.9 MB - relatively large. Keywords: bodybuilding diet, food calculator, macro tracking.';

        document.getElementsByName('layer_transactional')[0].value = 'App Store presence since 2012 but only 23 total ratings accumulated over 12+ years - extremely low engagement/download volume. Most recent reviews from July-August 2023 (18+ months old) - suggests minimal recent traction. Latest update Dec 26, 2024 added AI Chat but no ratings since then yet. Price points: $9.99/mo standard in market, but also offer $49.99/6mo (16% discount) and $79.99/year (33% discount) - aggressive discounting suggests difficulty converting users. Free tier exists but conversion rate unknown. Developer responsive to support emails per user feedback. No visible marketing campaigns or influencer partnerships. Multi-platform availability (iOS, iPadOS, Mac, Vision) but Android absent - missing 50%+ of mobile market. Recent version 3.0.6 suggests active development, but gap between last reviews (July 2023) and update (Dec 2024) indicates update did not drive new users. User testimonial mentions "competing 10 years ago" - may be resonating with older demographic vs younger fitness trend followers.';

        document.getElementsByName('strengths')[0].value = 'High App Store rating (4.7/5) shows quality product\\nDesigned by actual competition professionals - credibility\\n400k+ food database with smart categorization\\nWeekly macro cycling feature - advanced functionality\\nAI Chat guidance (newly added Dec 2024)\\nMulti-platform support including Apple Vision\\nDeveloper responsive to user questions\\nPrivacy-focused (data not linked to identity)';

        document.getElementsByName('weaknesses')[0].value = 'Only 23 ratings in 12+ years - severe discovery problem\\nNo ratings since AI feature added (Dec 2024) - feature not driving growth\\nLast reviews from July 2023 (18 months stale)\\nNo Android version - missing half the market\\nLarge app size (115.9 MB) may deter downloads\\n"Designed for dedicated users only" - exclusionary positioning\\nNo social/community features visible\\nZero marketing presence or brand awareness';

        document.getElementsByName('opportunities')[0].value = 'AI nutrition trend gaining mainstream adoption\\nApple Vision platform early mover advantage\\nPartnership with bodybuilding gyms and coaches\\nInfluencer marketing in fitness YouTube/Instagram space\\nB2B licensing to personal trainers\\nExpand to Android to double addressable market\\nLeverage existing users for testimonial marketing\\nSEO/ASO optimization to improve App Store visibility\\nIntegration with Apple Health and fitness trackers';

        document.getElementsByName('threats')[0].value = 'Established competitors with massive user bases (MyFitnessPal 50M+)\\nLow rating count signals lack of traction to potential users\\nFitness app market saturation and high churn rates\\nAI feature commoditization - competitors adding similar tools\\nApple policy changes affecting IAP or data collection\\nRising API costs for AI chat functionality\\nUser preference shift toward free/ad-supported models\\nNiche "serious athletes only" positioning limits TAM\\nStale reviews (18 months old) harm conversion rates';
      } else {
        document.getElementsByName('company_name')[0].value = '';
        document.getElementsByName('desired_outcomes')[0].value = '';
        document.getElementsByName('layer_canonical')[0].value = '';
        document.getElementsByName('layer_corpus')[0].value = '';
        document.getElementsByName('layer_transactional')[0].value = '';
        document.getElementsByName('strengths')[0].value = '';
        document.getElementsByName('weaknesses')[0].value = '';
        document.getElementsByName('opportunities')[0].value = '';
        document.getElementsByName('threats')[0].value = '';
      }
    }
  </script>
</head>
<body>
  <h1>SWOT DCIF Engine (v2)</h1>
  <div class="card">
    <p class="muted">This version adds Canonical / Corpus / Transactional layers, structured JSON from the LLM, and a Gap × Impact priority model. It also exposes a JSON API for downstream dashboards.</p>
  </div>

  <form class="card" onsubmit="onSubmit(event)">
    <div style="margin-bottom:20px; padding:12px; background:#e0f2fe; border-radius:6px;">
      <label style="display:flex; align-items:center; cursor:pointer; margin:0;">
        <input type="checkbox" onchange="togglePrefill(this.checked)" style="width:auto; margin-right:8px;">
        <span style="font-weight:bold; color:#0369a1;">Prefill starter info</span>
      </label>
    </div>

    <h2>Company</h2>
    <label>Company Name</label>
    <input type="text" name="company_name" required>
    <label>Desired Outcomes / KPIs</label>
    <textarea name="desired_outcomes" required placeholder="e.g., 30% YoY revenue growth, +10% forecast accuracy"></textarea>

    <h2>Three-Layer Inputs (free text)</h2>
    <div class="small">Provide short summaries for each layer (paste notes, bullet points, extracts). You can start with Canonical only—Corpus/Transactional are optional placeholders you can wire up later.</div>
    <label>Canonical (Internal Truth)</label>
    <textarea name="layer_canonical" placeholder="Playbooks, strategy docs, positioning…"></textarea>
    <label>Corpus (External Truth)</label>
    <textarea name="layer_corpus" placeholder="Market chatter, analyst notes, reviews, competitor messaging…"></textarea>
    <label>Transactional (Internal Reality)</label>
    <textarea name="layer_transactional" placeholder="Sales call patterns, objections, win/loss insights…"></textarea>

    <h2>(Optional) Canonical Quadrant Seed Inputs</h2>
    <div class="grid">
      <div>
        <label>Strengths (one per line)</label>
        <textarea name="strengths"></textarea>
      </div>
      <div>
        <label>Weaknesses (one per line)</label>
        <textarea name="weaknesses"></textarea>
      </div>
    </div>
    <div class="grid">
      <div>
        <label>Opportunities (one per line)</label>
        <textarea name="opportunities"></textarea>
      </div>
      <div>
        <label>Threats (one per line)</label>
        <textarea name="threats"></textarea>
      </div>
    </div>

    <div id="status" class="status"></div>
    <br>
    <button id="submitBtn" class="btn" type="submit">Analyze</button>
  </form>

  <div class="card">
    <p class="small">Tip: After a run, your JSON will be available at <code>/api/result?id=&lt;run_id&gt;</code> for visualization.</p>
  </div>
</body>
</html>
"""


def generate_visualization_html(summary: RunSummary) -> str:
    """Generate beautiful interactive HTML visualization of SWOT analysis."""

    # Prepare data for JavaScript
    data_json = json.dumps(summary.model_dump())

    # Helper to render items for a quadrant/layer
    def render_items(items: List[SWOTItem]) -> str:
        if not items:
            return '<div class="swot-item empty-item">No items</div>'
        return ''.join([
            f'<div class="swot-item"><span class="impact-badge">{item.impact}</span><span>{item.text}</span></div>'
            for item in items
        ])

    return f"""
    <div class="card">
        <h2>Interactive SWOT Visualization</h2>
        <div style="margin-bottom: 20px;">
            <button class="view-btn active" onclick="showView('matrix')">SWOT Matrix</button>
            <button class="view-btn" onclick="showView('layers')">Layer Comparison</button>
            <button class="view-btn" onclick="showView('impact')">Impact Analysis</button>
        </div>

        <!-- SWOT Matrix View -->
        <div id="matrix-view" class="viz-view">
            <div class="swot-grid">
                <div class="swot-quadrant strengths-quad">
                    <h3>💪 Strengths</h3>
                    <div class="layer-items">
                        <div class="layer-section">
                            <span class="layer-badge canonical">Canonical</span>
                            {render_items(summary.canonical.strengths)}
                        </div>
                        <div class="layer-section">
                            <span class="layer-badge corpus">Corpus</span>
                            {render_items(summary.corpus.strengths)}
                        </div>
                        <div class="layer-section">
                            <span class="layer-badge transactional">Transactional</span>
                            {render_items(summary.transactional.strengths)}
                        </div>
                    </div>
                </div>

                <div class="swot-quadrant weaknesses-quad">
                    <h3>⚠️ Weaknesses</h3>
                    <div class="layer-items">
                        <div class="layer-section">
                            <span class="layer-badge canonical">Canonical</span>
                            {render_items(summary.canonical.weaknesses)}
                        </div>
                        <div class="layer-section">
                            <span class="layer-badge corpus">Corpus</span>
                            {render_items(summary.corpus.weaknesses)}
                        </div>
                        <div class="layer-section">
                            <span class="layer-badge transactional">Transactional</span>
                            {render_items(summary.transactional.weaknesses)}
                        </div>
                    </div>
                </div>

                <div class="swot-quadrant opportunities-quad">
                    <h3>🚀 Opportunities</h3>
                    <div class="layer-items">
                        <div class="layer-section">
                            <span class="layer-badge canonical">Canonical</span>
                            {render_items(summary.canonical.opportunities)}
                        </div>
                        <div class="layer-section">
                            <span class="layer-badge corpus">Corpus</span>
                            {render_items(summary.corpus.opportunities)}
                        </div>
                        <div class="layer-section">
                            <span class="layer-badge transactional">Transactional</span>
                            {render_items(summary.transactional.opportunities)}
                        </div>
                    </div>
                </div>

                <div class="swot-quadrant threats-quad">
                    <h3>🛡️ Threats</h3>
                    <div class="layer-items">
                        <div class="layer-section">
                            <span class="layer-badge canonical">Canonical</span>
                            {render_items(summary.canonical.threats)}
                        </div>
                        <div class="layer-section">
                            <span class="layer-badge corpus">Corpus</span>
                            {render_items(summary.corpus.threats)}
                        </div>
                        <div class="layer-section">
                            <span class="layer-badge transactional">Transactional</span>
                            {render_items(summary.transactional.threats)}
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Layer Comparison View -->
        <div id="layers-view" class="viz-view" style="display:none;">
            <div class="layers-container">
                <div class="layer-card">
                    <h3>📋 Canonical Layer</h3>
                    <p class="layer-desc">Internal truth from strategy docs and playbooks</p>
                    <div class="layer-stats">
                        <div class="stat">
                            <span class="stat-label">Strengths</span>
                            <span class="stat-value">{len(summary.canonical.strengths)}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Weaknesses</span>
                            <span class="stat-value">{len(summary.canonical.weaknesses)}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Opportunities</span>
                            <span class="stat-value">{len(summary.canonical.opportunities)}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Threats</span>
                            <span class="stat-value">{len(summary.canonical.threats)}</span>
                        </div>
                    </div>
                </div>

                <div class="layer-card">
                    <h3>🌐 Corpus Layer</h3>
                    <p class="layer-desc">External truth from market and competitor data</p>
                    <div class="layer-stats">
                        <div class="stat">
                            <span class="stat-label">Strengths</span>
                            <span class="stat-value">{len(summary.corpus.strengths)}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Weaknesses</span>
                            <span class="stat-value">{len(summary.corpus.weaknesses)}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Opportunities</span>
                            <span class="stat-value">{len(summary.corpus.opportunities)}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Threats</span>
                            <span class="stat-value">{len(summary.corpus.threats)}</span>
                        </div>
                    </div>
                </div>

                <div class="layer-card">
                    <h3>💼 Transactional Layer</h3>
                    <p class="layer-desc">Internal reality from sales and operations data</p>
                    <div class="layer-stats">
                        <div class="stat">
                            <span class="stat-label">Strengths</span>
                            <span class="stat-value">{len(summary.transactional.strengths)}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Weaknesses</span>
                            <span class="stat-value">{len(summary.transactional.weaknesses)}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Opportunities</span>
                            <span class="stat-value">{len(summary.transactional.opportunities)}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Threats</span>
                            <span class="stat-value">{len(summary.transactional.threats)}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Impact Analysis View -->
        <div id="impact-view" class="viz-view" style="display:none;">
            <canvas id="impactChart" width="800" height="400"></canvas>
        </div>
    </div>

    <style>
        .view-btn {{
            background: #e5e7eb;
            color: #374151;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            margin-right: 8px;
            font-size: 14px;
            transition: all 0.3s;
        }}
        .view-btn:hover {{
            background: #d1d5db;
        }}
        .view-btn.active {{
            background: #2d7a46;
            color: white;
        }}

        .swot-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-top: 20px;
        }}

        .swot-quadrant {{
            padding: 20px;
            border-radius: 8px;
            min-height: 300px;
        }}

        .strengths-quad {{
            background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
            border: 2px solid #34d399;
        }}

        .weaknesses-quad {{
            background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
            border: 2px solid #f87171;
        }}

        .opportunities-quad {{
            background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
            border: 2px solid #60a5fa;
        }}

        .threats-quad {{
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border: 2px solid #fbbf24;
        }}

        .swot-quadrant h3 {{
            margin: 0 0 16px 0;
            font-size: 18px;
            color: #1f2937;
        }}

        .layer-section {{
            margin-bottom: 16px;
        }}

        .layer-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
            margin-bottom: 8px;
        }}

        .layer-badge.canonical {{
            background: #3b82f6;
            color: white;
        }}

        .layer-badge.corpus {{
            background: #8b5cf6;
            color: white;
        }}

        .layer-badge.transactional {{
            background: #ec4899;
            color: white;
        }}

        .swot-item {{
            background: rgba(255, 255, 255, 0.9);
            padding: 10px;
            margin: 6px 0;
            border-radius: 6px;
            font-size: 13px;
            line-height: 1.5;
            display: flex;
            align-items: flex-start;
            gap: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}

        .swot-item.empty-item {{
            color: #9ca3af;
            font-style: italic;
            justify-content: center;
        }}

        .impact-badge {{
            background: #1f2937;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: bold;
            min-width: 24px;
            text-align: center;
            flex-shrink: 0;
        }}

        .layers-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}

        .layer-card {{
            background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
            padding: 24px;
            border-radius: 8px;
            border: 2px solid #e5e7eb;
        }}

        .layer-card h3 {{
            margin: 0 0 8px 0;
            color: #1f2937;
        }}

        .layer-desc {{
            color: #6b7280;
            font-size: 13px;
            margin: 0 0 16px 0;
        }}

        .layer-stats {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }}

        .stat {{
            background: white;
            padding: 12px;
            border-radius: 6px;
            text-align: center;
        }}

        .stat-label {{
            display: block;
            font-size: 11px;
            color: #6b7280;
            text-transform: uppercase;
            margin-bottom: 4px;
        }}

        .stat-value {{
            display: block;
            font-size: 24px;
            font-weight: bold;
            color: #2d7a46;
        }}
    </style>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <script>
        const swotData = {data_json};

        function showView(viewName) {{
            document.querySelectorAll('.viz-view').forEach(v => v.style.display = 'none');
            document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));

            document.getElementById(viewName + '-view').style.display = 'block';
            event.target.classList.add('active');

            if (viewName === 'impact') {{
                renderImpactChart();
            }}
        }}

        function renderImpactChart() {{
            const ctx = document.getElementById('impactChart');
            if (ctx.chart) {{
                ctx.chart.destroy();
            }}

            const priorities = swotData.priorities.ranked;

            ctx.chart = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: priorities.map(p => p.dimension.charAt(0).toUpperCase() + p.dimension.slice(1)),
                    datasets: [
                        {{
                            label: 'Priority Score',
                            data: priorities.map(p => p.priority),
                            backgroundColor: ['#34d399', '#f87171', '#60a5fa', '#fbbf24'],
                            borderColor: ['#10b981', '#ef4444', '#3b82f6', '#f59e0b'],
                            borderWidth: 2
                        }},
                        {{
                            label: 'Gap',
                            data: priorities.map(p => p.gap),
                            backgroundColor: 'rgba(99, 102, 241, 0.5)',
                            borderColor: 'rgb(99, 102, 241)',
                            borderWidth: 2
                        }},
                        {{
                            label: 'Impact Mean',
                            data: priorities.map(p => p.impact_mean),
                            backgroundColor: 'rgba(236, 72, 153, 0.5)',
                            borderColor: 'rgb(236, 72, 153)',
                            borderWidth: 2
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {{
                        legend: {{
                            position: 'top',
                        }},
                        title: {{
                            display: true,
                            text: 'SWOT Priority Analysis (Gap × Impact)',
                            font: {{ size: 16 }}
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            title: {{
                                display: true,
                                text: 'Score'
                            }}
                        }}
                    }}
                }}
            }});
        }}
    </script>
    """


def generate_results_html(summary: RunSummary, viz_html: str) -> str:
    """Generate complete results page HTML."""
    pretty_json = json.dumps(summary.model_dump(), indent=2)

    return f"""
<!DOCTYPE html>
<html>
<head>
  <title>SWOT DCIF Results – {summary.company}</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 24px; background:#f5f5f5; }}
    h1 {{ color: #1f2937; margin-bottom: 8px; }}
    .card {{ background:#fff; border-radius:8px; padding:20px; box-shadow:0 2px 8px rgba(0,0,0,0.06); margin-bottom:20px; }}
    pre {{ background:#0f172a; color:#e2e8f0; padding:16px; border-radius:8px; overflow:auto; font-size: 12px; }}
    a.btn {{ display:inline-block; background:#2d7a46; color:#fff; padding:10px 14px; border-radius:6px; text-decoration:none; }}
    a.btn:hover {{ background:#25663a; }}
    .pill {{ display:inline-block; padding:4px 10px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-left:6px; }}
    table {{ width:100%; border-collapse: collapse; }}
    th, td {{ text-align:left; padding:10px; border-bottom:1px solid #eee; }}
    th {{ background:#f9fafb; font-weight:600; color:#374151; }}
    tr:hover {{ background:#f9fafb; }}
    .expand-btn {{
      background: #6b7280;
      color: white;
      border: none;
      padding: 8px 16px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 14px;
      margin-top: 12px;
    }}
    .expand-btn:hover {{ background: #4b5563; }}
    .json-section {{ display: none; margin-top: 16px; }}
    .json-section.expanded {{ display: block; }}
  </style>
  <script>
    function toggleJson() {{
      const section = document.getElementById('jsonSection');
      const btn = document.getElementById('toggleBtn');
      section.classList.toggle('expanded');
      btn.textContent = section.classList.contains('expanded') ? '▼ Hide Full JSON' : '▶ Show Full JSON';
    }}
  </script>
</head>
<body>
  <h1>SWOT DCIF Results – {summary.company}</h1>
  <div class="card">
    <p><strong>Run ID:</strong> <code>{summary.run_id}</code></p>
    <p><strong>Desired Outcomes:</strong> {summary.desired_outcomes}</p>
    <p>
      <a class="btn" href="/">← New Analysis</a>
      &nbsp;&nbsp;
      <a class="btn" href="/api/result?id={summary.run_id}">View JSON API</a>
    </p>
  </div>

  <div class="card">
    <h2>Top Priorities <span class="pill">Gap × Impact</span></h2>
    <table>
      <tr><th>Dimension</th><th>Priority</th><th>Gap</th><th>Impact Mean</th></tr>
      {''.join([
        f"<tr><td><b>{r['dimension'].title()}</b></td><td><b>{r['priority']}</b></td><td>{r['gap']}</td><td>{r['impact_mean']}</td></tr>"
        for r in summary.priorities['ranked']
      ])}
    </table>
  </div>

  {viz_html}

  <div class="card">
    <h2>Data Export</h2>
    <p>Access the complete structured data via the API endpoint or expand the JSON below.</p>
    <button id="toggleBtn" class="expand-btn" onclick="toggleJson()">▶ Show Full JSON</button>
    <div id="jsonSection" class="json-section">
      <pre>{pretty_json}</pre>
    </div>
  </div>

  <div class="card">
    <p style="font-size: 13px; color: #6b7280;">
      💡 <strong>Tip:</strong> Use <code>/api/result?id={summary.run_id}</code> for dashboards, 3D SWOT maps, or to compare runs over time.
    </p>
  </div>
</body>
</html>
"""
