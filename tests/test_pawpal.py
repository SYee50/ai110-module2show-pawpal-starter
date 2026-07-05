"""Tests for PawPal+ core classes."""

import os
import sys
from datetime import date, timedelta

# Put the project root on sys.path so `import pawpal_system` works when
# pytest is run from anywhere.
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pawpal_system import Owner, Pet, Scheduler, Task


def test_task_completion_marks_complete():
    """Calling mark_complete() flips the task's status to completed."""
    task = Task("Morning walk", 30)
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    """Adding a task to a Pet increases that pet's task count by one."""
    owner = Owner("Jordan")
    pet = Pet("Biscuit", "dog", "Golden Retriever", owner)
    owner.add_pet(pet)
    assert len(pet.get_tasks()) == 0

    pet.add_task(Task("Feeding", 10))

    assert len(pet.get_tasks()) == 1


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _owner_with_pets(*pet_specs):
    """Build an Owner with the given pets.

    Each spec is (pet_name, [Task, ...]); the tasks are attached to that pet.
    Returns (owner, [pet, ...]) so callers can reach individual pets.
    """
    owner = Owner("Jordan")
    pets = []
    for name, tasks in pet_specs:
        pet = Pet(name, "dog", "Mixed", owner)
        for task in tasks:
            pet.add_task(task)
        owner.add_pet(pet)
        pets.append(pet)
    return owner, pets


# ---------------------------------------------------------------------------
# Recurring tasks
# ---------------------------------------------------------------------------


def test_completing_recurring_task_creates_next_occurrence():
    """Completing a daily task auto-adds a fresh, incomplete follow-up task."""
    owner, (pet,) = _owner_with_pets(("Biscuit", [Task("Morning walk", 30, frequency="daily")]))
    assert len(pet.get_tasks()) == 1

    original = pet.get_tasks()[0]
    original.mark_complete()

    # The pet now has two tasks: the completed original and its recurrence.
    assert len(pet.get_tasks()) == 2
    new_task = pet.get_tasks()[1]
    assert new_task.completed is False
    assert new_task.description == original.description
    assert new_task.frequency == "daily"


def test_completing_non_recurring_task_creates_nothing():
    """A one-off task (frequency='none') spawns no follow-up when completed."""
    owner, (pet,) = _owner_with_pets(("Biscuit", [Task("Vet visit", 60, frequency="none")]))

    pet.get_tasks()[0].mark_complete()

    assert len(pet.get_tasks()) == 1


def test_daily_recurrence_advances_due_date_by_one_day():
    """Completing a daily task sets the new task's due_date to the following day."""
    today = date(2026, 7, 5)
    owner, (pet,) = _owner_with_pets(
        ("Biscuit", [Task("Walk", 30, frequency="daily", due_date=today)])
    )

    pet.get_tasks()[0].mark_complete()

    new_task = pet.get_tasks()[1]
    assert new_task.due_date == today + timedelta(days=1)


def test_weekly_recurrence_advances_due_date_by_seven_days():
    """Completing a weekly task sets the new task's due_date one week later."""
    today = date(2026, 7, 5)
    owner, (pet,) = _owner_with_pets(
        ("Biscuit", [Task("Bath", 30, frequency="weekly", due_date=today)])
    )

    pet.get_tasks()[0].mark_complete()

    new_task = pet.get_tasks()[1]
    assert new_task.due_date == today + timedelta(days=7)


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------


def test_filter_tasks_by_completion():
    """filter_tasks(completed=...) returns only tasks with that status."""
    done = Task("Feeding", 10, completed=True)
    pending = Task("Walk", 30)
    owner, _ = _owner_with_pets(("Biscuit", [done, pending]))
    scheduler = Scheduler(owner)

    assert scheduler.filter_tasks(completed=True) == [done]
    assert scheduler.filter_tasks(completed=False) == [pending]
    # No filter returns everything.
    assert set(id(t) for t in scheduler.filter_tasks()) == {id(done), id(pending)}


def test_filter_tasks_by_pet():
    """filter_tasks(pet_name=...) returns only that pet's tasks."""
    biscuit_task = Task("Walk", 30)
    mochi_task = Task("Litter box", 10)
    owner, _ = _owner_with_pets(
        ("Biscuit", [biscuit_task]),
        ("Mochi", [mochi_task]),
    )
    scheduler = Scheduler(owner)

    assert scheduler.filter_tasks(pet_name="Biscuit") == [biscuit_task]
    assert scheduler.filter_tasks(pet_name="Mochi") == [mochi_task]


# ---------------------------------------------------------------------------
# Sorting
# ---------------------------------------------------------------------------


def test_sort_by_time_orders_earliest_first():
    """sort_by_time() orders out-of-order tasks from earliest to latest start."""
    late = Task("Evening walk", 30, time="17:00")
    early = Task("Morning walk", 30, time="08:00")
    midday = Task("Lunch feed", 10, time="12:30")
    owner, _ = _owner_with_pets(("Biscuit", [late, early, midday]))
    scheduler = Scheduler(owner)

    ordered = scheduler.sort_by_time(scheduler.filter_tasks())

    assert [t.time for t in ordered] == ["08:00", "12:30", "17:00"]


def test_sort_places_untimed_tasks_last():
    """A task with no time (time=None) sorts after all timed tasks."""
    untimed = Task("Anytime play", 20)  # time defaults to None
    timed = Task("Morning walk", 30, time="08:00")
    owner, _ = _owner_with_pets(("Biscuit", [untimed, timed]))
    scheduler = Scheduler(owner)

    ordered = scheduler.sort_by_time(scheduler.filter_tasks())

    assert ordered[0].time == "08:00"
    assert ordered[-1].time is None


def test_sort_mixes_timed_and_untimed_tasks_correctly():
    """Timed tasks come out chronologically, with every untimed task after them."""
    owner, _ = _owner_with_pets(
        (
            "Biscuit",
            [
                Task("Anytime play", 20),  # None
                Task("Evening walk", 30, time="17:00"),
                Task("Grooming", 15),  # None
                Task("Morning walk", 30, time="08:00"),
            ],
        )
    )
    scheduler = Scheduler(owner)

    ordered = scheduler.sort_by_time(scheduler.filter_tasks())

    # Timed tasks first (earliest -> latest), then the untimed ones.
    assert [t.time for t in ordered] == ["08:00", "17:00", None, None]


# ---------------------------------------------------------------------------
# Robustness across pet counts (zero / one / many)
# ---------------------------------------------------------------------------


def test_functionality_with_one_pet():
    """Filtering and sorting work for an owner with a single pet."""
    owner, _ = _owner_with_pets(
        ("Biscuit", [Task("Walk", 30, time="09:00"), Task("Feed", 10, time="08:00")])
    )
    scheduler = Scheduler(owner)

    assert len(scheduler.filter_tasks()) == 2
    ordered = scheduler.sort_by_time(scheduler.filter_tasks())
    assert [t.time for t in ordered] == ["08:00", "09:00"]


def test_functionality_with_multiple_pets():
    """Filtering and sorting span tasks across two or more pets."""
    owner, _ = _owner_with_pets(
        ("Biscuit", [Task("Walk", 30, time="09:00")]),
        ("Mochi", [Task("Feed", 10, time="08:00")]),
        ("Rex", [Task("Play", 20, time="10:00")]),
    )
    scheduler = Scheduler(owner)

    assert len(scheduler.filter_tasks()) == 3
    ordered = scheduler.sort_by_time(scheduler.filter_tasks())
    assert [t.time for t in ordered] == ["08:00", "09:00", "10:00"]


def test_functionality_with_no_pets_does_not_error():
    """An owner with no pets returns empty results instead of raising."""
    owner = Owner("Jordan")
    scheduler = Scheduler(owner)

    assert scheduler.filter_tasks() == []
    assert scheduler.filter_tasks(completed=True) == []
    assert scheduler.filter_tasks(pet_name="Ghost") == []
    assert scheduler.sort_by_time([]) == []
    assert scheduler.detect_conflicts() == []
    assert scheduler.build_schedule() == {}


# ---------------------------------------------------------------------------
# Conflict detection (same start time -> warning, not crash)
# ---------------------------------------------------------------------------


def test_same_start_time_produces_warning_without_error():
    """Two tasks at the same time are flagged as a conflict, no exception raised."""
    owner, _ = _owner_with_pets(
        ("Biscuit", [Task("Walk", 30, time="08:00")]),
        ("Mochi", [Task("Feed", 10, time="08:00")]),
    )
    scheduler = Scheduler(owner)

    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "08:00" in warnings[0]
    # The scheduler still builds a plan despite the conflict (no crash).
    assert scheduler.build_schedule() is not None


def test_no_conflict_when_times_differ():
    """Distinct start times produce no conflict warnings."""
    owner, _ = _owner_with_pets(
        ("Biscuit", [Task("Walk", 30, time="08:00"), Task("Feed", 10, time="09:00")])
    )
    scheduler = Scheduler(owner)

    assert scheduler.detect_conflicts() == []
