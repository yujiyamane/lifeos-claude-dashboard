# Life OS Dashboard — Streamlit × Claude Code

> **A personal productivity operating system visualised: Gmail → GAS → Notion → Claude pipeline with interactive analytics**

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Claude Code](https://img.shields.io/badge/Claude_Code-FF6B35?style=for-the-badge&logo=anthropic&logoColor=white)](https://claude.ai/claude-code)

---

## 🚀 Live Demo

**[→ Open Dashboard](https://lifeos-claude-dashboard-gppbqbstnycryefokhn95g.streamlit.app/)**

---

## 📊 What Is This?

This dashboard visualises a real personal productivity system (Life OS) built on a **Gmail → Google Apps Script → Notion → Claude** pipeline. The public demo uses synthetic data; the architecture mirrors a production system used daily.

### The Life OS Architecture

```
📧 Gmail (trigger)
  ↓
⚡ Google Apps Script (routing + parsing)
  ↓
📊 Notion (9 databases: ToDo, Event, Routine, Journal, etc.)
  ↓
🤖 Claude (intelligence + automation)
  ↓
📈 Streamlit (this dashboard)
```

### Why This Matters

Most people use productivity tools passively. Life OS treats personal data as a **pipeline** — every email, task, event, and journal entry flows through a structured system that enables analytics, automation, and AI-powered insights.

---

## 📈 Dashboard Pages

### Page 1: Overview
Cross-database KPI cards, weekly task velocity, monthly event/journal activity dual-axis chart.

### Page 2: Productivity
Task status funnel, tag distribution, priority × status breakdown, time-to-completion histogram with median reference line.

### Page 3: Habits & Routines
Current vs longest streak comparison, 90-day completion rates, daily completion heatmap (habit × day-of-week).

### Page 4: Wellbeing
Mood trend with 7-day rolling average, mood distribution pie, mood × day-of-week correlation, monthly frequency and mood dual-axis.

---

## 🔧 Local Development

```bash
git clone https://github.com/yujiyamane/lifeos-claude-dashboard.git
cd lifeos-claude-dashboard
pip install -r requirements.txt
cd data && python generate_data.py && cd ..
streamlit run app.py
```

---

## 📁 File Structure

```
lifeos-claude-dashboard/
├── app.py                    # Main Streamlit application (4 pages)
├── requirements.txt
├── .streamlit/
│   └── config.toml
├── data/
│   ├── generate_data.py      # Synthetic data generator
│   ├── todos.csv             # 300 task records
│   ├── events.csv            # 250 event records
│   ├── routines.csv          # 12 habit definitions
│   ├── routine_log.csv       # 2,268 daily completion logs
│   └── journal.csv           # 150 journal entries
├── docs/
│   ├── architecture.md       # System architecture documentation
│   └── before_after.md       # Development impact analysis
└── screenshots/
```

---

## 🧠 Data Model

### 01 ToDo (300 records)
| Field | Description |
|-------|-------------|
| subject | Task description |
| status | ToDo, Backlog, OnHold, InProgress, Done, Cancelled, Active |
| priority | High, Medium, Low |
| tags | Work, Home, Property, Cheer, School, Subscription, Routine |
| person | Person A, Person B, Person C, Family |
| deadline, date_actioned | Date tracking |

### 02 Event (250 records)
| Field | Description |
|-------|-------------|
| subject | Event title |
| event_date, time, end_time | Scheduling |
| status | Upcoming, Done, Cancelled |
| tags | Work, Social, Personal, Cheer, School, Home, Travel, Property |
| location | Venue name |

### 05 Routine (12 habits, 2,268 daily logs)
| Field | Description |
|-------|-------------|
| subject | Habit name |
| time_of_day | Morning, Day, Night |
| current_streak, longest_streak | Streak tracking |
| last_90_days_rate | Recent consistency |
| routine_log | Daily completion records |

### 09 Journal (150 entries)
| Field | Description |
|-------|-------------|
| date | Journal date |
| mood | Great, Good, Okay, Low, Bad |
| entry_count | Number of entries |
| tags | Reflection, Property |

---

## ⚡ Before / After

### Life OS System (Full Pipeline)
| Component | Traditional | Claude Code | Improvement |
|-----------|-------------|-------------|-------------|
| **Email Processing Pipeline** | 2-3 weeks | 1 week | **67% reduction** |
| **Notion Database Design** | 1 week | 3 days | **57% reduction** |
| **GAS Integration** | 1 week | 2 days | **71% reduction** |

### Dashboard Visualization (This Repo)
| Metric | Traditional | Claude Code | Improvement |
|--------|-------------|-------------|-------------|
| **Streamlit Development** | 1 week | 1 hour | **99% reduction** |
| **Data Generation** | 2 days | 2 minutes | **99.9% reduction** |
| **Documentation** | 1 day | 2 minutes | **99.9% reduction** |

---

## 👨‍💻 Author

**Yuji Yamane** — BI Developer | AI-augmented analytics
- GitHub: [yujiyamane](https://github.com/yujiyamane)
- Location: Sydney, Australia

---

## 🏗️ Related Projects

| Case | Focus | Repo |
|------|-------|------|
| Case 1 | Power BI × Healthcare KPI | [powerbi-claude-health](https://github.com/yujiyamane/powerbi-claude-health) |
| Case 2 | Streamlit × ED Performance | [streamlit-claude-health](https://github.com/yujiyamane/streamlit-claude-health) |
| **Case 3** | **Life OS × Personal Analytics** | **This repo** |
# Chart colors unified with PALETTE system
