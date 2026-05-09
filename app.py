import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import os

st.set_page_config(
    page_title="Life OS Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

PRIMARY = "#002664"
SECONDARY = "#C00000"
ACCENT_GREEN = "#00843D"
ACCENT_AMBER = "#F7931E"
ACCENT_PURPLE = "#6B21A8"
MOOD_COLORS = {"Great": "#00843D", "Good": "#4CAF50", "Okay": "#F7931E", "Low": "#FF6B35", "Bad": "#C00000"}
STATUS_COLORS = {"Done": ACCENT_GREEN, "InProgress": PRIMARY, "ToDo": ACCENT_AMBER, "Backlog": "#8896AB", "OnHold": "#666", "Cancelled": "#CCC", "Active": ACCENT_PURPLE}

st.markdown("""
<style>
    .main-header { font-size: 2rem; font-weight: 700; color: #002664; margin-bottom: 0.5rem; }
    .sub-header { font-size: 1rem; color: #666; margin-bottom: 2rem; }
    .metric-card {
        background: white; padding: 1.2rem; border-radius: 8px;
        border-left: 4px solid #002664; box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #002664; }
    .metric-label { font-size: 0.85rem; color: #666; text-transform: uppercase; letter-spacing: 0.05em; }
    .alert-red { border-left-color: #C00000 !important; }
    .alert-red .metric-value { color: #C00000 !important; }
    .alert-green { border-left-color: #00843D !important; }
    .alert-green .metric-value { color: #00843D !important; }
    .alert-purple { border-left-color: #6B21A8 !important; }
    .alert-purple .metric-value { color: #6B21A8 !important; }
    div[data-testid="stSidebar"] { background-color: #002664; }
    div[data-testid="stSidebar"] .stMarkdown { color: white; }
    div[data-testid="stSidebar"] label { color: white !important; }
</style>
""", unsafe_allow_html=True)


def metric(label, value, suffix="", alert=""):
    cls = f"metric-card {alert}"
    st.markdown(f'<div class="{cls}"><div class="metric-label">{label}</div><div class="metric-value">{value}{suffix}</div></div>', unsafe_allow_html=True)


@st.cache_data
def load_data():
    base = os.path.dirname(__file__)
    data_dir = os.path.join(base, "data")
    if not os.path.exists(os.path.join(data_dir, "todos.csv")):
        data_dir = base

    todos = pd.read_csv(os.path.join(data_dir, "todos.csv"))
    todos["created_date"] = pd.to_datetime(todos["created_date"])
    todos["deadline"] = pd.to_datetime(todos["deadline"])
    todos["date_actioned"] = pd.to_datetime(todos["date_actioned"])

    events = pd.read_csv(os.path.join(data_dir, "events.csv"))
    events["event_date"] = pd.to_datetime(events["event_date"])

    routines = pd.read_csv(os.path.join(data_dir, "routines.csv"))
    routine_log = pd.read_csv(os.path.join(data_dir, "routine_log.csv"))
    routine_log["completion_date"] = pd.to_datetime(routine_log["completion_date"])

    journal = pd.read_csv(os.path.join(data_dir, "journal.csv"))
    journal["date"] = pd.to_datetime(journal["date"])

    return todos, events, routines, routine_log, journal


def page_overview(todos, events, routines, routine_log, journal):
    st.markdown('<div class="main-header">Life OS Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Personal productivity system powered by Gmail → GAS → Notion → Claude</div>', unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        open_tasks = len(todos[todos["status"].isin(["ToDo", "InProgress", "Active"])])
        metric("Open Tasks", open_tasks, alert="alert-red" if open_tasks > 50 else "")
    with c2:
        done_pct = len(todos[todos["status"] == "Done"]) / len(todos)
        metric("Completion Rate", f"{done_pct:.0%}", alert="alert-green" if done_pct > 0.5 else "")
    with c3:
        upcoming = len(events[events["status"] == "Upcoming"])
        metric("Upcoming Events", upcoming, alert="alert-purple")
    with c4:
        avg_streak = routines["current_streak"].mean()
        metric("Avg Streak", f"{avg_streak:.0f}", " days", alert="alert-green" if avg_streak > 5 else "")
    with c5:
        recent_mood = journal.sort_values("date").tail(7)["mood"].mode()
        mood_text = recent_mood.iloc[0] if len(recent_mood) > 0 else "N/A"
        mood_alert = "alert-green" if mood_text in ["Great", "Good"] else "alert-red" if mood_text in ["Low", "Bad"] else ""
        metric("Recent Mood", mood_text, alert=mood_alert)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        weekly = todos.copy()
        weekly["week"] = weekly["created_date"].dt.isocalendar().week.astype(int)
        weekly["year_week"] = weekly["created_date"].dt.strftime("%Y-W%U")
        created_weekly = weekly.groupby("year_week")["todo_id"].count().reset_index()
        created_weekly.columns = ["week", "created"]

        done_weekly = todos[todos["status"] == "Done"].copy()
        done_weekly["year_week"] = done_weekly["date_actioned"].dt.strftime("%Y-W%U")
        completed_weekly = done_weekly.groupby("year_week")["todo_id"].count().reset_index()
        completed_weekly.columns = ["week", "completed"]

        merged = pd.merge(created_weekly, completed_weekly, on="week", how="outer").fillna(0).sort_values("week")

        fig = go.Figure()
        fig.add_trace(go.Bar(x=merged["week"], y=merged["created"], name="Created", marker_color=PRIMARY, opacity=0.7))
        fig.add_trace(go.Bar(x=merged["week"], y=merged["completed"], name="Completed", marker_color=ACCENT_GREEN, opacity=0.7))
        fig.update_layout(
            title="Weekly Task Velocity (Created vs Completed)",
            template="plotly_white", height=380, barmode="group",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            margin=dict(t=60, b=40)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        monthly_events = events.groupby("month")["event_id"].count().reset_index()
        monthly_events.columns = ["month", "count"]
        monthly_events = monthly_events.sort_values("month")

        monthly_journal = journal.groupby("month")["journal_id"].count().reset_index()
        monthly_journal.columns = ["month", "count"]

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(x=monthly_events["month"], y=monthly_events["count"], name="Events", marker_color=ACCENT_PURPLE, opacity=0.7), secondary_y=False)
        fig.add_trace(go.Scatter(x=monthly_journal["month"], y=monthly_journal["count"], name="Journal Entries", line=dict(color=ACCENT_AMBER, width=3), mode="lines+markers"), secondary_y=True)
        fig.update_layout(
            title="Monthly Events & Journal Activity",
            template="plotly_white", height=380,
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            margin=dict(t=60, b=40)
        )
        fig.update_yaxes(title_text="Events", secondary_y=False)
        fig.update_yaxes(title_text="Journal Entries", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)


def page_productivity(todos):
    st.markdown('<div class="main-header">Productivity Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Task management performance and backlog health</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric("Total Tasks", len(todos))
    with c2:
        done = len(todos[todos["status"] == "Done"])
        metric("Completed", done, alert="alert-green")
    with c3:
        overdue = len(todos[(todos["deadline"].notna()) & (todos["deadline"] < datetime.now()) & (~todos["status"].isin(["Done", "Cancelled"]))])
        metric("Overdue", overdue, alert="alert-red" if overdue > 10 else "")
    with c4:
        avg_days = todos["days_to_complete"].dropna().mean()
        metric("Avg Days to Close", f"{avg_days:.1f}")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        status_counts = todos["status"].value_counts().reset_index()
        status_counts.columns = ["status", "count"]
        colors = [STATUS_COLORS.get(s, "#999") for s in status_counts["status"]]

        fig = go.Figure(data=[go.Pie(
            labels=status_counts["status"], values=status_counts["count"],
            hole=0.45, marker_colors=colors,
            textinfo="label+value"
        )])
        fig.update_layout(title="Task Status Distribution", template="plotly_white", height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        tag_data = todos["tags"].str.split("|", expand=True).stack().reset_index(level=1, drop=True).to_frame("tag")
        tag_counts = tag_data["tag"].value_counts().reset_index()
        tag_counts.columns = ["tag", "count"]

        fig = go.Figure(go.Bar(
            x=tag_counts["count"], y=tag_counts["tag"],
            orientation="h", marker_color=PRIMARY,
            text=tag_counts["count"], textposition="auto"
        ))
        fig.update_layout(title="Tasks by Tag", template="plotly_white", height=400, margin=dict(l=120))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    col3, col4 = st.columns(2)

    with col3:
        priority_status = todos.groupby(["priority", "status"])["todo_id"].count().reset_index()
        priority_status.columns = ["priority", "status", "count"]

        fig = px.bar(
            priority_status, x="priority", y="count", color="status",
            color_discrete_map=STATUS_COLORS,
            category_orders={"priority": ["High", "Medium", "Low"]}
        )
        fig.update_layout(title="Priority × Status Breakdown", template="plotly_white", height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        completed = todos[todos["days_to_complete"].notna()].copy()
        if len(completed) > 0:
            fig = px.histogram(
                completed, x="days_to_complete", nbins=20,
                color_discrete_sequence=[PRIMARY],
                labels={"days_to_complete": "Days to Complete"}
            )
            fig.add_vline(x=completed["days_to_complete"].median(), line_dash="dash", line_color=SECONDARY,
                          annotation_text=f"Median: {completed['days_to_complete'].median():.0f} days")
            fig.update_layout(title="Time to Completion Distribution", template="plotly_white", height=400)
            st.plotly_chart(fig, use_container_width=True)


def page_habits(routines, routine_log):
    st.markdown('<div class="main-header">Habits & Routines</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Daily habit tracking, streaks, and consistency analysis</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric("Active Habits", len(routines[routines["status"] == "Active"]))
    with c2:
        best = routines.loc[routines["current_streak"].idxmax()]
        metric("Best Streak", f"{int(best['current_streak'])}", f" ({best['subject'][:12]})", alert="alert-green")
    with c3:
        avg_90 = routines["last_90_days_rate"].mean()
        metric("90-Day Avg Rate", f"{avg_90:.0%}", alert="alert-green" if avg_90 > 0.7 else "alert-red")
    with c4:
        total_completions = routine_log["completed"].sum()
        metric("Total Completions", f"{int(total_completions):,}")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        streak_data = routines.sort_values("current_streak", ascending=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=streak_data["subject"], x=streak_data["current_streak"],
            orientation="h", name="Current", marker_color=ACCENT_GREEN,
            text=streak_data["current_streak"].astype(int), textposition="auto"
        ))
        fig.add_trace(go.Bar(
            y=streak_data["subject"], x=streak_data["longest_streak"],
            orientation="h", name="Longest", marker_color=PRIMARY, opacity=0.4
        ))
        fig.update_layout(
            title="Current vs Longest Streaks", template="plotly_white",
            height=450, barmode="overlay", margin=dict(l=150),
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        rate_data = routines.sort_values("last_90_days_rate", ascending=True)
        colors = [ACCENT_GREEN if r >= 0.7 else ACCENT_AMBER if r >= 0.5 else SECONDARY for r in rate_data["last_90_days_rate"]]
        fig = go.Figure(go.Bar(
            y=rate_data["subject"], x=rate_data["last_90_days_rate"] * 100,
            orientation="h", marker_color=colors,
            text=[f"{r:.0%}" for r in rate_data["last_90_days_rate"]], textposition="auto"
        ))
        fig.add_vline(x=70, line_dash="dash", line_color="gray", annotation_text="Target 70%")
        fig.update_layout(
            title="Last 90 Days Completion Rate", template="plotly_white",
            height=450, xaxis_title="Completion %", xaxis_range=[0, 100], margin=dict(l=150)
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Daily Completion Heatmap")

    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heatmap = routine_log.groupby(["routine_name", "day_of_week"])["completed"].mean().reset_index()
    heatmap_pivot = heatmap.pivot(index="routine_name", columns="day_of_week", values="completed")
    heatmap_pivot = heatmap_pivot.reindex(columns=day_order)

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_pivot.values * 100,
        x=day_order,
        y=heatmap_pivot.index.tolist(),
        colorscale=[[0, SECONDARY], [0.5, ACCENT_AMBER], [1, ACCENT_GREEN]],
        colorbar_title="Completion %",
        hovertemplate="Habit: %{y}<br>Day: %{x}<br>Rate: %{z:.0f}%<extra></extra>"
    ))
    fig.update_layout(template="plotly_white", height=400, margin=dict(l=150, t=20))
    st.plotly_chart(fig, use_container_width=True)


def page_wellbeing(journal):
    st.markdown('<div class="main-header">Wellbeing & Journal</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Mood tracking, journaling frequency, and sentiment patterns</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric("Total Entries", len(journal))
    with c2:
        good_pct = len(journal[journal["mood"].isin(["Great", "Good"])]) / len(journal)
        metric("Positive Days", f"{good_pct:.0%}", alert="alert-green" if good_pct > 0.5 else "alert-red")
    with c3:
        avg_entries = journal["entry_count"].mean()
        metric("Avg Entry Count", f"{avg_entries:.1f}")
    with c4:
        journal_days = journal["date"].nunique()
        coverage = journal_days / TOTAL_DAYS if TOTAL_DAYS > 0 else 0
        metric("Journal Coverage", f"{coverage:.0%}")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        journal_sorted = journal.sort_values("date")
        mood_numeric = journal_sorted["mood"].map({"Great": 5, "Good": 4, "Okay": 3, "Low": 2, "Bad": 1})
        rolling_mood = mood_numeric.rolling(7, center=True).mean()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=journal_sorted["date"], y=mood_numeric,
            mode="markers", name="Daily Mood",
            marker=dict(color=[MOOD_COLORS.get(m, "#999") for m in journal_sorted["mood"]], size=8),
        ))
        fig.add_trace(go.Scatter(
            x=journal_sorted["date"], y=rolling_mood,
            mode="lines", name="7-Day Average",
            line=dict(color=PRIMARY, width=3)
        ))
        fig.update_layout(
            title="Mood Trend Over Time",
            yaxis=dict(tickvals=[1, 2, 3, 4, 5], ticktext=["Bad", "Low", "Okay", "Good", "Great"]),
            template="plotly_white", height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        mood_counts = journal["mood"].value_counts().reindex(["Great", "Good", "Okay", "Low", "Bad"]).reset_index()
        mood_counts.columns = ["mood", "count"]

        fig = go.Figure(data=[go.Pie(
            labels=mood_counts["mood"], values=mood_counts["count"],
            hole=0.45,
            marker_colors=[MOOD_COLORS[m] for m in mood_counts["mood"]],
            textinfo="label+percent"
        )])
        fig.update_layout(title="Mood Distribution", template="plotly_white", height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    col3, col4 = st.columns(2)

    with col3:
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        mood_map = {"Great": 5, "Good": 4, "Okay": 3, "Low": 2, "Bad": 1}
        journal["mood_score"] = journal["mood"].map(mood_map)
        dow_mood = journal.groupby("day_of_week")["mood_score"].mean().reset_index()
        dow_mood["day_order"] = dow_mood["day_of_week"].map({d: i for i, d in enumerate(day_order)})
        dow_mood = dow_mood.sort_values("day_order")

        colors = [ACCENT_GREEN if s >= 3.5 else ACCENT_AMBER if s >= 3.0 else SECONDARY for s in dow_mood["mood_score"]]
        fig = go.Figure(go.Bar(
            x=dow_mood["day_of_week"], y=dow_mood["mood_score"],
            marker_color=colors,
            text=[f"{s:.2f}" for s in dow_mood["mood_score"]], textposition="auto"
        ))
        fig.update_layout(
            title="Average Mood by Day of Week",
            yaxis=dict(tickvals=[1, 2, 3, 4, 5], ticktext=["Bad", "Low", "Okay", "Good", "Great"], range=[1, 5]),
            template="plotly_white", height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        monthly_mood = journal.groupby("month").agg(
            avg_mood=("mood_score", "mean"),
            entries=("journal_id", "count")
        ).reset_index().sort_values("month")

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(
            x=monthly_mood["month"], y=monthly_mood["entries"],
            name="Entries", marker_color=PRIMARY, opacity=0.6
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=monthly_mood["month"], y=monthly_mood["avg_mood"],
            name="Avg Mood", line=dict(color=ACCENT_GREEN, width=3), mode="lines+markers"
        ), secondary_y=True)
        fig.update_layout(
            title="Monthly Journal Frequency & Mood",
            template="plotly_white", height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        fig.update_yaxes(title_text="Entries", secondary_y=False)
        fig.update_yaxes(title_text="Avg Mood Score", secondary_y=True, range=[1, 5])
        st.plotly_chart(fig, use_container_width=True)


TOTAL_DAYS = 189

def main():
    todos, events, routines, routine_log, journal = load_data()

    with st.sidebar:
        st.markdown("## 🧠 Life OS")
        st.markdown("---")

        page = st.radio(
            "Navigation",
            ["Overview", "Productivity", "Habits & Routines", "Wellbeing"],
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.markdown("### Architecture")
        st.markdown(
            "<div style='color: rgba(255,255,255,0.8); font-size: 0.8rem;'>"
            "Gmail → GAS → Notion → Claude<br><br>"
            "📧 Email triggers<br>"
            "⚡ Apps Script routing<br>"
            "📊 Notion databases<br>"
            "🤖 Claude intelligence"
            "</div>",
            unsafe_allow_html=True
        )

        st.markdown("---")
        st.markdown(
            "<div style='color: rgba(255,255,255,0.5); font-size: 0.75rem;'>"
            "Built with Claude Code<br>"
            "Data: Synthetic demo<br>"
            "© 2026 Yuji Yamane"
            "</div>",
            unsafe_allow_html=True
        )

    if page == "Overview":
        page_overview(todos, events, routines, routine_log, journal)
    elif page == "Productivity":
        page_productivity(todos)
    elif page == "Habits & Routines":
        page_habits(routines, routine_log)
    elif page == "Wellbeing":
        page_wellbeing(journal)


if __name__ == "__main__":
    main()
