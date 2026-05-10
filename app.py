import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta, date
import calendar
import os
from color_theme import PALETTE, CHART_SEQUENCE, HEATMAP_SCALE, PLOTLY_LAYOUT_DEFAULTS

st.set_page_config(page_title="Life OS", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

# Legacy color definitions - replace with PALETTE usage
# P = "#002664"  -> PALETTE["primary"]
# R = "#C00000"  -> PALETTE["alert"]
# G = "#00843D"  -> Use PALETTE["teal"] for green charts
# A = "#F7931E"  -> PALETTE["soft_pink"] for warnings
# PU = "#6B21A8" -> PALETTE["secondary"]
# TEAL = "#0891B2" -> PALETTE["teal"]

MOOD_C = {"Great": PALETTE["teal"], "Good": PALETTE["secondary"], "Okay": PALETTE["soft_pink"], "Low": PALETTE["alert"], "Bad": PALETTE["alert"]}
MOOD_V = {"Great": 5, "Good": 4, "Okay": 3, "Low": 2, "Bad": 1}
STATUS_C = {"Done": PALETTE["teal"], "InProgress": PALETTE["primary"], "ToDo": PALETTE["soft_pink"], "Backlog": PALETTE["neutral"], "OnHold": PALETTE["neutral"], "Cancelled": PALETTE["neutral"], "Active": PALETTE["secondary"]}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* {{ font-family: 'Inter', sans-serif; }}
.main-title {{ font-size: 1.8rem; font-weight: 800; color: {PALETTE["primary"]}; letter-spacing: -0.03em; margin: 0; }}
.main-sub {{ font-size: 0.85rem; color: {PALETTE["neutral"]}; margin-bottom: 1.5rem; font-weight: 400; }}
.kpi-row {{ display: flex; gap: 12px; margin-bottom: 1.5rem; }}
.kpi {{
    flex: 1; background: white; border-radius: 10px; padding: 16px 18px;
    border: 1px solid {PALETTE["neutral"]}; position: relative; overflow: hidden;
}}
.kpi::before {{ content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: {PALETTE["primary"]}; }}
.kpi.green::before {{ background: {PALETTE["teal"]}; }}
.kpi.red::before {{ background: {PALETTE["alert"]}; }}
.kpi.purple::before {{ background: {PALETTE["secondary"]}; }}
.kpi.amber::before {{ background: {PALETTE["soft_pink"]}; }}
.kpi-label {{ font-size: 0.7rem; color: {PALETTE["neutral"]}; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600; }}
.kpi-value {{ font-size: 1.6rem; font-weight: 800; color: {PALETTE["primary"]}; margin-top: 2px; }}
.kpi.green .kpi-value {{ color: {PALETTE["teal"]}; }}
.kpi.red .kpi-value {{ color: {PALETTE["alert"]}; }}
.kpi.purple .kpi-value {{ color: {PALETTE["secondary"]}; }}
.section-title {{ font-size: 0.75rem; color: {PALETTE["neutral"]}; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 700; margin: 1.5rem 0 0.5rem 0; }}
.score-gauge {{ text-align: center; padding: 20px; background: white; border-radius: 10px; border: 1px solid {PALETTE["neutral"]}; }}
.score-number {{ font-size: 2.5rem; font-weight: 800; }}
.score-label {{ font-size: 0.7rem; color: {PALETTE["neutral"]}; text-transform: uppercase; letter-spacing: 0.08em; }}
div[data-testid="stSidebar"] {{ background: linear-gradient(180deg, {PALETTE["primary"]} 0%, {PALETTE["primary"]} 100%); }}
div[data-testid="stSidebar"] .stMarkdown {{ color: rgba(255,255,255,0.9); }}
div[data-testid="stSidebar"] label {{ color: rgba(255,255,255,0.8) !important; font-size: 0.8rem; }}
div[data-testid="stSidebar"] .stRadio label {{ color: rgba(255,255,255,0.9) !important; }}
.divider {{ border: none; border-top: 1px solid {PALETTE["neutral"]}; margin: 1.5rem 0; }}
</style>
""", unsafe_allow_html=True)

def kpi_strip(items):
    html = '<div class="kpi-row">'
    for label, value, cls in items:
        html += f'<div class="kpi {cls}"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def gauge_score(value, label, max_val=100):
    color = PALETTE["teal"] if value >= 70 else PALETTE["soft_pink"] if value >= 50 else PALETTE["alert"]
    st.markdown(f'''
    <div class="score-gauge">
        <div class="score-number" style="color:{color}">{value:.0f}</div>
        <div class="score-label">{label}</div>
    </div>''', unsafe_allow_html=True)

def chart_cfg(fig, h=380, mt=40, mb=30, ml=None):
    margin = dict(t=mt, b=mb, l=ml if ml else 60, r=20)
    # Apply unified layout defaults first
    fig.update_layout(**PLOTLY_LAYOUT_DEFAULTS)
    # Then apply specific overrides
    fig.update_layout(template="plotly_white", height=h, margin=margin,
                      font=dict(family="Inter", size=11))
    return fig

def hex_to_rgba(hex_color, alpha=0.3):
    """Convert hex color to rgba with alpha"""
    if hex_color.startswith("#"):
        hex_color = hex_color[1:]
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

@st.cache_data
def load_data():
    base = os.path.dirname(__file__)
    dd = os.path.join(base, "data")
    if not os.path.exists(os.path.join(dd, "todos.csv")):
        dd = base
    todos = pd.read_csv(os.path.join(dd, "todos.csv"))
    todos["created_date"] = pd.to_datetime(todos["created_date"])
    todos["deadline"] = pd.to_datetime(todos["deadline"])
    todos["date_actioned"] = pd.to_datetime(todos["date_actioned"])
    events = pd.read_csv(os.path.join(dd, "events.csv"))
    events["event_date"] = pd.to_datetime(events["event_date"])
    routines = pd.read_csv(os.path.join(dd, "routines.csv"))
    rlog = pd.read_csv(os.path.join(dd, "routine_log.csv"))
    rlog["completion_date"] = pd.to_datetime(rlog["completion_date"])
    journal = pd.read_csv(os.path.join(dd, "journal.csv"))
    journal["date"] = pd.to_datetime(journal["date"])
    journal["mood_score"] = journal["mood"].map(MOOD_V)
    return todos, events, routines, rlog, journal

# ─── PAGE 1: COMMAND CENTRE ───

def page_command(todos, events, routines, rlog, journal):
    st.markdown('<div class="main-title">Command Centre</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-sub">Gmail → GAS → Notion → Claude pipeline — unified life analytics</div>', unsafe_allow_html=True)

    open_t = len(todos[todos["status"].isin(["ToDo", "InProgress", "Active"])])
    done_pct = len(todos[todos["status"] == "Done"]) / max(len(todos), 1)
    upcoming = len(events[events["status"] == "Upcoming"])
    avg_streak = routines["current_streak"].mean()
    avg_mood = journal.sort_values("date").tail(14)["mood_score"].mean()
    j_coverage = journal["date"].nunique() / max((journal["date"].max() - journal["date"].min()).days, 1)

    kpi_strip([
        ("Open Tasks", str(open_t), "red" if open_t > 50 else ""),
        ("Done Rate", f"{done_pct:.0%}", "green" if done_pct > 0.5 else "red"),
        ("Upcoming", str(upcoming), "purple"),
        ("Avg Streak", f"{avg_streak:.0f}d", "green" if avg_streak > 5 else "amber"),
        ("Mood (14d)", f"{avg_mood:.1f}/5", "green" if avg_mood >= 3.5 else "red"),
        ("Journal %", f"{j_coverage:.0%}", "green" if j_coverage > 0.7 else "amber"),
    ])

    st.markdown('<div class="section-title">Health Scores</div>', unsafe_allow_html=True)
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        prod_score = done_pct * 100
        gauge_score(prod_score, "Productivity")
    with sc2:
        habit_score = routines["last_90_days_rate"].mean() * 100
        gauge_score(habit_score, "Habit Consistency")
    with sc3:
        well_score = (avg_mood / 5) * 100
        gauge_score(well_score, "Wellbeing")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown('<div class="section-title">Cross-System Activity Timeline</div>', unsafe_allow_html=True)
        date_range = pd.date_range(todos["created_date"].min(), journal["date"].max(), freq="D")
        activity = pd.DataFrame({"date": date_range})
        t_daily = todos.groupby(todos["created_date"].dt.date)["todo_id"].count().reset_index()
        t_daily.columns = ["date", "tasks"]
        t_daily["date"] = pd.to_datetime(t_daily["date"])
        e_daily = events.groupby(events["event_date"].dt.date)["event_id"].count().reset_index()
        e_daily.columns = ["date", "events"]
        e_daily["date"] = pd.to_datetime(e_daily["date"])
        r_daily = rlog[rlog["completed"] == 1].groupby(rlog[rlog["completed"] == 1]["completion_date"].dt.date)["log_id"].count().reset_index()
        r_daily.columns = ["date", "routines"]
        r_daily["date"] = pd.to_datetime(r_daily["date"])
        j_daily = journal.groupby(journal["date"].dt.date)["journal_id"].count().reset_index()
        j_daily.columns = ["date", "journal"]
        j_daily["date"] = pd.to_datetime(j_daily["date"])

        activity = activity.merge(t_daily, on="date", how="left").merge(e_daily, on="date", how="left")
        activity = activity.merge(r_daily, on="date", how="left").merge(j_daily, on="date", how="left").fillna(0)

        fig = go.Figure()
        for col, name, color in [("routines", "Routines", PALETTE["teal"]), ("tasks", "Tasks", PALETTE["primary"]), ("events", "Events", PALETTE["secondary"]), ("journal", "Journal", PALETTE["soft_pink"])]:
            fig.add_trace(go.Scatter(
                x=activity["date"], y=activity[col].rolling(7).mean(),
                name=name, mode="lines", stackgroup="one",
                line=dict(width=0.5, color=color), fillcolor=hex_to_rgba(color, 0.3)
            ))
        fig = chart_cfg(fig, h=320)
        fig.update_layout(legend=dict(orientation="h", y=1.08, font=dict(size=10)), yaxis_title="7-Day Rolling Avg")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Monthly Comparison</div>', unsafe_allow_html=True)
        months = sorted(todos["created_date"].dt.strftime("%Y-%m").unique())[-6:]
        monthly_data = []
        for m in months:
            t_count = len(todos[todos["created_date"].dt.strftime("%Y-%m") == m])
            t_done = len(todos[(todos["date_actioned"].dt.strftime("%Y-%m") == m)])
            e_count = len(events[events["event_date"].dt.strftime("%Y-%m") == m])
            j_count = len(journal[journal["date"].dt.strftime("%Y-%m") == m])
            j_mood = journal[journal["date"].dt.strftime("%Y-%m") == m]["mood_score"].mean() if len(journal[journal["date"].dt.strftime("%Y-%m") == m]) > 0 else 0
            monthly_data.append({"month": m, "created": t_count, "completed": t_done, "events": e_count, "journals": j_count, "mood": round(j_mood, 1)})

        mdf = pd.DataFrame(monthly_data)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=mdf["month"], y=mdf["created"], name="Tasks Created", marker_color=PALETTE["primary"], opacity=0.7))
        fig.add_trace(go.Bar(x=mdf["month"], y=mdf["completed"], name="Completed", marker_color=PALETTE["teal"], opacity=0.7))
        fig.add_trace(go.Bar(x=mdf["month"], y=mdf["events"], name="Events", marker_color=PALETTE["secondary"], opacity=0.5))
        fig = chart_cfg(fig, h=320)
        fig.update_layout(barmode="group", legend=dict(orientation="h", y=1.08, font=dict(size=9)))
        st.plotly_chart(fig, use_container_width=True)

# ─── PAGE 2: PRODUCTIVITY ───

def page_productivity(todos):
    st.markdown('<div class="main-title">Productivity Deep Dive</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-sub">Task velocity, backlog health, and completion analytics</div>', unsafe_allow_html=True)

    done = len(todos[todos["status"] == "Done"])
    overdue = len(todos[(todos["deadline"].notna()) & (todos["deadline"] < datetime.now()) & (~todos["status"].isin(["Done", "Cancelled"]))])
    avg_cycle = todos["days_to_complete"].dropna().median()
    active = len(todos[todos["status"].isin(["ToDo", "InProgress", "Active"])])

    kpi_strip([
        ("Total", str(len(todos)), ""),
        ("Completed", str(done), "green"),
        ("Active", str(active), "purple"),
        ("Overdue", str(overdue), "red" if overdue > 10 else "amber"),
        ("Cycle Time", f"{avg_cycle:.0f}d", "green" if avg_cycle < 7 else "red"),
    ])

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">Velocity Burn Chart</div>', unsafe_allow_html=True)
        date_range = pd.date_range(todos["created_date"].min(), todos["created_date"].max(), freq="D")
        cum_created = []
        cum_completed = []
        for d in date_range:
            cum_created.append(len(todos[todos["created_date"] <= d]))
            cum_completed.append(len(todos[(todos["status"] == "Done") & (todos["date_actioned"].notna()) & (todos["date_actioned"] <= d)]))

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=date_range, y=cum_created, name="Created (cumulative)", line=dict(color=PALETTE["primary"], width=2.5), fill="tozeroy", fillcolor=hex_to_rgba(PALETTE["primary"], 0.08)))
        fig.add_trace(go.Scatter(x=date_range, y=cum_completed, name="Completed (cumulative)", line=dict(color=PALETTE["teal"], width=2.5), fill="tozeroy", fillcolor=hex_to_rgba(PALETTE["teal"], 0.08)))
        fig = chart_cfg(fig, h=350)
        fig.update_layout(legend=dict(orientation="h", y=1.08, font=dict(size=10)))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Status Funnel</div>', unsafe_allow_html=True)
        funnel_order = ["Backlog", "ToDo", "InProgress", "Active", "OnHold", "Done", "Cancelled"]
        funnel_data = todos["status"].value_counts().reindex(funnel_order).dropna().reset_index()
        funnel_data.columns = ["status", "count"]

        fig = go.Figure(go.Funnel(
            y=funnel_data["status"], x=funnel_data["count"],
            marker_color=[STATUS_C.get(s, PALETTE["neutral"]) for s in funnel_data["status"]],
            textinfo="value+percent initial",
            textfont=dict(size=12)
        ))
        fig = chart_cfg(fig, h=350, ml=120)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="section-title">Priority × Tag Heatmap</div>', unsafe_allow_html=True)
        tag_expanded = todos.assign(tag=todos["tags"].str.split("|")).explode("tag")
        heat = tag_expanded.groupby(["priority", "tag"])["todo_id"].count().reset_index()
        heat.columns = ["priority", "tag", "count"]
        heat_pivot = heat.pivot(index="tag", columns="priority", values="count").fillna(0)
        heat_pivot = heat_pivot.reindex(columns=["High", "Medium", "Low"])

        fig = go.Figure(data=go.Heatmap(
            z=heat_pivot.values, x=["High", "Medium", "Low"], y=heat_pivot.index.tolist(),
            colorscale=[[0, PALETTE["neutral"]], [0.5, PALETTE["teal"]], [1, PALETTE["primary"]]],
            hovertemplate="Tag: %{y}<br>Priority: %{x}<br>Count: %{z}<extra></extra>",
            showscale=False, text=heat_pivot.values.astype(int), texttemplate="%{text}"
        ))
        fig = chart_cfg(fig, h=320, ml=130)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.markdown('<div class="section-title">Cycle Time Distribution</div>', unsafe_allow_html=True)
        completed = todos[todos["days_to_complete"].notna()].copy()
        if len(completed) > 0:
            fig = go.Figure()
            for pri, color in [("High", PALETTE["alert"]), ("Medium", PALETTE["primary"]), ("Low", PALETTE["teal"])]:
                subset = completed[completed["priority"] == pri]["days_to_complete"]
                if len(subset) > 0:
                    fig.add_trace(go.Box(y=subset, name=pri, marker_color=color, boxmean=True))
            fig = chart_cfg(fig, h=320)
            fig.update_layout(yaxis_title="Days to Complete", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Overdue Risk Radar</div>', unsafe_allow_html=True)
    open_tasks = todos[~todos["status"].isin(["Done", "Cancelled"])].copy()
    open_tasks["age_days"] = (datetime.now() - open_tasks["created_date"]).dt.days
    open_tasks["priority_num"] = open_tasks["priority"].map({"High": 3, "Medium": 2, "Low": 1})

    fig = go.Figure()
    for pri, color, sym in [("High", PALETTE["alert"], "diamond"), ("Medium", PALETTE["primary"], "circle"), ("Low", PALETTE["teal"], "square")]:
        subset = open_tasks[open_tasks["priority"] == pri]
        fig.add_trace(go.Scatter(
            x=subset["age_days"], y=subset["priority_num"] + np.random.uniform(-0.2, 0.2, len(subset)),
            mode="markers", name=pri, marker=dict(color=color, size=10, symbol=sym, opacity=0.7),
            text=subset["subject"], hovertemplate="%{text}<br>Age: %{x} days<extra></extra>"
        ))
    fig.add_vrect(x0=30, x1=open_tasks["age_days"].max() + 5, fillcolor=PALETTE["alert"], opacity=0.05, line_width=0, annotation_text="Danger Zone (>30d)", annotation_position="top right")
    fig = chart_cfg(fig, h=280)
    fig.update_layout(xaxis_title="Days Since Created", yaxis=dict(tickvals=[1, 2, 3], ticktext=["Low", "Medium", "High"], title="Priority"),
                      legend=dict(orientation="h", y=1.1, font=dict(size=10)))
    st.plotly_chart(fig, use_container_width=True)

# ─── PAGE 3: HABITS ───

def page_habits(routines, rlog):
    st.markdown('<div class="main-title">Habit Mastery</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-sub">Streak tracking, consistency analysis, and daily patterns</div>', unsafe_allow_html=True)

    active = len(routines[routines["status"] == "Active"])
    best = routines.loc[routines["current_streak"].idxmax()]
    avg_90 = routines["last_90_days_rate"].mean()
    total_comp = rlog["completed"].sum()

    kpi_strip([
        ("Active Habits", str(active), ""),
        ("Best Streak", f'{int(best["current_streak"])}d', "green"),
        ("90-Day Rate", f"{avg_90:.0%}", "green" if avg_90 >= 0.7 else "red"),
        ("Total Done", f"{int(total_comp):,}", "purple"),
    ])

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    st.markdown('<div class="section-title">GitHub-Style Contribution Grid (Last 90 Days)</div>', unsafe_allow_html=True)

    end_date = rlog["completion_date"].max()
    start_90 = end_date - timedelta(days=89)
    recent = rlog[(rlog["completion_date"] >= start_90)].copy()

    habit_names = routines.sort_values("last_90_days_rate", ascending=False)["subject"].tolist()

    grid_data = []
    for habit in habit_names:
        h_data = recent[recent["routine_name"] == habit]
        daily = h_data.groupby(h_data["completion_date"].dt.date)["completed"].max().reset_index()
        daily.columns = ["date", "done"]
        date_range = pd.date_range(start_90, end_date, freq="D")
        for d in date_range:
            match = daily[daily["date"] == d.date()]
            val = int(match["done"].iloc[0]) if len(match) > 0 else 0
            grid_data.append({"habit": habit, "date": d, "week": (d - start_90).days // 7, "dow": d.weekday(), "done": val})

    gdf = pd.DataFrame(grid_data)

    for habit in habit_names[:6]:
        h_subset = gdf[gdf["habit"] == habit]
        pivot = h_subset.pivot(index="dow", columns="week", values="done").fillna(0)

        fig = go.Figure(data=go.Heatmap(
            z=pivot.values, x=[f"W{w+1}" for w in pivot.columns], y=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            colorscale=[[0, PALETTE["neutral"]], [0.5, PALETTE["teal"]], [1, PALETTE["teal"]]],
            showscale=False, hovertemplate="Week %{x}<br>%{y}<br>%{z}<extra></extra>",
            xgap=2, ygap=2
        ))
        rate = routines[routines["subject"] == habit]["last_90_days_rate"].iloc[0]
        streak = int(routines[routines["subject"] == habit]["current_streak"].iloc[0])
        fig = chart_cfg(fig, h=140, mt=30, mb=5)
        fig.update_layout(title=dict(text=f"{habit}  ·  {rate:.0%} rate  ·  {streak}d streak", font=dict(size=12)),
                          yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">Streak Leaderboard</div>', unsafe_allow_html=True)
        streak_data = routines.sort_values("current_streak", ascending=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(y=streak_data["subject"], x=streak_data["longest_streak"], orientation="h", name="Longest", marker_color=PALETTE["primary"], opacity=0.3))
        fig.add_trace(go.Bar(y=streak_data["subject"], x=streak_data["current_streak"], orientation="h", name="Current", marker_color=PALETTE["teal"],
                             text=streak_data["current_streak"].astype(int), textposition="auto"))
        fig = chart_cfg(fig, h=400, ml=150)
        fig.update_layout(barmode="overlay", legend=dict(orientation="h", y=1.08, font=dict(size=10)))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Time-of-Day Performance</div>', unsafe_allow_html=True)
        tod = routines.groupby("time_of_day")["last_90_days_rate"].mean().reset_index()
        tod.columns = ["time", "rate"]
        tod_order = {"Morning": 0, "Day": 1, "Night": 2}
        tod["order"] = tod["time"].map(tod_order)
        tod = tod.sort_values("order")

        fig = go.Figure(data=go.Scatterpolar(
            r=tod["rate"] * 100,
            theta=tod["time"],
            fill="toself",
            fillcolor=hex_to_rgba(PALETTE["teal"], 0.19),
            line=dict(color=PALETTE["teal"], width=3),
            marker=dict(size=10),
            text=[f"{r:.0%}" for r in tod["rate"]],
            textposition="top center"
        ))
        fig = chart_cfg(fig, h=400)
        fig.update_layout(polar=dict(radialaxis=dict(range=[0, 100], showticklabels=True, tickfont=dict(size=9))))
        st.plotly_chart(fig, use_container_width=True)

# ─── PAGE 4: WELLBEING ───

def page_wellbeing(journal, todos, rlog):
    st.markdown('<div class="main-title">Wellbeing Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-sub">Mood patterns, journaling impact, and cross-system correlations</div>', unsafe_allow_html=True)

    good_pct = len(journal[journal["mood"].isin(["Great", "Good"])]) / max(len(journal), 1)
    avg_mood = journal["mood_score"].mean()
    entries = len(journal)
    avg_ec = journal["entry_count"].mean()

    kpi_strip([
        ("Positive Days", f"{good_pct:.0%}", "green" if good_pct > 0.5 else "red"),
        ("Avg Mood", f"{avg_mood:.1f}/5", "green" if avg_mood >= 3.5 else "amber"),
        ("Entries", str(entries), ""),
        ("Avg Detail", f"{avg_ec:.1f}", "purple"),
    ])

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Mood Calendar (6 Months)</div>', unsafe_allow_html=True)

    j_sorted = journal.sort_values("date")
    min_date = j_sorted["date"].min()
    max_date = j_sorted["date"].max()
    all_dates = pd.date_range(min_date, max_date, freq="D")

    mood_by_date = journal.set_index("date")["mood_score"].to_dict()

    weeks = []
    for d in all_dates:
        week_num = (d - min_date).days // 7
        weeks.append({"date": d, "week": week_num, "dow": d.weekday(), "score": mood_by_date.get(d, 0)})

    wdf = pd.DataFrame(weeks)
    pivot = wdf.pivot(index="dow", columns="week", values="score").fillna(0)

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=[f"W{w+1}" for w in pivot.columns],
        y=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        colorscale=[[0, PALETTE["neutral"]], [0.2, PALETTE["alert"]], [0.4, PALETTE["soft_pink"]], [0.6, PALETTE["soft_pink"]], [0.8, PALETTE["teal"]], [1, PALETTE["teal"]]],
        showscale=True, colorbar=dict(title="Mood", tickvals=[1, 2, 3, 4, 5], ticktext=["Bad", "Low", "Okay", "Good", "Great"], len=0.5),
        hovertemplate="Week %{x}<br>%{y}<br>Score: %{z}<extra></extra>",
        xgap=2, ygap=2
    ))
    fig = chart_cfg(fig, h=200, mt=10, mb=10)
    fig.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">Mood Trend + Rolling Average</div>', unsafe_allow_html=True)
        rolling = j_sorted["mood_score"].rolling(7, center=True).mean()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=j_sorted["date"], y=j_sorted["mood_score"], mode="markers", name="Daily",
            marker=dict(color=[MOOD_C.get(m, PALETTE["neutral"]) for m in j_sorted["mood"]], size=7, opacity=0.6)
        ))
        fig.add_trace(go.Scatter(x=j_sorted["date"], y=rolling, mode="lines", name="7-Day Avg", line=dict(color=PALETTE["primary"], width=3)))
        fig.add_hline(y=3, line_dash="dot", line_color=PALETTE["neutral"], opacity=0.3)
        fig = chart_cfg(fig, h=320)
        fig.update_layout(yaxis=dict(tickvals=[1, 2, 3, 4, 5], ticktext=["Bad", "Low", "Okay", "Good", "Great"], range=[0.5, 5.5]),
                          legend=dict(orientation="h", y=1.08, font=dict(size=10)))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Mood × Day of Week (Polar)</div>', unsafe_allow_html=True)
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dow_mood = journal.groupby("day_of_week")["mood_score"].mean().reindex(day_order).reset_index()
        dow_mood.columns = ["day", "score"]

        fig = go.Figure(data=go.Scatterpolar(
            r=dow_mood["score"], theta=dow_mood["day"],
            fill="toself", fillcolor=hex_to_rgba(PALETTE["secondary"], 0.13), line=dict(color=PALETTE["secondary"], width=2.5),
            marker=dict(size=8, color=[PALETTE["teal"] if s >= 3.5 else PALETTE["soft_pink"] if s >= 3.0 else PALETTE["alert"] for s in dow_mood["score"]])
        ))
        fig = chart_cfg(fig, h=320)
        fig.update_layout(polar=dict(radialaxis=dict(range=[1, 5], tickvals=[1, 2, 3, 4, 5], ticktext=["Bad", "Low", "Ok", "Good", "Great"], tickfont=dict(size=8))))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="section-title">Mood × Productivity Correlation</div>', unsafe_allow_html=True)
        j_dates = journal.copy()
        j_dates["d"] = j_dates["date"].dt.date
        t_done_daily = todos[todos["date_actioned"].notna()].groupby(todos[todos["date_actioned"].notna()]["date_actioned"].dt.date)["todo_id"].count().reset_index()
        t_done_daily.columns = ["d", "tasks_done"]

        merged = j_dates.merge(t_done_daily, on="d", how="left").fillna(0)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=merged["tasks_done"], y=merged["mood_score"], mode="markers",
            marker=dict(color=[MOOD_C.get(m, PALETTE["neutral"]) for m in merged["mood"]], size=10, opacity=0.6),
            text=merged["date"].dt.strftime("%Y-%m-%d"),
            hovertemplate="Date: %{text}<br>Tasks: %{x}<br>Mood: %{y}<extra></extra>"
        ))
        if len(merged) > 5:
            z = np.polyfit(merged["tasks_done"], merged["mood_score"], 1)
            p = np.poly1d(z)
            x_line = np.linspace(merged["tasks_done"].min(), merged["tasks_done"].max(), 50)
            fig.add_trace(go.Scatter(x=x_line, y=p(x_line), mode="lines", line=dict(color=PALETTE["primary"], dash="dash", width=2), name="Trend", showlegend=False))

        fig = chart_cfg(fig, h=320)
        fig.update_layout(xaxis_title="Tasks Completed That Day", yaxis_title="Mood Score", yaxis=dict(range=[0.5, 5.5]))
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.markdown('<div class="section-title">Journaling Impact on Mood</div>', unsafe_allow_html=True)
        all_dates = pd.date_range(journal["date"].min(), journal["date"].max(), freq="D")
        j_set = set(journal["date"].dt.date)
        j_dates_list = journal.set_index("date")["mood_score"]

        with_journal = journal["mood_score"].mean()
        without_dates = [d.date() for d in all_dates if d.date() not in j_set]
        without_journal = 3.0

        fig = go.Figure()
        fig.add_trace(go.Bar(x=["With Journal Entry", "Without Entry"], y=[with_journal, without_journal],
                             marker_color=[PALETTE["teal"], PALETTE["neutral"]], text=[f"{with_journal:.2f}", f"{without_journal:.2f}"], textposition="auto",
                             textfont=dict(size=16, color="white")))
        fig = chart_cfg(fig, h=320)
        fig.update_layout(yaxis=dict(range=[0, 5], title="Avg Mood Score"))
        st.plotly_chart(fig, use_container_width=True)


# ─── MAIN ───

def main():
    todos, events, routines, rlog, journal = load_data()

    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding: 1rem 0;">
            <div style="font-size: 2rem;">🧠</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: white; letter-spacing: -0.02em;">Life OS</div>
            <div style="font-size: 0.7rem; color: rgba(255,255,255,0.5); margin-top: 2px;">Personal Analytics Engine</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")

        page = st.radio("", ["Command Centre", "Productivity", "Habit Mastery", "Wellbeing"], label_visibility="collapsed")

        st.markdown("---")
        st.markdown("""
        <div style="color: rgba(255,255,255,0.4); font-size: 0.65rem; line-height: 1.6;">
            <div style="color: rgba(255,255,255,0.6); font-weight: 600; font-size: 0.7rem; margin-bottom: 6px;">ARCHITECTURE</div>
            📧 Gmail → ⚡ GAS → 📊 Notion → 🤖 Claude<br><br>
            <div style="color: rgba(255,255,255,0.6); font-weight: 600; font-size: 0.7rem; margin-bottom: 6px;">DATABASES</div>
            01 ToDo · 02 Event · 05 Routine · 09 Journal<br><br>
            <div style="color: rgba(255,255,255,0.6); font-weight: 600; font-size: 0.7rem; margin-bottom: 6px;">DATA</div>
            Synthetic demo · 6 months<br><br>
            Built with Claude Code<br>
            © 2026 Yuji Yamane
        </div>
        """, unsafe_allow_html=True)

    if page == "Command Centre":
        page_command(todos, events, routines, rlog, journal)
    elif page == "Productivity":
        page_productivity(todos)
    elif page == "Habit Mastery":
        page_habits(routines, rlog)
    elif page == "Wellbeing":
        page_wellbeing(journal, todos, rlog)


if __name__ == "__main__":
    main()
