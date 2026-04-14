import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Bhagwati Industries – Production Tracker",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
STAGES = [
    "Drawing Received",
    "Drawing Approval / Clarifications",
    "Material Planning",
    "Plate Cutting",
    "Bending",
    "Fit-up (Main Tank)",
    "Welding (Main Tank)",
    "HV Port Fit-up Complete",
    "LV Port Fit-up Complete",
    "Conservator Fit-up Complete",
    "Pipeline Fit-up Complete",
    "Grinding / Finishing",
    "Leak Test / Inspection",
    "Final Assembly",
    "Painting",
    "Dispatch Preparation",
    "Dispatch Done"
]

CRITICAL_STAGES = [
    "HV Port Fit-up Complete",
    "LV Port Fit-up Complete",
    "Conservator Fit-up Complete",
    "Pipeline Fit-up Complete"
]

STATUS_OPTIONS = ["Not Started", "In Progress", "Completed", "Hold"]
PRIORITY_OPTIONS = ["High", "Medium", "Low"]

EMPLOYEES = [
    "Rajesh Kumar", "Amit Shah", "Suresh Patel", "Dinesh Verma",
    "Mahesh Joshi", "Nilesh Desai", "Prakash Modi", "Vikas Sharma",
    "Ravi Tiwari", "Sandip Rao"
]

TANK_TYPES = [
    "100 KVA Distribution", "250 KVA Distribution", "500 KVA Distribution",
    "1 MVA Power", "2.5 MVA Power", "5 MVA Power", "10 MVA Power",
    "33 KV Substation", "66 KV Substation", "Custom Specialty"
]

CLIENTS = [
    "GETCO Gujarat", "MSEDCL Maharashtra", "PGCIL National",
    "Torrent Power", "Adani Transmission", "BSES Delhi",
    "CESC Kolkata", "KSEB Kerala", "TNEB Tamil Nadu", "APDCL Assam"
]

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&family=Barlow:wght@300;400;500;600&display=swap');

/* Root variables */
:root {
    --bg-primary: #0a0e1a;
    --bg-secondary: #0f1629;
    --bg-card: #131c2e;
    --bg-card-hover: #1a2540;
    --accent-blue: #1e90ff;
    --accent-cyan: #00d4ff;
    --accent-orange: #ff6b35;
    --accent-green: #00e676;
    --accent-yellow: #ffd600;
    --accent-red: #ff1744;
    --text-primary: #e8edf5;
    --text-secondary: #8899aa;
    --border: rgba(30, 144, 255, 0.2);
    --border-bright: rgba(30, 144, 255, 0.5);
}

/* Global */
.stApp {
    background: var(--bg-primary);
    font-family: 'Barlow', sans-serif;
    color: var(--text-primary);
}

/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1rem 2rem; max-width: 100%; }

/* Sidebar */
.css-1d391kg, [data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
}

/* Header banner */
.dashboard-header {
    background: linear-gradient(135deg, #0f1629 0%, #131c2e 50%, #0a1428 100%);
    border: 1px solid var(--border-bright);
    border-radius: 8px;
    padding: 20px 28px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.dashboard-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent-cyan), var(--accent-blue), transparent);
}
.dashboard-header h1 {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
    letter-spacing: 2px;
    text-transform: uppercase;
}
.dashboard-header p {
    color: var(--text-secondary);
    margin: 4px 0 0;
    font-size: 0.85rem;
    font-family: 'Share Tech Mono', monospace;
    letter-spacing: 1px;
}
.header-badge {
    display: inline-block;
    background: rgba(30,144,255,0.15);
    border: 1px solid rgba(30,144,255,0.4);
    border-radius: 4px;
    padding: 2px 10px;
    font-size: 0.7rem;
    color: var(--accent-cyan);
    font-family: 'Share Tech Mono', monospace;
    letter-spacing: 1px;
    margin-top: 8px;
}

/* Metric cards */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 18px 20px;
    position: relative;
    overflow: hidden;
    transition: all 0.2s;
}
.metric-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
}
.metric-card.blue::after { background: var(--accent-blue); }
.metric-card.green::after { background: var(--accent-green); }
.metric-card.red::after { background: var(--accent-red); }
.metric-card.orange::after { background: var(--accent-orange); }
.metric-card.yellow::after { background: var(--accent-yellow); }

.metric-value {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.4rem;
    font-weight: 700;
    line-height: 1;
    margin: 4px 0;
}
.metric-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: var(--text-secondary);
    font-family: 'Share Tech Mono', monospace;
}
.metric-icon { font-size: 1.4rem; margin-bottom: 6px; }
.metric-card.blue .metric-value { color: var(--accent-blue); }
.metric-card.green .metric-value { color: var(--accent-green); }
.metric-card.red .metric-value { color: var(--accent-red); }
.metric-card.orange .metric-value { color: var(--accent-orange); }
.metric-card.yellow .metric-value { color: var(--accent-yellow); }

/* Section headers */
.section-header {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--accent-cyan);
    border-bottom: 1px solid var(--border);
    padding-bottom: 8px;
    margin: 20px 0 14px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Kanban */
.kanban-col {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px;
    min-height: 160px;
}
.kanban-col-header {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 10px;
    padding: 6px 10px;
    border-radius: 4px;
    text-align: center;
}
.kanban-card {
    background: var(--bg-secondary);
    border-radius: 6px;
    padding: 8px 10px;
    margin-bottom: 8px;
    border-left: 3px solid;
    font-size: 0.82rem;
}
.kanban-card.completed { border-color: var(--accent-green); }
.kanban-card.in-progress { border-color: var(--accent-yellow); }
.kanban-card.hold { border-color: var(--accent-red); }
.kanban-card.not-started { border-color: var(--text-secondary); }
.kanban-tag {
    display: inline-block;
    font-size: 0.65rem;
    padding: 1px 6px;
    border-radius: 10px;
    margin-top: 4px;
    font-family: 'Share Tech Mono', monospace;
}
.tag-high { background: rgba(255,23,68,0.2); color: var(--accent-red); }
.tag-medium { background: rgba(255,214,0,0.2); color: var(--accent-yellow); }
.tag-low { background: rgba(0,230,118,0.2); color: var(--accent-green); }
.tag-critical { background: rgba(255,107,53,0.2); color: var(--accent-orange); }

/* Status pills */
.pill {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.72rem;
    font-weight: 600;
    font-family: 'Share Tech Mono', monospace;
    letter-spacing: 0.5px;
}
.pill-completed { background: rgba(0,230,118,0.15); color: #00e676; border: 1px solid rgba(0,230,118,0.3); }
.pill-progress  { background: rgba(255,214,0,0.15);  color: #ffd600; border: 1px solid rgba(255,214,0,0.3); }
.pill-hold      { background: rgba(255,23,68,0.15);  color: #ff1744; border: 1px solid rgba(255,23,68,0.3); }
.pill-notstart  { background: rgba(136,153,170,0.15); color: #8899aa; border: 1px solid rgba(136,153,170,0.3); }

/* Table styles */
.styled-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.82rem;
}
.styled-table th {
    background: rgba(30,144,255,0.1);
    color: var(--accent-cyan);
    padding: 8px 12px;
    text-align: left;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 1px;
    border-bottom: 1px solid var(--border-bright);
}
.styled-table td {
    padding: 7px 12px;
    border-bottom: 1px solid var(--border);
    color: var(--text-primary);
}
.styled-table tr:hover td { background: var(--bg-card-hover); }
.delayed-row td { background: rgba(255,23,68,0.04) !important; }

/* Alert boxes */
.alert-box {
    padding: 10px 14px;
    border-radius: 6px;
    margin: 6px 0;
    font-size: 0.82rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
.alert-red { background: rgba(255,23,68,0.1); border: 1px solid rgba(255,23,68,0.3); color: #ff6b6b; }
.alert-yellow { background: rgba(255,214,0,0.08); border: 1px solid rgba(255,214,0,0.3); color: #ffd600; }
.alert-green { background: rgba(0,230,118,0.08); border: 1px solid rgba(0,230,118,0.3); color: #00e676; }

/* Progress bar */
.prog-bar-wrap { background: rgba(255,255,255,0.06); border-radius: 4px; height: 6px; overflow: hidden; }
.prog-bar-fill { height: 100%; border-radius: 4px; }

/* Divider */
hr { border: none; border-top: 1px solid var(--border); margin: 16px 0; }

/* Streamlit overrides */
.stSelectbox > div > div { background: var(--bg-card) !important; border-color: var(--border-bright) !important; color: var(--text-primary) !important; }
.stTextInput > div > div { background: var(--bg-card) !important; border-color: var(--border-bright) !important; }
.stDateInput > div > div { background: var(--bg-card) !important; border-color: var(--border-bright) !important; }
.stButton > button {
    background: rgba(30,144,255,0.15) !important;
    border: 1px solid rgba(30,144,255,0.5) !important;
    color: var(--accent-cyan) !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}
.stButton > button:hover {
    background: rgba(30,144,255,0.3) !important;
    border-color: var(--accent-blue) !important;
}
div[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}
.stTabs [data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1px solid var(--border) !important; }
.stTabs [data-baseweb="tab"] { color: var(--text-secondary) !important; font-family: 'Rajdhani', sans-serif !important; font-weight: 600 !important; letter-spacing: 1px !important; text-transform: uppercase !important; }
.stTabs [aria-selected="true"] { color: var(--accent-cyan) !important; border-bottom: 2px solid var(--accent-cyan) !important; }
[data-testid="stMetricValue"] { color: var(--accent-blue) !important; font-family: 'Rajdhani', sans-serif !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE / DATA INIT
# ─────────────────────────────────────────────
def init_sample_data():
    today = datetime.today().date()

    # ── Orders ──────────────────────────────────
    orders = pd.DataFrame([
        {"Order_ID": "ORD-001", "Client_Name": "GETCO Gujarat",      "Tank_Type": "100 KVA Distribution", "Quantity": 3, "Drawing_Receipt_Date": today - timedelta(days=30), "Committed_Dispatch": today + timedelta(days=10), "Priority": "High"},
        {"Order_ID": "ORD-002", "Client_Name": "MSEDCL Maharashtra", "Tank_Type": "250 KVA Distribution", "Quantity": 2, "Drawing_Receipt_Date": today - timedelta(days=20), "Committed_Dispatch": today + timedelta(days=20), "Priority": "Medium"},
        {"Order_ID": "ORD-003", "Client_Name": "Torrent Power",      "Tank_Type": "1 MVA Power",           "Quantity": 1, "Drawing_Receipt_Date": today - timedelta(days=45), "Committed_Dispatch": today - timedelta(days=3),  "Priority": "High"},
        {"Order_ID": "ORD-004", "Client_Name": "Adani Transmission", "Tank_Type": "5 MVA Power",           "Quantity": 2, "Drawing_Receipt_Date": today - timedelta(days=15), "Committed_Dispatch": today + timedelta(days=30), "Priority": "Low"},
        {"Order_ID": "ORD-005", "Client_Name": "PGCIL National",     "Tank_Type": "10 MVA Power",          "Quantity": 1, "Drawing_Receipt_Date": today - timedelta(days=60), "Committed_Dispatch": today + timedelta(days=5),  "Priority": "High"},
    ])

    # ── Production Tracking ───────────────────
    def make_tank_stages(order_id, tank_id, priority, current_stage_idx, assigned_map, delay_days=0):
        rows = []
        for i, stage in enumerate(STAGES):
            if i < current_stage_idx:
                status = "Completed"
                start_dt = today - timedelta(days=(len(STAGES) - i) * 2 + delay_days)
                end_dt   = start_dt + timedelta(days=1)
            elif i == current_stage_idx:
                status = "In Progress"
                start_dt = today - timedelta(days=2)
                end_dt   = None
            else:
                status = "Not Started"
                start_dt = None
                end_dt   = None

            person = assigned_map.get(i, assigned_map.get(0, EMPLOYEES[0]))
            exp_end = (today - timedelta(days=delay_days)) if status == "In Progress" else None
            delay = (today - exp_end).days if (exp_end and status == "In Progress" and today > exp_end) else 0

            rows.append({
                "Order_ID":      order_id,
                "Tank_ID":       tank_id,
                "Stage_Name":    stage,
                "Stage_No":      i + 1,
                "Stage_Status":  status,
                "Assigned_Person": person,
                "Start_Date":    start_dt,
                "End_Date":      end_dt,
                "Remarks":       "",
                "Delay_Days":    delay,
                "Is_Critical":   stage in CRITICAL_STAGES,
                "Priority":      priority,
            })
        return rows

    tracks = []
    # ORD-001: 3 tanks (different stages)
    tracks += make_tank_stages("ORD-001", "TK-001-A", "High",   12, {0: "Rajesh Kumar",  7: "Amit Shah",  12: "Suresh Patel"}, delay_days=5)
    tracks += make_tank_stages("ORD-001", "TK-001-B", "High",   10, {0: "Dinesh Verma",  7: "Mahesh Joshi", 10: "Nilesh Desai"}, delay_days=3)
    tracks += make_tank_stages("ORD-001", "TK-001-C", "High",    7, {0: "Prakash Modi",  7: "Vikas Sharma"}, delay_days=0)
    # ORD-002: 2 tanks
    tracks += make_tank_stages("ORD-002", "TK-002-A", "Medium",  5, {0: "Ravi Tiwari",   5: "Sandip Rao"}, delay_days=0)
    tracks += make_tank_stages("ORD-002", "TK-002-B", "Medium",  3, {0: "Rajesh Kumar",  3: "Amit Shah"},  delay_days=2)
    # ORD-003: 1 tank (nearly done but delayed)
    tracks += make_tank_stages("ORD-003", "TK-003-A", "High",   15, {0: "Suresh Patel", 14: "Dinesh Verma", 15: "Mahesh Joshi"}, delay_days=8)
    # ORD-004: 2 tanks
    tracks += make_tank_stages("ORD-004", "TK-004-A", "Low",     2, {0: "Nilesh Desai",  2: "Prakash Modi"}, delay_days=0)
    tracks += make_tank_stages("ORD-004", "TK-004-B", "Low",     1, {0: "Vikas Sharma"}, delay_days=0)
    # ORD-005: 1 tank (on hold mid-way)
    stages_005 = make_tank_stages("ORD-005", "TK-005-A", "High", 8, {0: "Ravi Tiwari", 8: "Sandip Rao"}, delay_days=10)
    stages_005[8]["Stage_Status"] = "Hold"
    stages_005[8]["Remarks"] = "Waiting for customer clarification on HV port spec"
    tracks += stages_005

    tracking_df = pd.DataFrame(tracks)
    return orders, tracking_df

if "orders" not in st.session_state or "tracking" not in st.session_state:
    st.session_state.orders, st.session_state.tracking = init_sample_data()

orders_df   = st.session_state.orders
tracking_df = st.session_state.tracking

# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────
def recalc_delays(df):
    today = datetime.today().date()
    # Simplified: for In Progress stages, recalc delay
    # Expected per stage ~ 2 days
    def calc(row):
        if row["Stage_Status"] == "In Progress" and row["Start_Date"] is not None:
            exp_end = row["Start_Date"] + timedelta(days=2)
            d = (today - exp_end).days
            return max(0, d)
        return row["Delay_Days"]
    df["Delay_Days"] = df.apply(calc, axis=1)
    return df

def get_tank_current_stage(tank_id, df):
    t = df[df["Tank_ID"] == tank_id]
    ip = t[t["Stage_Status"] == "In Progress"]
    if not ip.empty:
        return ip.iloc[0]["Stage_Name"], ip.iloc[0]["Stage_No"]
    hold = t[t["Stage_Status"] == "Hold"]
    if not hold.empty:
        return hold.iloc[0]["Stage_Name"], hold.iloc[0]["Stage_No"]
    comp = t[t["Stage_Status"] == "Completed"]
    if len(comp) == len(STAGES):
        return "Dispatch Done", 17
    ns = t[t["Stage_Status"] == "Not Started"]
    if not ns.empty:
        return ns.iloc[0]["Stage_Name"], ns.iloc[0]["Stage_No"]
    return "Unknown", 0

def get_tank_progress_pct(tank_id, df):
    t = df[df["Tank_ID"] == tank_id]
    comp = len(t[t["Stage_Status"] == "Completed"])
    return round(comp / len(STAGES) * 100)

def status_pill(status):
    cls = {"Completed": "pill-completed", "In Progress": "pill-progress",
           "Hold": "pill-hold", "Not Started": "pill-notstart"}.get(status, "pill-notstart")
    return f'<span class="pill {cls}">{status}</span>'

def priority_tag(p):
    cls = {"High": "tag-high", "Medium": "tag-medium", "Low": "tag-low"}.get(p, "tag-low")
    return f'<span class="kanban-tag {cls}">{p}</span>'

def get_plotly_theme():
    return {
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": "#8899aa", "family": "Barlow"},
        "gridcolor": "rgba(30,144,255,0.1)",
    }

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:16px 0 8px;">
        <div style="font-family:'Rajdhani',sans-serif;font-size:1.4rem;font-weight:700;color:#e8edf5;letter-spacing:2px;">⚙️ BHAGWATI</div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:#00d4ff;letter-spacing:2px;margin-top:2px;">INDUSTRIES PVT. LTD.</div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:#8899aa;margin-top:4px;">TRANSFORMER FABRICATION</div>
    </div>
    <hr style="border-color:rgba(30,144,255,0.2);margin:8px 0 16px;">
    """, unsafe_allow_html=True)

    nav = st.radio("Navigation", [
        "📊 Dashboard Overview",
        "🏭 Kanban Board",
        "📋 Detailed Tracking",
        "⚠️ Delay Analysis",
        "👤 Responsibility View",
        "📦 Order Management",
        "✏️ Update Stage Status"
    ], label_visibility="collapsed")

    st.markdown("<hr style='border-color:rgba(30,144,255,0.2);'>", unsafe_allow_html=True)

    # Quick filters
    st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.7rem;color:#00d4ff;letter-spacing:1px;margin-bottom:8px;">QUICK FILTERS</div>', unsafe_allow_html=True)
    filter_priority = st.multiselect("Priority", PRIORITY_OPTIONS, default=PRIORITY_OPTIONS, label_visibility="collapsed")
    filter_order = st.multiselect("Order", orders_df["Order_ID"].tolist(), default=orders_df["Order_ID"].tolist(), label_visibility="collapsed")

    st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.65rem;color:#8899aa;margin-top:8px;">Filtering by Priority & Order</div>', unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(30,144,255,0.2);'>", unsafe_allow_html=True)
    today_str = datetime.today().strftime("%d %b %Y  |  %H:%M")
    st.markdown(f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.65rem;color:#8899aa;text-align:center;">{today_str}</div>', unsafe_allow_html=True)

# Apply filters
filtered_tracking = tracking_df[
    (tracking_df["Priority"].isin(filter_priority)) &
    (tracking_df["Order_ID"].isin(filter_order))
]
filtered_orders = orders_df[orders_df["Order_ID"].isin(filter_order)]

# ─────────────────────────────────────────────
# COMPUTED METRICS
# ─────────────────────────────────────────────
all_tanks     = tracking_df["Tank_ID"].unique()
tank_ids_filt = filtered_tracking["Tank_ID"].unique()

completed_tanks   = []
delayed_tanks     = []
critical_hold     = []
in_progress_tanks = []

for tid in tank_ids_filt:
    t = filtered_tracking[filtered_tracking["Tank_ID"] == tid]
    comp = len(t[t["Stage_Status"] == "Completed"])
    if comp == len(STAGES):
        completed_tanks.append(tid)
    ip = t[t["Stage_Status"].isin(["In Progress", "Hold"])]
    if not ip.empty:
        in_progress_tanks.append(tid)
    delayed = t[t["Delay_Days"] > 0]
    if not delayed.empty:
        delayed_tanks.append(tid)
    crit = t[(t["Is_Critical"]) & (t["Stage_Status"].isin(["In Progress", "Hold"]))]
    if not crit.empty:
        critical_hold.append(tid)

total_tanks_count     = len(tank_ids_filt)
completed_count       = len(completed_tanks)
delayed_count         = len(set(delayed_tanks))
critical_count        = len(set(critical_hold))
in_progress_count     = len(set(in_progress_tanks)) - completed_count

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="dashboard-header">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;">
        <div>
            <h1>⚙️ Production Tracking System</h1>
            <p>BHAGWATI INDUSTRIES PVT. LTD. · TRANSFORMER TANK FABRICATION · VADODARA, GUJARAT</p>
            <span class="header-badge">LIVE DASHBOARD</span>
        </div>
        <div style="text-align:right;">
            <div style="font-family:'Share Tech Mono',monospace;font-size:0.75rem;color:#00d4ff;">{total_tanks_count} TANKS TRACKED</div>
            <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:#8899aa;margin-top:4px;">{len(filtered_orders)} ACTIVE ORDERS</div>
            <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:#8899aa;">UPDATED: {datetime.today().strftime('%d %b %Y')}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ── PAGE: DASHBOARD OVERVIEW ──────────────────
# ─────────────────────────────────────────────
if nav == "📊 Dashboard Overview":

    # KPI row
    c1, c2, c3, c4, c5 = st.columns(5)
    cards = [
        (c1, "blue",   "🏗️", str(total_tanks_count),  "TOTAL TANKS"),
        (c2, "yellow", "⚙️", str(in_progress_count),  "IN PRODUCTION"),
        (c3, "green",  "✅", str(completed_count),     "DISPATCHED"),
        (c4, "red",    "🚨", str(delayed_count),       "DELAYED"),
        (c5, "orange", "⚡", str(critical_count),      "CRITICAL STAGE"),
    ]
    for col, color, icon, val, label in cards:
        with col:
            st.markdown(f"""
            <div class="metric-card {color}">
                <div class="metric-icon">{icon}</div>
                <div class="metric-value">{val}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")

    # ── Row 2: Stage distribution + Priority pie ──
    col_a, col_b = st.columns([3, 2])

    with col_a:
        st.markdown('<div class="section-header">📊 Stage Distribution</div>', unsafe_allow_html=True)
        stage_counts = (
            filtered_tracking[filtered_tracking["Stage_Status"] == "In Progress"]
            .groupby("Stage_Name").size().reset_index(name="Count")
        )
        stage_counts["Stage_No"] = stage_counts["Stage_Name"].map(
            {s: i+1 for i, s in enumerate(STAGES)}
        )
        stage_counts = stage_counts.sort_values("Stage_No")
        colors = ["#ff6b35" if s in CRITICAL_STAGES else "#1e90ff" for s in stage_counts["Stage_Name"]]

        fig = go.Figure(go.Bar(
            x=stage_counts["Stage_Name"],
            y=stage_counts["Count"],
            marker_color=colors,
            text=stage_counts["Count"],
            textposition="outside",
            textfont_color="#e8edf5"
        ))
        th = get_plotly_theme()
        fig.update_layout(
            plot_bgcolor=th["plot_bgcolor"], paper_bgcolor=th["paper_bgcolor"],
            font=th["font"], margin=dict(l=0, r=0, t=10, b=120),
            height=280, showlegend=False,
            xaxis=dict(tickangle=-40, gridcolor=th["gridcolor"], tickfont_size=10),
            yaxis=dict(gridcolor=th["gridcolor"]),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-header">🎯 By Priority</div>', unsafe_allow_html=True)
        pri_counts = (
            filtered_tracking.drop_duplicates("Tank_ID")
            .groupby("Priority").size().reset_index(name="Count")
        )
        fig2 = go.Figure(go.Pie(
            labels=pri_counts["Priority"],
            values=pri_counts["Count"],
            hole=0.55,
            marker_colors=["#ff1744", "#ffd600", "#00e676"],
            textfont_color="#e8edf5",
            textfont_size=12,
        ))
        fig2.update_layout(
            plot_bgcolor=th["plot_bgcolor"], paper_bgcolor=th["paper_bgcolor"],
            font=th["font"], margin=dict(l=0, r=0, t=10, b=0),
            height=280, showlegend=True,
            legend=dict(font_color="#8899aa", bgcolor="rgba(0,0,0,0)")
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Row 3: Tank progress table + Dispatch alert ──
    col_c, col_d = st.columns([3, 2])

    with col_c:
        st.markdown('<div class="section-header">🔄 Tank Progress Overview</div>', unsafe_allow_html=True)
        rows_html = ""
        for tid in tank_ids_filt:
            t = filtered_tracking[filtered_tracking["Tank_ID"] == tid]
            if t.empty:
                continue
            stage_name, stage_no = get_tank_current_stage(tid, filtered_tracking)
            pct = get_tank_progress_pct(tid, filtered_tracking)
            order_id = t.iloc[0]["Order_ID"]
            priority = t.iloc[0]["Priority"]
            delay = t["Delay_Days"].max()
            delay_str = f'<span style="color:#ff1744;font-weight:600;">+{delay}d</span>' if delay > 0 else '<span style="color:#00e676;">On Time</span>'
            is_delayed = delay > 0
            row_class = "delayed-row" if is_delayed else ""
            color = "#ff1744" if delay > 0 else ("#00e676" if pct == 100 else "#1e90ff")
            rows_html += f"""
            <tr class="{row_class}">
                <td style="font-family:'Share Tech Mono',monospace;color:#00d4ff;">{tid}</td>
                <td style="color:#8899aa;">{order_id}</td>
                <td style="max-width:180px;font-size:0.78rem;">{stage_name}</td>
                <td>
                    <div style="display:flex;align-items:center;gap:8px;">
                        <div class="prog-bar-wrap" style="width:80px;">
                            <div class="prog-bar-fill" style="width:{pct}%;background:{color};"></div>
                        </div>
                        <span style="font-family:'Share Tech Mono',monospace;font-size:0.72rem;color:{color};">{pct}%</span>
                    </div>
                </td>
                <td>{priority_tag(priority)}</td>
                <td>{delay_str}</td>
            </tr>"""
        st.markdown(f"""
        <table class="styled-table">
            <thead><tr>
                <th>TANK ID</th><th>ORDER</th><th>CURRENT STAGE</th><th>PROGRESS</th><th>PRIORITY</th><th>DELAY</th>
            </tr></thead>
            <tbody>{rows_html}</tbody>
        </table>""", unsafe_allow_html=True)

    with col_d:
        st.markdown('<div class="section-header">📅 Dispatch Alerts</div>', unsafe_allow_html=True)
        today = datetime.today().date()
        for _, row in filtered_orders.iterrows():
            dispatch = row["Committed_Dispatch"]
            days_left = (dispatch - today).days
            order_tanks = filtered_tracking[
                (filtered_tracking["Order_ID"] == row["Order_ID"]) &
                (filtered_tracking["Stage_Status"] != "Completed")
            ]["Tank_ID"].nunique()

            if days_left < 0:
                cls = "alert-red"
                icon = "🚨"
                msg = f"OVERDUE by {abs(days_left)} days"
            elif days_left <= 7:
                cls = "alert-yellow"
                icon = "⚠️"
                msg = f"{days_left} days remaining"
            else:
                cls = "alert-green"
                icon = "✅"
                msg = f"{days_left} days remaining"

            st.markdown(f"""
            <div class="alert-box {cls}">
                <span>{icon}</span>
                <div>
                    <div style="font-weight:600;font-size:0.82rem;">{row['Order_ID']} – {row['Client_Name']}</div>
                    <div style="font-size:0.72rem;opacity:0.8;">{msg} · {order_tanks} tanks pending · Dispatch: {dispatch.strftime('%d %b %Y')}</div>
                </div>
            </div>""", unsafe_allow_html=True)

        # Delay heatmap mini
        st.markdown('<div class="section-header" style="margin-top:20px;">🔥 Delay by Stage</div>', unsafe_allow_html=True)
        delay_by_stage = (
            filtered_tracking.groupby("Stage_Name")["Delay_Days"]
            .sum().reset_index()
        )
        delay_by_stage["Stage_No"] = delay_by_stage["Stage_Name"].map(
            {s: i+1 for i, s in enumerate(STAGES)}
        )
        delay_by_stage = delay_by_stage[delay_by_stage["Delay_Days"] > 0].sort_values("Stage_No")
        if not delay_by_stage.empty:
            fig3 = go.Figure(go.Bar(
                x=delay_by_stage["Delay_Days"],
                y=delay_by_stage["Stage_Name"],
                orientation="h",
                marker_color="#ff1744",
                text=delay_by_stage["Delay_Days"].apply(lambda x: f"+{x}d"),
                textposition="outside",
                textfont_color="#ff1744"
            ))
            fig3.update_layout(
                plot_bgcolor=th["plot_bgcolor"], paper_bgcolor=th["paper_bgcolor"],
                font=dict(color="#8899aa", family="Barlow", size=10),
                margin=dict(l=0, r=40, t=0, b=0), height=200, showlegend=False,
                xaxis=dict(gridcolor=th["gridcolor"]),
                yaxis=dict(gridcolor="rgba(0,0,0,0)"),
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.markdown('<div class="alert-box alert-green">✅ No delays detected in current selection</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ── PAGE: KANBAN BOARD ────────────────────────
# ─────────────────────────────────────────────
elif nav == "🏭 Kanban Board":
    st.markdown('<div class="section-header">🏭 Kanban Board – Stage-wise Tank View</div>', unsafe_allow_html=True)

    # Group stages into clusters for display
    stage_groups = [
        ("Planning",    STAGES[0:3]),
        ("Fabrication", STAGES[3:7]),
        ("Port Fit-up", STAGES[7:11]),
        ("Finishing",   STAGES[11:14]),
        ("Final",       STAGES[14:17]),
    ]

    for group_name, group_stages in stage_groups:
        st.markdown(f'<div style="font-family:\'Rajdhani\',sans-serif;font-size:1rem;font-weight:700;color:#00d4ff;text-transform:uppercase;letter-spacing:2px;margin:16px 0 8px;border-left:3px solid #00d4ff;padding-left:10px;">{group_name}</div>', unsafe_allow_html=True)
        cols = st.columns(len(group_stages))

        for col, stage in zip(cols, group_stages):
            is_critical = stage in CRITICAL_STAGES
            bg_color = "rgba(255,107,53,0.1)" if is_critical else "rgba(19,28,46,1)"
            border_color = "#ff6b35" if is_critical else "rgba(30,144,255,0.2)"
            header_color = "#ff6b35" if is_critical else "#1e90ff"

            tanks_at_stage = filtered_tracking[
                (filtered_tracking["Stage_Name"] == stage) &
                (filtered_tracking["Stage_Status"].isin(["In Progress", "Hold", "Completed"]))
            ]

            with col:
                crit_badge = ' ⚡' if is_critical else ''
                count = len(tanks_at_stage)
                cards_html = ""
                for _, row in tanks_at_stage.iterrows():
                    status = row["Stage_Status"]
                    css_class = {
                        "Completed": "completed",
                        "In Progress": "in-progress",
                        "Hold": "hold",
                        "Not Started": "not-started"
                    }.get(status, "not-started")
                    delay_str = f'<span style="color:#ff1744;font-size:0.68rem;">⏱ +{row["Delay_Days"]}d delay</span>' if row["Delay_Days"] > 0 else ""
                    hold_str  = f'<span style="color:#ff1744;font-size:0.68rem;">🔒 HOLD</span>' if status == "Hold" else ""
                    cards_html += f"""
                    <div class="kanban-card {css_class}">
                        <div style="font-family:'Share Tech Mono',monospace;font-size:0.8rem;color:#00d4ff;">{row['Tank_ID']}</div>
                        <div style="font-size:0.72rem;color:#8899aa;">{row['Order_ID']}</div>
                        <div style="font-size:0.72rem;color:#e8edf5;margin-top:2px;">👤 {row['Assigned_Person'].split()[0]}</div>
                        {priority_tag(row['Priority'])}{delay_str}{hold_str}
                    </div>"""

                st.markdown(f"""
                <div class="kanban-col" style="background:{bg_color};border-color:{border_color};">
                    <div class="kanban-col-header" style="background:rgba(30,144,255,0.08);color:{header_color};border:1px solid {border_color};">
                        {stage.replace(' Complete', '')[:22]}{crit_badge}
                        <span style="float:right;background:rgba(0,0,0,0.3);border-radius:10px;padding:0 6px;font-size:0.7rem;">{count}</span>
                    </div>
                    {cards_html if cards_html else '<div style="color:#8899aa;font-size:0.75rem;text-align:center;padding:20px 0;font-family:Share Tech Mono,monospace;">— empty —</div>'}
                </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ── PAGE: DETAILED TRACKING ───────────────────
# ─────────────────────────────────────────────
elif nav == "📋 Detailed Tracking":
    st.markdown('<div class="section-header">📋 Detailed Stage Tracking</div>', unsafe_allow_html=True)

    tank_options = filtered_tracking["Tank_ID"].unique().tolist()
    sel_tank = st.selectbox("Select Tank", tank_options)

    if sel_tank:
        t_data = filtered_tracking[filtered_tracking["Tank_ID"] == sel_tank].copy()
        order_id = t_data.iloc[0]["Order_ID"]
        order_info = orders_df[orders_df["Order_ID"] == order_id].iloc[0]
        pct = get_tank_progress_pct(sel_tank, filtered_tracking)

        # Tank info bar
        days_left = (order_info["Committed_Dispatch"] - datetime.today().date()).days
        dispatch_color = "#ff1744" if days_left < 0 else ("#ffd600" if days_left <= 7 else "#00e676")
        st.markdown(f"""
        <div style="background:var(--bg-card);border:1px solid rgba(30,144,255,0.3);border-radius:8px;padding:14px 20px;margin-bottom:16px;display:flex;gap:30px;flex-wrap:wrap;">
            <div><div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:#8899aa;">TANK ID</div><div style="font-family:'Rajdhani',sans-serif;font-size:1.2rem;font-weight:700;color:#00d4ff;">{sel_tank}</div></div>
            <div><div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:#8899aa;">ORDER</div><div style="font-family:'Rajdhani',sans-serif;font-size:1.2rem;font-weight:700;color:#e8edf5;">{order_id}</div></div>
            <div><div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:#8899aa;">CLIENT</div><div style="font-size:0.9rem;color:#e8edf5;">{order_info['Client_Name']}</div></div>
            <div><div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:#8899aa;">TYPE</div><div style="font-size:0.9rem;color:#e8edf5;">{order_info['Tank_Type']}</div></div>
            <div><div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:#8899aa;">DISPATCH DATE</div><div style="font-size:0.9rem;color:{dispatch_color};">{order_info['Committed_Dispatch'].strftime('%d %b %Y')} ({days_left}d)</div></div>
            <div><div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:#8899aa;">OVERALL PROGRESS</div>
                <div style="display:flex;align-items:center;gap:8px;margin-top:4px;">
                    <div class="prog-bar-wrap" style="width:120px;height:8px;"><div class="prog-bar-fill" style="width:{pct}%;background:#1e90ff;"></div></div>
                    <span style="font-family:'Share Tech Mono',monospace;color:#1e90ff;">{pct}%</span>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        # Stage rows
        rows_html = ""
        for _, row in t_data.sort_values("Stage_No").iterrows():
            status = row["Stage_Status"]
            is_crit = row["Is_Critical"]
            bg = "rgba(255,107,53,0.05)" if is_crit else ""
            delay_str = f'<span style="color:#ff1744;font-weight:600;">+{row["Delay_Days"]}d</span>' if row["Delay_Days"] > 0 else '<span style="color:#8899aa;">—</span>'
            crit_mark = ' <span style="color:#ff6b35;font-size:0.7rem;">⚡CRITICAL</span>' if is_crit else ""
            start = row["Start_Date"].strftime("%d %b") if row["Start_Date"] else "—"
            end   = row["End_Date"].strftime("%d %b") if row["End_Date"] else "—"
            rows_html += f"""
            <tr style="background:{bg};">
                <td style="font-family:'Share Tech Mono',monospace;color:#8899aa;font-size:0.72rem;">{row['Stage_No']:02d}</td>
                <td>{row['Stage_Name']}{crit_mark}</td>
                <td>{status_pill(status)}</td>
                <td style="font-size:0.8rem;">{row['Assigned_Person']}</td>
                <td style="font-family:'Share Tech Mono',monospace;font-size:0.75rem;color:#8899aa;">{start}</td>
                <td style="font-family:'Share Tech Mono',monospace;font-size:0.75rem;color:#8899aa;">{end}</td>
                <td>{delay_str}</td>
                <td style="font-size:0.78rem;color:#8899aa;">{row['Remarks'] or '—'}</td>
            </tr>"""

        st.markdown(f"""
        <table class="styled-table">
            <thead><tr>
                <th>#</th><th>STAGE</th><th>STATUS</th><th>ASSIGNED TO</th><th>START</th><th>END</th><th>DELAY</th><th>REMARKS</th>
            </tr></thead>
            <tbody>{rows_html}</tbody>
        </table>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ── PAGE: DELAY ANALYSIS ──────────────────────
# ─────────────────────────────────────────────
elif nav == "⚠️ Delay Analysis":
    st.markdown('<div class="section-header">⚠️ Delay Analysis & Bottleneck Identification</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    th = get_plotly_theme()

    with col1:
        # Total delay by stage
        delay_stage = (
            filtered_tracking.groupby("Stage_Name")["Delay_Days"].sum().reset_index()
        )
        delay_stage["Stage_No"] = delay_stage["Stage_Name"].map({s: i+1 for i, s in enumerate(STAGES)})
        delay_stage = delay_stage.sort_values("Stage_No")
        colors_ds = ["#ff6b35" if s in CRITICAL_STAGES else "#ff1744" if d > 5 else "#ffd600" if d > 0 else "#1e90ff"
                     for s, d in zip(delay_stage["Stage_Name"], delay_stage["Delay_Days"])]
        fig = go.Figure(go.Bar(
            x=delay_stage["Stage_Name"], y=delay_stage["Delay_Days"],
            marker_color=colors_ds, text=delay_stage["Delay_Days"],
            textposition="outside", textfont_color="#e8edf5"
        ))
        fig.update_layout(plot_bgcolor=th["plot_bgcolor"], paper_bgcolor=th["paper_bgcolor"],
                          font=th["font"], margin=dict(l=0,r=0,t=20,b=120), height=320,
                          title=dict(text="Total Delay Days by Stage", font_color="#e8edf5", font_size=13),
                          xaxis=dict(tickangle=-40, tickfont_size=9, gridcolor=th["gridcolor"]),
                          yaxis=dict(gridcolor=th["gridcolor"]))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Delay per tank
        tank_delay = (
            filtered_tracking.groupby("Tank_ID")["Delay_Days"].sum().reset_index()
            .sort_values("Delay_Days", ascending=False)
        )
        c = ["#ff1744" if d > 10 else "#ffd600" if d > 5 else "#00e676" for d in tank_delay["Delay_Days"]]
        fig2 = go.Figure(go.Bar(
            x=tank_delay["Tank_ID"], y=tank_delay["Delay_Days"],
            marker_color=c, text=tank_delay["Delay_Days"],
            textposition="outside", textfont_color="#e8edf5"
        ))
        fig2.update_layout(plot_bgcolor=th["plot_bgcolor"], paper_bgcolor=th["paper_bgcolor"],
                           font=th["font"], margin=dict(l=0,r=0,t=20,b=60), height=320,
                           title=dict(text="Total Delay Days per Tank", font_color="#e8edf5", font_size=13),
                           xaxis=dict(gridcolor=th["gridcolor"]), yaxis=dict(gridcolor=th["gridcolor"]))
        st.plotly_chart(fig2, use_container_width=True)

    # Worst bottlenecks
    st.markdown('<div class="section-header">🚧 Top Bottleneck Stages</div>', unsafe_allow_html=True)
    top_delays = delay_stage.sort_values("Delay_Days", ascending=False).head(5)
    cols = st.columns(len(top_delays))
    for col, (_, row) in zip(cols, top_delays.iterrows()):
        d = int(row["Delay_Days"])
        color = "#ff1744" if d > 8 else "#ffd600" if d > 3 else "#00e676"
        is_c = row["Stage_Name"] in CRITICAL_STAGES
        with col:
            st.markdown(f"""
            <div class="metric-card {'orange' if is_c else 'red'}" style="text-align:center;">
                <div class="metric-icon">{"⚡" if is_c else "⏱"}</div>
                <div class="metric-value" style="font-size:1.8rem;color:{color};">{d}d</div>
                <div class="metric-label" style="font-size:0.65rem;">{row['Stage_Name'][:25]}</div>
                {"<div style='font-size:0.65rem;color:#ff6b35;margin-top:4px;'>CRITICAL STAGE</div>" if is_c else ""}
            </div>""", unsafe_allow_html=True)

    # Delayed tanks details
    st.markdown('<div class="section-header">🔴 Delayed Tanks Detail</div>', unsafe_allow_html=True)
    delayed_detail = filtered_tracking[filtered_tracking["Delay_Days"] > 0].sort_values("Delay_Days", ascending=False)
    if not delayed_detail.empty:
        rows_html = ""
        for _, row in delayed_detail.iterrows():
            rows_html += f"""
            <tr>
                <td style="font-family:'Share Tech Mono',monospace;color:#ff6b6b;">{row['Tank_ID']}</td>
                <td>{row['Order_ID']}</td>
                <td>{row['Stage_Name']}{"<span style='color:#ff6b35;'> ⚡</span>" if row['Is_Critical'] else ""}</td>
                <td>{status_pill(row['Stage_Status'])}</td>
                <td style="color:#ff1744;font-weight:600;">+{row['Delay_Days']} days</td>
                <td>{row['Assigned_Person']}</td>
                <td style="font-size:0.78rem;color:#8899aa;">{row['Remarks'] or '—'}</td>
            </tr>"""
        st.markdown(f"""<table class="styled-table">
            <thead><tr><th>TANK</th><th>ORDER</th><th>STAGE</th><th>STATUS</th><th>DELAY</th><th>RESPONSIBLE</th><th>REMARKS</th></tr></thead>
            <tbody>{rows_html}</tbody></table>""", unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-box alert-green">✅ No delays in current selection!</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ── PAGE: RESPONSIBILITY VIEW ─────────────────
# ─────────────────────────────────────────────
elif nav == "👤 Responsibility View":
    st.markdown('<div class="section-header">👤 Workload & Responsibility Tracking</div>', unsafe_allow_html=True)

    emp_stats = (
        filtered_tracking.groupby("Assigned_Person").agg(
            Total_Tasks=("Tank_ID", "count"),
            Completed=("Stage_Status", lambda x: (x == "Completed").sum()),
            In_Progress=("Stage_Status", lambda x: (x == "In Progress").sum()),
            On_Hold=("Stage_Status", lambda x: (x == "Hold").sum()),
            Total_Delay=("Delay_Days", "sum"),
        ).reset_index()
    )
    emp_stats["Pending"] = emp_stats["Total_Tasks"] - emp_stats["Completed"]
    emp_stats["Efficiency"] = (emp_stats["Completed"] / emp_stats["Total_Tasks"] * 100).round(0).astype(int)

    th = get_plotly_theme()
    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Completed", x=emp_stats["Assigned_Person"], y=emp_stats["Completed"],
                             marker_color="#00e676", text=emp_stats["Completed"], textposition="inside"))
        fig.add_trace(go.Bar(name="In Progress", x=emp_stats["Assigned_Person"], y=emp_stats["In_Progress"],
                             marker_color="#ffd600", text=emp_stats["In_Progress"], textposition="inside"))
        fig.add_trace(go.Bar(name="Pending", x=emp_stats["Assigned_Person"], y=emp_stats["Pending"],
                             marker_color="#1e90ff", text=emp_stats["Pending"], textposition="inside"))
        fig.update_layout(barmode="stack", plot_bgcolor=th["plot_bgcolor"], paper_bgcolor=th["paper_bgcolor"],
                          font=th["font"], margin=dict(l=0,r=0,t=20,b=80), height=320,
                          title=dict(text="Tasks per Employee", font_color="#e8edf5", font_size=13),
                          xaxis=dict(tickangle=-30, tickfont_size=9, gridcolor=th["gridcolor"]),
                          yaxis=dict(gridcolor=th["gridcolor"]),
                          legend=dict(font_color="#8899aa", bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = go.Figure(go.Bar(
            x=emp_stats["Assigned_Person"], y=emp_stats["Efficiency"],
            marker_color=["#00e676" if e >= 70 else "#ffd600" if e >= 40 else "#ff1744" for e in emp_stats["Efficiency"]],
            text=[f"{e}%" for e in emp_stats["Efficiency"]], textposition="outside", textfont_color="#e8edf5"
        ))
        fig2.update_layout(plot_bgcolor=th["plot_bgcolor"], paper_bgcolor=th["paper_bgcolor"],
                           font=th["font"], margin=dict(l=0,r=0,t=20,b=80), height=320,
                           title=dict(text="Completion Efficiency (%)", font_color="#e8edf5", font_size=13),
                           xaxis=dict(tickangle=-30, tickfont_size=9, gridcolor=th["gridcolor"]),
                           yaxis=dict(gridcolor=th["gridcolor"], range=[0, 115]))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-header">📊 Employee Summary Table</div>', unsafe_allow_html=True)
    rows_html = ""
    for _, row in emp_stats.sort_values("Pending", ascending=False).iterrows():
        eff = row["Efficiency"]
        eff_color = "#00e676" if eff >= 70 else "#ffd600" if eff >= 40 else "#ff1744"
        delay_str = f'<span style="color:#ff1744;">+{int(row["Total_Delay"])}d</span>' if row["Total_Delay"] > 0 else '<span style="color:#00e676;">0d</span>'
        rows_html += f"""
        <tr>
            <td style="font-weight:600;">{row['Assigned_Person']}</td>
            <td style="font-family:'Share Tech Mono',monospace;">{row['Total_Tasks']}</td>
            <td style="color:#00e676;">{row['Completed']}</td>
            <td style="color:#ffd600;">{row['In_Progress']}</td>
            <td style="color:#ff1744;">{row['On_Hold']}</td>
            <td style="color:#1e90ff;">{row['Pending']}</td>
            <td>{delay_str}</td>
            <td>
                <div style="display:flex;align-items:center;gap:8px;">
                    <div class="prog-bar-wrap" style="width:80px;">
                        <div class="prog-bar-fill" style="width:{eff}%;background:{eff_color};"></div>
                    </div>
                    <span style="font-family:'Share Tech Mono',monospace;font-size:0.72rem;color:{eff_color};">{eff}%</span>
                </div>
            </td>
        </tr>"""
    st.markdown(f"""<table class="styled-table">
        <thead><tr><th>EMPLOYEE</th><th>TOTAL</th><th>DONE</th><th>IN PROG</th><th>HOLD</th><th>PENDING</th><th>DELAY</th><th>EFFICIENCY</th></tr></thead>
        <tbody>{rows_html}</tbody></table>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ── PAGE: ORDER MANAGEMENT ────────────────────
# ─────────────────────────────────────────────
elif nav == "📦 Order Management":
    st.markdown('<div class="section-header">📦 Order Master</div>', unsafe_allow_html=True)

    # Display current orders
    rows_html = ""
    today = datetime.today().date()
    for _, row in orders_df.iterrows():
        days_left = (row["Committed_Dispatch"] - today).days
        dc = "#ff1744" if days_left < 0 else "#ffd600" if days_left <= 7 else "#00e676"
        rows_html += f"""<tr>
            <td style="font-family:'Share Tech Mono',monospace;color:#00d4ff;">{row['Order_ID']}</td>
            <td>{row['Client_Name']}</td>
            <td style="font-size:0.8rem;">{row['Tank_Type']}</td>
            <td style="text-align:center;">{row['Quantity']}</td>
            <td style="font-family:'Share Tech Mono',monospace;font-size:0.75rem;">{row['Drawing_Receipt_Date'].strftime('%d %b %Y')}</td>
            <td style="color:{dc};font-family:'Share Tech Mono',monospace;font-size:0.75rem;">{row['Committed_Dispatch'].strftime('%d %b %Y')} ({days_left}d)</td>
            <td>{priority_tag(row['Priority'])}</td>
        </tr>"""
    st.markdown(f"""<table class="styled-table">
        <thead><tr><th>ORDER ID</th><th>CLIENT</th><th>TANK TYPE</th><th>QTY</th><th>DRAWING DATE</th><th>DISPATCH DATE</th><th>PRIORITY</th></tr></thead>
        <tbody>{rows_html}</tbody></table>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header" style="margin-top:24px;">➕ Add New Order</div>', unsafe_allow_html=True)
    with st.expander("Expand to add a new order"):
        c1, c2, c3 = st.columns(3)
        with c1:
            new_client   = st.selectbox("Client Name", CLIENTS)
            new_type     = st.selectbox("Tank Type", TANK_TYPES)
        with c2:
            new_qty      = st.number_input("Quantity", min_value=1, max_value=20, value=1)
            new_priority = st.selectbox("Priority", PRIORITY_OPTIONS)
        with c3:
            new_draw_dt  = st.date_input("Drawing Receipt Date", value=datetime.today().date())
            new_disp_dt  = st.date_input("Committed Dispatch Date", value=datetime.today().date() + timedelta(days=45))

        if st.button("➕ Add Order"):
            existing_ids = orders_df["Order_ID"].tolist()
            last_num = max([int(oid.split("-")[1]) for oid in existing_ids]) if existing_ids else 0
            new_id = f"ORD-{str(last_num + 1).zfill(3)}"

            new_order = pd.DataFrame([{
                "Order_ID": new_id,
                "Client_Name": new_client,
                "Tank_Type": new_type,
                "Quantity": new_qty,
                "Drawing_Receipt_Date": new_draw_dt,
                "Committed_Dispatch": new_disp_dt,
                "Priority": new_priority,
            }])
            st.session_state.orders = pd.concat([st.session_state.orders, new_order], ignore_index=True)

            # Create tank records
            new_tracks = []
            for i in range(new_qty):
                tank_id = f"{new_id}-{'ABCDEFGHIJKLMNOPQRST'[i]}"
                for j, stage in enumerate(STAGES):
                    new_tracks.append({
                        "Order_ID": new_id, "Tank_ID": tank_id, "Stage_Name": stage,
                        "Stage_No": j + 1, "Stage_Status": "Not Started" if j > 0 else "In Progress",
                        "Assigned_Person": EMPLOYEES[0], "Start_Date": new_draw_dt if j == 0 else None,
                        "End_Date": None, "Remarks": "", "Delay_Days": 0,
                        "Is_Critical": stage in CRITICAL_STAGES, "Priority": new_priority,
                    })
            st.session_state.tracking = pd.concat(
                [st.session_state.tracking, pd.DataFrame(new_tracks)], ignore_index=True
            )
            st.success(f"✅ Order {new_id} added with {new_qty} tank(s)!")
            st.rerun()

# ─────────────────────────────────────────────
# ── PAGE: UPDATE STAGE STATUS ─────────────────
# ─────────────────────────────────────────────
elif nav == "✏️ Update Stage Status":
    st.markdown('<div class="section-header">✏️ Update Stage Status</div>', unsafe_allow_html=True)
    st.markdown('<div class="alert-box alert-yellow">⚠️ A stage can only be marked In Progress if the previous stage is Completed. Rule is enforced automatically.</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        sel_order_u = st.selectbox("Select Order", orders_df["Order_ID"].tolist())
    with c2:
        tanks_in_order = tracking_df[tracking_df["Order_ID"] == sel_order_u]["Tank_ID"].unique().tolist()
        sel_tank_u = st.selectbox("Select Tank", tanks_in_order)

    if sel_tank_u:
        t_data = tracking_df[tracking_df["Tank_ID"] == sel_tank_u].sort_values("Stage_No").copy()
        st.markdown(f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.75rem;color:#00d4ff;margin:12px 0 8px;">STAGES FOR {sel_tank_u}</div>', unsafe_allow_html=True)

        for idx, row in t_data.iterrows():
            prev_completed = True
            if row["Stage_No"] > 1:
                prev = t_data[t_data["Stage_No"] == row["Stage_No"] - 1].iloc[0]
                prev_completed = prev["Stage_Status"] == "Completed"

            is_crit = row["Is_Critical"]
            crit_label = " ⚡" if is_crit else ""
            bg = "rgba(255,107,53,0.05)" if is_crit else "rgba(19,28,46,0.5)"
            border = "rgba(255,107,53,0.3)" if is_crit else "rgba(30,144,255,0.15)"

            with st.container():
                st.markdown(f"""
                <div style="background:{bg};border:1px solid {border};border-radius:6px;padding:10px 14px;margin-bottom:8px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
                        <div>
                            <span style="font-family:'Share Tech Mono',monospace;font-size:0.7rem;color:#8899aa;">STAGE {row['Stage_No']:02d}</span>
                            <span style="font-family:'Rajdhani',sans-serif;font-weight:600;margin-left:8px;color:{'#ff6b35' if is_crit else '#e8edf5'};">{row['Stage_Name']}{crit_label}</span>
                        </div>
                        <div>{status_pill(row['Stage_Status'])}</div>
                    </div>
                </div>""", unsafe_allow_html=True)

                with st.expander(f"Edit Stage {row['Stage_No']:02d}: {row['Stage_Name']}", expanded=False):
                    ec1, ec2, ec3 = st.columns(3)
                    with ec1:
                        allowed_statuses = STATUS_OPTIONS.copy()
                        if not prev_completed and row["Stage_No"] > 1:
                            allowed_statuses = ["Not Started"]
                            st.warning("Previous stage not completed.")
                        new_status = st.selectbox(
                            "Status",
                            allowed_statuses,
                            index=allowed_statuses.index(row["Stage_Status"]) if row["Stage_Status"] in allowed_statuses else 0,
                            key=f"status_{idx}"
                        )
                    with ec2:
                        new_person = st.selectbox(
                            "Assigned Person", EMPLOYEES,
                            index=EMPLOYEES.index(row["Assigned_Person"]) if row["Assigned_Person"] in EMPLOYEES else 0,
                            key=f"person_{idx}"
                        )
                    with ec3:
                        new_remarks = st.text_input("Remarks", value=row["Remarks"] or "", key=f"rem_{idx}")

                    if st.button(f"💾 Save Stage {row['Stage_No']}", key=f"save_{idx}"):
                        today = datetime.today().date()
                        mask = (
                            (st.session_state.tracking["Tank_ID"] == sel_tank_u) &
                            (st.session_state.tracking["Stage_No"] == row["Stage_No"])
                        )
                        if new_status == "In Progress" and row["Stage_Status"] != "In Progress":
                            st.session_state.tracking.loc[mask, "Start_Date"] = today
                            st.session_state.tracking.loc[mask, "End_Date"] = None
                        elif new_status == "Completed":
                            st.session_state.tracking.loc[mask, "End_Date"] = today
                            # Auto-start next stage
                            next_mask = (
                                (st.session_state.tracking["Tank_ID"] == sel_tank_u) &
                                (st.session_state.tracking["Stage_No"] == row["Stage_No"] + 1)
                            )
                            if next_mask.any():
                                st.session_state.tracking.loc[next_mask, "Stage_Status"] = "In Progress"
                                st.session_state.tracking.loc[next_mask, "Start_Date"] = today

                        st.session_state.tracking.loc[mask, "Stage_Status"]   = new_status
                        st.session_state.tracking.loc[mask, "Assigned_Person"]= new_person
                        st.session_state.tracking.loc[mask, "Remarks"]        = new_remarks
                        st.success(f"✅ Stage {row['Stage_No']} updated to '{new_status}'")
                        st.rerun()
