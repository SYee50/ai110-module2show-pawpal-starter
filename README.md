# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## ✨ Features

PawPal+ implements the following scheduling algorithms and behaviors:

- **Sorting by time** — orders tasks chronologically by their `HH:MM` preferred time (earliest first), with untimed tasks pushed to the end (`Scheduler.sort_by_time`).
- **Filtering** — returns the owner's tasks filtered by completion status, by pet name, by both, or unfiltered — every filter argument is optional (`Scheduler.filter_tasks`).
- **Conflict warnings** — flags incomplete tasks that share the same preferred time, whether for the same pet or across different pets, returning human-readable warning strings instead of raising errors (`Scheduler.detect_conflicts`).
- **Conflict-free daily plan** — packs each pet's incomplete tasks into non-overlapping time slots within the owner's availability window, using a round-robin pass across pets so no two tasks ever overlap (`Scheduler.build_schedule`).
- **Daily & weekly recurrence** — completing a recurring task automatically spawns its next occurrence, advancing the due date by +1 day (daily) or +7 days (weekly); non-recurring tasks do not respawn (`Task.mark_complete`, `Task.next_occurrence`).
- **Availability window** — the owner defines a start and end time; the scheduler only places tasks that fit inside the remaining window and skips those that don't (`Owner.available_minutes`, `Scheduler.build_schedule`).

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
Today's Schedule for Jordan
================================
Daily plan for Biscuit (Golden Retriever):
  08:00 — Morning walk (30 min)
  08:40 — Feeding (10 min)

Daily plan for Mochi (Tabby):
  08:30 — Feeding (10 min)
  08:50 — Litter box (15 min)

```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Run with coverage:
python -m pytest --cov
```

### What the tests cover

- **Task basics** — Marking a task complete flips its status and adding a task to a pet increases that pet's task count.
- **Recurring tasks** — Completing a daily or weekly task automatically creates the next occurrence with its due date advanced by the right amount (+1 day or +7 days), while a non-recurring task does not automatically create another occurrence.
- **Filtering** — filter_tasks() returns tasks filtered by completion status, by pet name, and with no filter (every task is returned).
- **Sorting** — sort_by_time() returns tasks in chronological order even when they were added out of order, and pushes untimed tasks to the end.
- **Robustness across pet counts** — Filtering and sorting behave correctly with one pet, two-or-more pets, and no pets (an empty owner returns empty results instead of crashing the program or erroring).
- **Conflict detection** — Two tasks sharing a start time produce a warning (without crashing the program), while distinct times do not produce a warning.

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.8.13, pytest-8.3.5, pluggy-1.5.0
collected 16 items

tests/test_pawpal.py ................                                    [100%]

============================== 16 passed in 0.01s ==============================
```

### Confidence Level

4 stars

## 📐 Smarter Scheduling


| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | Scheduler.sort_by_time() | Sorts tasks by their "HH:MM" time attribute (earliest first and untimed tasks sort to the end) |
| Filtering | Scheduler.filter_tasks() | Filters the owner's tasks by completion status, by pet name, by both, or neither (both arguments optional) |
| Conflict handling | Scheduler.detect_conflicts() | Flags incomplete tasks sharing the same start time (same pet or across pets). Returns a list of warning strings instead of raising an error. |
| Recurring tasks | Task.mark_complete(), Task.next_occurrence() | Completing a daily or weekly task automatically creates the next occurrence, advancing the due date by +1 day or +7 days |


## 📸 Demo Walkthrough

PawPal+ runs as a Streamlit app (`streamlit run app.py`). This walkthrough describes the interface, a typical workflow, and the Scheduler behaviors you'll see along the way.

### The main UI

The app is a single scrolling page with these sections, top to bottom:

- **Owner** — set the owner's name and daily availability window (`Available from` / `Available until` as `HH:MM`).
- **Add a Pet** — enter a pet's name, species, and breed, then submit to attach it to the owner.
- **Add a Task** — pick which pet the task is for, then enter a description, duration (minutes), frequency (none/daily/weekly/monthly/annually), and an optional preferred time. The preferred time is what drives sorting and conflict detection.
- **Current Pets & Tasks** — a filterable, sorted table of every task. Two dropdowns let you filter **by pet** and **by status** (To do / Completed / All); the results are always sorted by preferred time.
- **Build Schedule** — a button that generates the conflict-free daily plan, shows any timing-conflict warnings, and renders one table per pet.

### Example workflow

1. **Set the availability window** — e.g. Jordan, available `08:00`–`18:00`.
2. **Add a pet** — add "Biscuit," a Golden Retriever dog. A green success message confirms it.
3. **Schedule some tasks** — add "Morning walk" (30 min, daily, `08:00`) and "Feeding" (10 min, daily, `08:00`) to Biscuit.
4. **Review the task list** — scroll to **Current Pets & Tasks**; the table shows both tasks sorted by time. Filter by status "To do" to hide completed ones.
5. **Generate today's schedule** — click **Generate schedule**. Because both tasks want `08:00`, an amber conflict warning appears above the plan, followed by a per-pet table showing the tasks packed into non-overlapping slots (`08:00` and `08:30`).

### Key Scheduler behaviors shown

- **Sorting by time** — the Current Pets & Tasks table lists tasks earliest-first, untimed tasks last, regardless of the order they were added.
- **Filtering** — the pet/status dropdowns scope the table down to a single pet or only to-do / completed tasks.
- **Conflict warnings** — tasks sharing a preferred time surface one amber `st.warning` per clashing slot, with a follow-up note explaining the plan already spaced them out. No clashes shows a green "no conflicts" message.
- **Conflict-free packing** — even when preferred times collide, **Build Schedule** assigns each task its own non-overlapping slot inside the availability window.

### Sample CLI output

The same core logic can be exercised from the terminal with `python main.py`, which builds two pets with tasks added out of order (and a deliberate 12:00 clash) to demonstrate sorting, filtering, and conflict detection:

```
PawPal+ sorting & filtering demo
==================================

All tasks (insertion order):
      17:00  [todo]  Evening walk (30 min)
      08:00  [done]  Morning walk (30 min)
      12:00  [todo]  Lunch feeding (10 min)
      12:00  [todo]  Give meds (5 min)
      15:00  [todo]  Litter box (15 min)
      09:00  [done]  Breakfast (10 min)
      12:00  [todo]  Midday play (20 min)

All tasks (sorted by time):
      08:00  [done]  Morning walk (30 min)
      09:00  [done]  Breakfast (10 min)
      12:00  [todo]  Lunch feeding (10 min)
      12:00  [todo]  Give meds (5 min)
      12:00  [todo]  Midday play (20 min)
      15:00  [todo]  Litter box (15 min)
      17:00  [todo]  Evening walk (30 min)

Filter -> incomplete only:
      17:00  [todo]  Evening walk (30 min)
      12:00  [todo]  Lunch feeding (10 min)
      12:00  [todo]  Give meds (5 min)
      15:00  [todo]  Litter box (15 min)
      12:00  [todo]  Midday play (20 min)

Filter -> completed only:
      08:00  [done]  Morning walk (30 min)
      09:00  [done]  Breakfast (10 min)

Filter -> Biscuit's tasks:
      17:00  [todo]  Evening walk (30 min)
      08:00  [done]  Morning walk (30 min)
      12:00  [todo]  Lunch feeding (10 min)
      12:00  [todo]  Give meds (5 min)

Filter+sort -> Mochi's remaining tasks by time:
      12:00  [todo]  Midday play (20 min)
      15:00  [todo]  Litter box (15 min)

Conflict check:
  ⚠️  Conflict at 12:00: Lunch feeding (Biscuit), Give meds (Biscuit), Midday play (Mochi)
```
