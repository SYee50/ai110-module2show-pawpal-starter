"""PawPal+ core system.

Skeleton classes generated from diagrams/uml.mmd. Method bodies are stubs
(`raise NotImplementedError`) to be filled in incrementally.

Data model: Owner -> Pet(s) -> Task(s). The Scheduler reads an Owner and
builds a daily plan across all of that owner's pets.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    """A single pet-care activity (e.g. a walk, feeding, or meds)."""

    name: str
    duration_minutes: int
    priority: str = "medium"  # "low" | "medium" | "high"
    recurrence: str = "daily"  # "daily" | "weekly" | "once"
    day_of_week: str | None = None  # only meaningful when recurrence == "weekly"
    fixed_time: str | None = None  # "HH:MM" if this task must happen at a set time

    def priority_rank(self) -> int:
        """Return a sortable rank for this task's priority (higher = more urgent)."""
        raise NotImplementedError

    def is_due_today(self, day: str) -> bool:
        """Return True if this task should run on the given day."""
        raise NotImplementedError

    def __str__(self) -> str:
        """Render like: 'Morning walk (30 min) [priority: high]'."""
        raise NotImplementedError


@dataclass
class Pet:
    """One animal, owning the list of tasks that belong to it."""

    name: str
    species: str
    owner_name: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet."""
        raise NotImplementedError

    def edit_task(self, name: str, **changes) -> None:
        """Update fields of the task matching `name`."""
        raise NotImplementedError

    def remove_task(self, name: str) -> None:
        """Remove the task matching `name`."""
        raise NotImplementedError

    def get_tasks(self) -> list[Task]:
        """Return this pet's tasks."""
        raise NotImplementedError


@dataclass
class Owner:
    """Top-level aggregate: holds the pets and the owner's scheduling constraints."""

    name: str
    pets: list[Pet] = field(default_factory=list)
    day_start: str = "08:00"  # when the schedule's clock begins ("HH:MM")
    available_minutes: int = 120  # total time budget for the day
    priorities: list[str] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        raise NotImplementedError

    def edit_pet(self, name: str, **changes) -> None:
        """Update fields of the pet matching `name`."""
        raise NotImplementedError

    def remove_pet(self, name: str) -> None:
        """Remove the pet matching `name`."""
        raise NotImplementedError

    def get_all_tasks(self) -> list[Task]:
        """Collect tasks across all of this owner's pets."""
        raise NotImplementedError


class Scheduler:
    """Builds a daily plan for an owner across all of their pets.

    Holds no task data of its own -- it reads the Owner and organizes the
    tasks. This is where the algorithmic features live.
    """

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def generate_schedule(self, day: str) -> dict:
        """Main entry point: build a per-pet daily plan for the given day."""
        raise NotImplementedError

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Algorithm 1 -- order tasks by priority, then duration."""
        raise NotImplementedError

    def filter_tasks(self, tasks: list[Task], budget: int) -> list[Task]:
        """Algorithm 2 -- keep tasks until the time budget runs out."""
        raise NotImplementedError

    def detect_conflicts(self, tasks: list[Task]) -> list:
        """Algorithm 3 -- find tasks whose fixed time slots overlap."""
        raise NotImplementedError

    def expand_recurring(self, day: str) -> list[Task]:
        """Algorithm 4 -- select only the tasks due on the given day."""
        raise NotImplementedError

    def assign_times(self, tasks: list[Task], start: str) -> list:
        """Walk the clock from `start`, giving each task a start time."""
        raise NotImplementedError

    def format_plan(self, schedule: dict) -> str:
        """Render the schedule as the 'Daily plan for ...' text output."""
        raise NotImplementedError
