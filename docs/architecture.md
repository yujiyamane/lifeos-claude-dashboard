# Life OS Architecture

## System Overview

Life OS is a personal productivity system that transforms fragmented daily inputs (emails, voice memos, calendar invites) into structured, actionable data through an automated pipeline.

## Pipeline Architecture

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌──────────────┐
│   Gmail     │───▶│  Google Apps     │───▶│    Notion       │───▶│   Claude     │
│  (Trigger)  │    │  Script (Router) │    │  (9 Databases)  │    │ (AI Layer)   │
└─────────────┘    └──────────────────┘    └─────────────────┘    └──────────────┘
       │                    │                       │                      │
   Emails            Parse + Route           Store + Query         Analyse + Act
   Voice memos       Label + Forward         Filter + View        Summarise
   Calendar          Transform data          Track progress       Automate
```

## Database Layer (Notion)

| DB | Purpose | Key Metrics |
|----|---------|-------------|
| 01 ToDo | Task management | Status flow, priority, completion velocity |
| 02 Event | Calendar events | Scheduling density, tag distribution |
| 05 Routine | Habit tracking | Streaks, completion rates, consistency |
| 09 Journal | Daily reflection | Mood trends, entry frequency, sentiment |

## Data Flow Examples

### Email → ToDo
1. Email arrives in Gmail with specific label/keyword
2. GAS trigger fires, parses subject/sender/date
3. Creates Notion page in 01 ToDo with auto-tagged properties
4. Claude Daily Brief surfaces it next morning

### Voice Memo → Journal
1. Voice memo recorded on phone, synced to Gmail
2. GAS detects audio attachment, transcribes (UTF-16 BE handling)
3. Creates Notion page in 09 Journal with mood classification
4. Dashboard shows mood trend update

### Calendar Invite → Event
1. ICS attachment arrives via email
2. GAS parses ICS, extracts date/time/location
3. Creates Notion page in 02 Event + syncs to Google Calendar
4. Family calendar routing: person-based calendar assignment

## Analytics Layer (This Dashboard)

```
Notion APIs ──▶ Python (pandas) ──▶ Streamlit + Plotly
                     │
              Synthetic data (public demo)
              Live Notion API (private version)
```

## Key Design Principles

1. **Zero manual data entry** — everything flows from email or voice
2. **Single source of truth** — Notion is the canonical store
3. **AI as intelligence layer** — Claude adds analysis, not just storage
4. **Observable system** — this dashboard makes the invisible visible
