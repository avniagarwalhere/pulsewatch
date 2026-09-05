import random
from datetime import datetime, timedelta

DEFAULT_CATALYSTS = {
    'NVDA': [
        {'title': 'Hyperscale Cloud AI Cluster Expansion Announced', 'desc': 'Tier 1 cloud providers increase multi-billion Blackwell accelerator orders, boosting FY27 datacenter guidance.', 'category': 'Earnings', 'impact': 95, 'sentiment': 'Bullish', 'time_offset_min': 15},
        {'title': 'Tier-1 Semiconductor Foundry Capacity Uplift', 'desc': 'Packaging yield improves by 18%, relieving near-term delivery bottleneck.', 'category': 'Supply Chain', 'impact': 82, 'sentiment': 'Bullish', 'time_offset_min': 90},
        {'title': 'Analyst Consensus Price Target Raised to $165', 'desc': 'Wall Street upgrades on expanding gross margins above 76%.', 'category': 'Analyst', 'impact': 78, 'sentiment': 'Bullish', 'time_offset_min': 240},
    ],
    'TSLA': [
        {'title': 'NHTSA Expands FSD Software Safety Assessment', 'desc': 'Regulators request telemetry logs on full-self driving disengagements in low-visibility conditions.', 'category': 'Regulatory', 'impact': 88, 'sentiment': 'Bearish', 'time_offset_min': 35},
        {'title': 'European EV Incentive Revision Draft Released', 'desc': 'Subsidy qualifications narrow for imported assembly architectures.', 'category': 'Macro', 'impact': 74, 'sentiment': 'Bearish', 'time_offset_min': 180},
        {'title': 'Next-Gen Cybercab Prototype Factory Tooling Initiated', 'desc': 'Gigafactory Austin initiates pilot robotics calibration for unboxed platform.', 'category': 'Product', 'impact': 80, 'sentiment': 'Bullish', 'time_offset_min': 360},
    ],
    'AAPL': [
        {'title': 'Apple Intelligence Siri LLM Beta Expands Globally', 'desc': 'On-device contextual neural models roll out to developer preview in 12 new regions.', 'category': 'Product', 'impact': 84, 'sentiment': 'Bullish', 'time_offset_min': 45},
        {'title': 'Services Revenue Hits Record Trajectory in EU', 'desc': 'App Store alternative fee adjustments maintain 88% gross margin resilience.', 'category': 'Earnings', 'impact': 76, 'sentiment': 'Bullish', 'time_offset_min': 210},
    ],
    'MSFT': [
        {'title': 'Azure AI Customer Annual Run Rate Surpasses $14B', 'desc': 'Enterprise Copilot seat penetration doubles across Fortune 500 accounts.', 'category': 'Earnings', 'impact': 90, 'sentiment': 'Bullish', 'time_offset_min': 60},
        {'title': 'Data Center Clean Energy Power Purchase Agreement Finalized', 'desc': 'Secures 1.2 GW of dedicated nuclear & geothermal capacity.', 'category': 'Operations', 'impact': 70, 'sentiment': 'Bullish', 'time_offset_min': 300},
    ],
    'AMZN': [
        {'title': 'AWS Custom Silicon Trainium3 Launch Confirmed', 'desc': 'Promises 40% compute cost reduction for frontier model fine-tuning.', 'category': 'Product', 'impact': 86, 'sentiment': 'Bullish', 'time_offset_min': 80},
        {'title': 'Prime Same-Day Delivery Logistics Efficiency Gains', 'desc': 'Regional fulfillment center automation reduces cost per unit by 65 cents.', 'category': 'Operations', 'impact': 72, 'sentiment': 'Bullish', 'time_offset_min': 340},
    ],
    'GOOGL': [
        {'title': 'Gemini 2.5 Multi-Agent Enterprise Suite Released', 'desc': 'New agentic reasoning model tops industry latency and SWE benchmarks.', 'category': 'Product', 'impact': 89, 'sentiment': 'Bullish', 'time_offset_min': 50},
        {'title': 'DOJ Search Remedy Hearing Concludes Opening Arguments', 'desc': 'Court evaluates potential browser distribution non-exclusivity provisions.', 'category': 'Regulatory', 'impact': 85, 'sentiment': 'Bearish', 'time_offset_min': 150},
    ],
    'META': [
        {'title': 'Llama 4 Open Weights Milestone Published', 'desc': 'Surpasses proprietary frontier benchmarks while running locally on enterprise clusters.', 'category': 'Product', 'impact': 91, 'sentiment': 'Bullish', 'time_offset_min': 110},
        {'title': 'Advantage+ AI Ad Platform Conversion Lift +22%', 'desc': 'Advertiser ROAS surges following automated video creative generation rollout.', 'category': 'Earnings', 'impact': 87, 'sentiment': 'Bullish', 'time_offset_min': 280},
    ],
    'AMD': [
        {'title': 'MI350X Accelerator Enterprise Shipments Accelerate', 'desc': 'Wins 3 major tier-2 CSP cluster deployments totaling 80,000 units.', 'category': 'Earnings', 'impact': 86, 'sentiment': 'Bullish', 'time_offset_min': 75},
        {'title': 'Server CPU Market Share Expands to 34.5%', 'desc': 'EPYC Turin chips gain traction in enterprise virtualization refreshes.', 'category': 'Market Share', 'impact': 80, 'sentiment': 'Bullish', 'time_offset_min': 320},
    ],
    'PLTR': [
        {'title': 'US Defense Agency Multi-Year AIP Expansion Signed', 'desc': '$450M defense logistics and battlefield intelligence modernization contract awarded.', 'category': 'Contract', 'impact': 93, 'sentiment': 'Bullish', 'time_offset_min': 25},
        {'title': 'Commercial AIP Bootcamps Surpass 1,800 Enterprises', 'desc': 'Sales cycle contracts from 6 months to 14 days.', 'category': 'Earnings', 'impact': 85, 'sentiment': 'Bullish', 'time_offset_min': 200},
    ],
    'COIN': [
        {'title': 'Base Network TVL Crosses $12B with Record Fee Generation', 'desc': 'Layer-2 sequencer revenue contributes 18% of annualized net income.', 'category': 'Product', 'impact': 88, 'sentiment': 'Bullish', 'time_offset_min': 40},
        {'title': 'Institutional Custody Inflows Surge 45% Post-ETF Inflows', 'desc': 'Spot asset staking participation rate hits 18-month high.', 'category': 'Flows', 'impact': 82, 'sentiment': 'Bullish', 'time_offset_min': 260},
    ]
}

def get_catalysts_for_symbol(symbol: str, count: int = 4):
    sym = symbol.upper()
    now = datetime.utcnow()
    raw_list = DEFAULT_CATALYSTS.get(sym, [
        {'title': f'{sym} Trading Activity Surge', 'desc': 'Intraday volume and liquidity flow shifted above standard deviation thresholds.', 'category': 'Technical', 'impact': 65, 'sentiment': 'Neutral', 'time_offset_min': 60},
        {'title': f'{sym} Sector Rotation & Rebalancing', 'desc': 'Institutional index rebalancing flows impacting short term order depth.', 'category': 'Macro', 'impact': 60, 'sentiment': 'Neutral', 'time_offset_min': 180}
    ])
    
    result = []
    for item in raw_list[:count]:
        ts = now - timedelta(minutes=item.get('time_offset_min', 60))
        result.append({
            'title': item['title'],
            'description': item['desc'],
            'category': item['category'],
            'impact_score': item['impact'],
            'sentiment': item.get('sentiment', 'Neutral'),
            'timestamp': ts.isoformat() + 'Z',
            'time_ago': format_time_ago(ts)
        })
    return result

def format_time_ago(dt: datetime) -> str:
    diff = datetime.utcnow() - dt
    secs = int(diff.total_seconds())
    if secs < 60:
        return f'{secs}s ago'
    mins = secs // 60
    if mins < 60:
        return f'{mins}m ago'
    hrs = mins // 60
    if hrs < 24:
        return f'{hrs}h {mins % 60}m ago'
    days = hrs // 24
    return f'{days}d ago'
