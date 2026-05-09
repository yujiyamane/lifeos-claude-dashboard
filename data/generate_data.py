#!/usr/bin/env python3
"""
Life OS Dashboard - Dummy Data Generator

Generates realistic personal productivity data matching the Life OS Notion schema.
4 CSVs: todos, events, routines, journal entries.
All names anonymised. 6 months of data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import random
import os

np.random.seed(42)
random.seed(42)

START_DATE = date(2025, 11, 1)
END_DATE = date(2026, 5, 9)
TOTAL_DAYS = (END_DATE - START_DATE).days

PERSONS = ["Person A", "Person B", "Person C", "Family"]
PERSON_WEIGHTS = [0.55, 0.20, 0.15, 0.10]

TODO_STATUSES = ["ToDo", "Backlog", "OnHold", "InProgress", "Done", "Cancelled", "Active"]
TODO_PRIORITIES = ["High", "Medium", "Low"]
TODO_TAGS = ["Work", "Home", "Property", "Cheer", "School", "Subscription", "Routine"]
TODO_TAG_WEIGHTS = [0.25, 0.18, 0.15, 0.12, 0.10, 0.08, 0.12]

EVENT_STATUSES = ["Upcoming", "Done", "Cancelled"]
EVENT_TAGS = ["Work", "Social", "Personal", "Cheer", "School", "Home", "Travel", "Property", "Subscription"]
EVENT_TAG_WEIGHTS = [0.20, 0.15, 0.15, 0.12, 0.10, 0.10, 0.05, 0.08, 0.05]

ROUTINE_ITEMS = [
    ("Morning Reading", "Morning", 7),
    ("Journaling", "Morning", 7),
    ("Exercise", "Morning", 5),
    ("Meditation", "Morning", 7),
    ("Property Research", "Morning", 5),
    ("Language Study", "Day", 5),
    ("Code Practice", "Day", 3),
    ("Review Inbox", "Day", 7),
    ("Evening Walk", "Night", 5),
    ("Gratitude Log", "Night", 7),
    ("Stretch Routine", "Night", 5),
    ("Weekly Planning", "Morning", 1),
]

MOODS = ["Great", "Good", "Okay", "Low", "Bad"]
MOOD_WEIGHTS = [0.15, 0.35, 0.30, 0.15, 0.05]

TODO_SUBJECTS = [
    "Review quarterly budget", "Schedule dentist appointment", "Update property insurance",
    "Research investment options", "Fix garden fence", "Organise photo backup",
    "Submit tax documents", "Book car service", "Renew gym membership",
    "Plan weekend trip", "Update resume", "Review school report",
    "Call mortgage broker", "Clean garage", "Order birthday gift",
    "Set up automated backups", "Research schools nearby", "Fix leaking tap",
    "Meal prep for the week", "Cancel unused subscription",
    "Review energy bill", "Update emergency contacts", "Organise filing cabinet",
    "Book holiday accommodation", "Replace smoke detector battery",
    "Research new phone plan", "Submit council application", "Review rental yield",
    "Update household inventory", "Schedule pest inspection",
    "Prepare presentation slides", "Follow up with real estate agent",
    "Compare health insurance", "Renew passport", "Fix WiFi dead zone",
    "Organise kids sports gear", "Review strata minutes", "Plan family dinner",
    "Update LinkedIn profile", "Book eye exam", "Research solar panels",
    "Clean out wardrobe", "Set up bill reminders", "Review tenant application",
    "Arrange carpet cleaning", "Update investment spreadsheet",
    "Book team lunch", "Research after-school programs", "Fix door handle",
    "Plan anniversary celebration"
]

EVENT_SUBJECTS = [
    "Team standup", "School parent-teacher night", "Dentist checkup",
    "Property inspection", "Family BBQ", "Cheer competition",
    "Client presentation", "Weekend market", "Gym orientation",
    "Birthday party", "Mortgage meeting", "School sports day",
    "Date night", "Car service appointment", "Community cleanup",
    "Work conference", "Swimming lesson", "Sunday brunch",
    "Tax meeting with accountant", "House open for inspection",
    "Piano recital", "Neighbourhood watch meeting",
    "Annual health check", "Property settlement meeting",
    "School excursion", "Friend's wedding", "Home maintenance day",
    "Quarterly review", "Kids birthday party", "Surf lesson"
]

EVENT_LOCATIONS = [
    "Office", "School Hall", "Medical Centre", "Property Address",
    "Local Park", "Sports Centre", "Client Office", "Market Square",
    "Gym", "Restaurant", "Bank Branch", "School Oval",
    "City Centre", "Service Centre", "Community Hall", "Conference Room",
    "Pool", "Cafe", "Accountant Office", "Beach"
]


def generate_todos(n=300):
    rows = []
    for i in range(n):
        created_offset = np.random.randint(0, TOTAL_DAYS)
        created_date = START_DATE + timedelta(days=created_offset)

        is_old = created_offset < TOTAL_DAYS * 0.7
        if is_old:
            status_weights = [0.05, 0.05, 0.03, 0.02, 0.70, 0.10, 0.05]
        else:
            status_weights = [0.30, 0.15, 0.10, 0.20, 0.10, 0.05, 0.10]
        status = np.random.choice(TODO_STATUSES, p=status_weights)

        priority = np.random.choice(TODO_PRIORITIES, p=[0.20, 0.50, 0.30])

        n_tags = np.random.choice([1, 2], p=[0.7, 0.3])
        tags = list(np.random.choice(TODO_TAGS, size=n_tags, replace=False, p=TODO_TAG_WEIGHTS))

        person_count = np.random.choice([1, 2], p=[0.8, 0.2])
        persons = list(np.random.choice(PERSONS, size=person_count, replace=False, p=PERSON_WEIGHTS))

        has_deadline = np.random.random() < 0.6
        deadline = None
        if has_deadline:
            deadline_offset = np.random.randint(1, 30)
            deadline = created_date + timedelta(days=deadline_offset)

        date_actioned = None
        if status == "Done":
            days_to_complete = max(1, int(np.random.lognormal(mean=1.5, sigma=0.8)))
            date_actioned = created_date + timedelta(days=min(days_to_complete, TOTAL_DAYS - created_offset))

        subject = random.choice(TODO_SUBJECTS)

        rows.append({
            "todo_id": i + 1,
            "subject": subject,
            "status": status,
            "priority": priority,
            "tags": "|".join(tags),
            "person": "|".join(persons),
            "created_date": created_date.isoformat(),
            "deadline": deadline.isoformat() if deadline else None,
            "date_actioned": date_actioned.isoformat() if date_actioned else None,
            "days_to_complete": (date_actioned - created_date).days if date_actioned else None,
        })

    return pd.DataFrame(rows)


def generate_events(n=250):
    rows = []
    for i in range(n):
        event_offset = np.random.randint(0, TOTAL_DAYS + 30)
        event_date = START_DATE + timedelta(days=event_offset)

        if event_date <= END_DATE:
            status = np.random.choice(EVENT_STATUSES, p=[0.10, 0.80, 0.10])
        else:
            status = "Upcoming"

        n_tags = np.random.choice([1, 2], p=[0.75, 0.25])
        tags = list(np.random.choice(EVENT_TAGS, size=n_tags, replace=False, p=EVENT_TAG_WEIGHTS))

        person_count = np.random.choice([1, 2, 3], p=[0.5, 0.3, 0.2])
        persons = list(np.random.choice(PERSONS, size=min(person_count, len(PERSONS)), replace=False, p=PERSON_WEIGHTS))

        recurring = "Yes" if np.random.random() < 0.25 else "No"

        hour = np.random.choice(range(7, 20))
        minute = np.random.choice([0, 15, 30, 45])
        time_str = f"{hour:02d}:{minute:02d}"

        duration_hours = np.random.choice([0.5, 1, 1.5, 2, 3, 4], p=[0.10, 0.30, 0.15, 0.25, 0.10, 0.10])
        end_hour = hour + int(duration_hours)
        end_minute = minute + int((duration_hours % 1) * 60)
        if end_minute >= 60:
            end_hour += 1
            end_minute -= 60
        end_time = f"{min(end_hour, 23):02d}:{end_minute:02d}"

        subject = random.choice(EVENT_SUBJECTS)
        location = random.choice(EVENT_LOCATIONS)

        rows.append({
            "event_id": i + 1,
            "subject": subject,
            "event_date": event_date.isoformat(),
            "time": time_str,
            "end_time": end_time,
            "status": status,
            "tags": "|".join(tags),
            "person": "|".join(persons),
            "location": location,
            "recurring": recurring,
            "day_of_week": event_date.strftime("%A"),
            "month": event_date.strftime("%Y-%m"),
        })

    return pd.DataFrame(rows)


def generate_routines():
    rows = []
    routine_id = 1

    for name, time_of_day, target_days in ROUTINE_ITEMS:
        completion_dates = []
        current_streak = 0
        longest_streak = 0
        temp_streak = 0

        for day_offset in range(TOTAL_DAYS):
            d = START_DATE + timedelta(days=day_offset)
            if d.weekday() < target_days or (target_days == 7):
                base_prob = 0.7
                if d.weekday() >= 5:
                    base_prob *= 0.85
                day_in_month = d.day
                if day_in_month <= 7:
                    base_prob *= 1.1

                if np.random.random() < min(base_prob, 0.95):
                    completion_dates.append(d.isoformat())
                    temp_streak += 1
                    longest_streak = max(longest_streak, temp_streak)
                else:
                    temp_streak = 0

        current_streak = temp_streak
        last_90 = [d for d in completion_dates if date.fromisoformat(d) >= END_DATE - timedelta(days=90)]

        rows.append({
            "routine_id": routine_id,
            "subject": name,
            "time_of_day": time_of_day,
            "target_days": target_days,
            "status": "Active",
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "total_completions": len(completion_dates),
            "last_90_days_count": len(last_90),
            "last_90_days_rate": round(len(last_90) / 90, 3),
            "start_date": START_DATE.isoformat(),
            "person": "Person A",
        })
        routine_id += 1

    completion_log = []
    log_id = 1
    for name, time_of_day, target_days in ROUTINE_ITEMS:
        for day_offset in range(TOTAL_DAYS):
            d = START_DATE + timedelta(days=day_offset)
            base_prob = 0.7
            if d.weekday() >= 5:
                base_prob *= 0.85
            if d.day <= 7:
                base_prob *= 1.1

            completed = np.random.random() < min(base_prob, 0.95)
            completion_log.append({
                "log_id": log_id,
                "routine_name": name,
                "time_of_day": time_of_day,
                "completion_date": d.isoformat(),
                "completed": 1 if completed else 0,
                "day_of_week": d.strftime("%A"),
                "month": d.strftime("%Y-%m"),
            })
            log_id += 1

    return pd.DataFrame(rows), pd.DataFrame(completion_log)


def generate_journal(n=150):
    rows = []
    used_dates = set()

    for i in range(n):
        while True:
            day_offset = np.random.randint(0, TOTAL_DAYS)
            journal_date = START_DATE + timedelta(days=day_offset)
            if journal_date.isoformat() not in used_dates:
                used_dates.add(journal_date.isoformat())
                break

        day_of_week = journal_date.weekday()
        is_weekend = day_of_week >= 5
        is_monday = day_of_week == 0

        if is_weekend:
            mood_weights = [0.20, 0.40, 0.25, 0.10, 0.05]
        elif is_monday:
            mood_weights = [0.10, 0.30, 0.35, 0.20, 0.05]
        else:
            mood_weights = [0.15, 0.35, 0.30, 0.15, 0.05]

        mood = np.random.choice(MOODS, p=mood_weights)
        entry_count = max(1, int(np.random.normal(3, 1.5)))
        status = "Reviewed" if np.random.random() < 0.7 else "New"

        n_tags = np.random.choice([0, 1, 2], p=[0.3, 0.5, 0.2])
        tags = list(np.random.choice(["Reflection", "Property"], size=n_tags, replace=False)) if n_tags > 0 else []

        person_count = np.random.choice([1, 2], p=[0.7, 0.3])
        persons = list(np.random.choice(PERSONS[:3], size=person_count, replace=False, p=[0.6, 0.25, 0.15]))

        rows.append({
            "journal_id": i + 1,
            "date": journal_date.isoformat(),
            "mood": mood,
            "entry_count": entry_count,
            "status": status,
            "tags": "|".join(tags) if tags else "",
            "person": "|".join(persons),
            "day_of_week": journal_date.strftime("%A"),
            "month": journal_date.strftime("%Y-%m"),
        })

    return pd.DataFrame(rows).sort_values("date").reset_index(drop=True)


if __name__ == "__main__":
    print("Life OS Dashboard - Data Generation")
    print("=" * 50)

    output_dir = os.path.dirname(os.path.abspath(__file__))

    print("Generating ToDo data...")
    todos = generate_todos(300)
    todos.to_csv(os.path.join(output_dir, "todos.csv"), index=False)
    print(f"  [OK] todos.csv ({len(todos)} rows)")

    print("Generating Event data...")
    events = generate_events(250)
    events.to_csv(os.path.join(output_dir, "events.csv"), index=False)
    print(f"  [OK] events.csv ({len(events)} rows)")

    print("Generating Routine data...")
    routines, routine_log = generate_routines()
    routines.to_csv(os.path.join(output_dir, "routines.csv"), index=False)
    routine_log.to_csv(os.path.join(output_dir, "routine_log.csv"), index=False)
    print(f"  [OK] routines.csv ({len(routines)} rows)")
    print(f"  [OK] routine_log.csv ({len(routine_log)} rows)")

    print("Generating Journal data...")
    journal = generate_journal(150)
    journal.to_csv(os.path.join(output_dir, "journal.csv"), index=False)
    print(f"  [OK] journal.csv ({len(journal)} rows)")

    print(f"\nData Summary:")
    print(f"  * Period: {START_DATE} to {END_DATE}")
    print(f"  * ToDos: {len(todos)} tasks, {len(todos[todos['status']=='Done'])} completed")
    print(f"  * Events: {len(events)} events")
    print(f"  * Routines: {len(routines)} habits, {len(routine_log)} daily logs")
    print(f"  * Journal: {len(journal)} entries, avg mood breakdown:")
    for mood in MOODS:
        count = len(journal[journal["mood"] == mood])
        print(f"      {mood}: {count} ({count/len(journal):.0%})")
    print(f"\nReady for Streamlit dashboard.")
