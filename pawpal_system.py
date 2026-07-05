"""PawPal+ core system.

Implements the four classes from diagrams/uml.mmd:

    Owner -> Pet(s) -> Task(s), with a Scheduler that reads an Owner and builds
    a conflict-free daily plan across all of that owner's pets.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

# Task recurrence options ("how often"). Stored for future filtering; the
# scheduler currently plans every incomplete task once.
FREQUENCIES = ("none", "daily", "weekly", "monthly", "annually")


def to_minutes(hhmm: str) -> int:
    """Convert an 'HH:MM' string to minutes since midnight ('08:30' -> 510)."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


def to_hhmm(minutes: int) -> str:
    """Convert minutes since midnight back to 'HH:MM' (510 -> '08:30')."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------


@dataclass
class Task:
    """A single pet-care activity (e.g. a walk, feeding, or meds)."""

    description: str
    duration_minutes: int
    frequency: str = "daily"  # one of FREQUENCIES
    completed: bool = False
    time: str | None = None  # scheduled/preferred time of day, "HH:MM"
    due_date: "date | None" = None  # when the task is due (used for recurrence)
    # Back-reference to the owning pet; set automatically by Pet.add_task().
    pet: "Pet | None" = field(default=None, repr=False, compare=False)

    def mark_complete(self) -> "Task | None":
        """Mark complete; for daily/weekly tasks, spawn the next occurrence."""
        self.completed = True
        next_task = self.next_occurrence()
        if next_task is not None and self.pet is not None:
            self.pet.add_task(next_task)
        return next_task

    def next_occurrence(self) -> "Task | None":
        """Return a fresh Task for the next date, or None if it doesn't recur.

        Only "daily" (+1 day) and "weekly" (+7 days) recur. The next date is
        advanced from this task's due_date, or from today if none is set.
        """
        if self.frequency == "daily":
            delta = timedelta(days=1)
        elif self.frequency == "weekly":
            delta = timedelta(weeks=1)
        else:
            return None
        base = self.due_date or date.today()
        return Task(
            self.description,
            self.duration_minutes,
            frequency=self.frequency,
            time=self.time,
            due_date=base + delta,
        )

    def __str__(self) -> str:
        """Render like: 'Morning walk (30 min)'."""
        # If priority is added later, append e.g. f" [priority: {label}]" here.
        return f"{self.description} ({self.duration_minutes} min)"


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------


@dataclass(eq=False)  # identity equality so Pet is hashable (used as dict keys)
class Pet:
    """Stores a pet's details and its list of tasks."""

    name: str
    species: str
    breed: str
    owner: "Owner" = field(repr=False)  # back-reference; repr=False avoids recursion
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet and record the pet on the task."""
        task.pet = self
        self.tasks.append(task)

    def remove_task(self, description: str) -> bool:
        """Remove the task matching `description`. Returns True if removed."""
        before = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.description != description]
        return len(self.tasks) < before

    def get_tasks(self) -> list[Task]:
        """Return this pet's tasks."""
        return self.tasks

    def header(self) -> str:
        """Label for the plan header, e.g. 'Biscuit (Golden Retriever)'."""
        label = self.breed or self.species
        return f"{self.name} ({label})"


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------


@dataclass
class Owner:
    """Manages multiple pets and the owner's daily time availability."""

    name: str
    start_time: str = "08:00"  # start of the owner's available window ("HH:MM")
    end_time: str = "18:00"  # end of the owner's available window ("HH:MM")
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, name: str) -> bool:
        """Remove the pet matching `name`. Returns True if removed."""
        before = len(self.pets)
        self.pets = [p for p in self.pets if p.name != name]
        return len(self.pets) < before

    def find_pet(self, name: str) -> Pet | None:
        """Return the pet matching `name`, or None."""
        for pet in self.pets:
            if pet.name == name:
                return pet
        return None

    def available_minutes(self) -> int:
        """Total minutes in the owner's daily availability window."""
        return to_minutes(self.end_time) - to_minutes(self.start_time)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------


class Scheduler:
    """The 'brain': retrieves, organizes, and manages tasks across pets.

    Builds one shared timeline for the owner so no two tasks -- across any of
    the owner's pets -- overlap. A single pet's schedule is extracted from that
    shared plan, guaranteeing it never conflicts with another pet's.
    """

    def __init__(self, owner: Owner) -> None:
        """Store the owner whose pets this scheduler plans."""
        self.owner = owner

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted by their 'HH:MM' time attribute (earliest first)."""
        # Zero-padded "HH:MM" strings sort correctly as text; tasks with no
        # time set (None) fall back to "99:99" so they land at the end.
        return sorted(tasks, key=lambda task: task.time or "99:99")

    def filter_tasks(
        self, completed: bool | None = None, pet_name: str | None = None
    ) -> list[Task]:
        """Return the owner's tasks, optionally filtered by completion and/or pet name."""
        result = []
        for pet in self.owner.pets:
            if pet_name is not None and pet.name != pet_name:
                continue
            for task in pet.tasks:
                if completed is not None and task.completed != completed:
                    continue
                result.append(task)
        return result

    def detect_conflicts(self) -> list[str]:
        """Return warning messages for tasks sharing the same time (never raises).

        Lightweight check: two incomplete tasks -- for the same pet or different
        pets -- that have the same "HH:MM" time are flagged. Tasks with no time
        set are ignored. Returns an empty list when there are no conflicts.
        """
        by_time: dict[str, list[tuple[Pet, Task]]] = {}
        for pet in self.owner.pets:
            for task in pet.tasks:
                if task.completed or task.time is None:
                    continue
                by_time.setdefault(task.time, []).append((pet, task))

        warnings = []
        for time_str in sorted(by_time):
            entries = by_time[time_str]
            if len(entries) > 1:
                labels = ", ".join(
                    f"{task.description} ({pet.name})" for pet, task in entries
                )
                warnings.append(f"⚠️  Conflict at {time_str}: {labels}")
        return warnings

    def build_schedule(self) -> dict[Pet, list[tuple[str, Task]]]:
        """Build one conflict-free plan across all pets, round-robin and time-packed."""
        plan: dict[Pet, list[tuple[str, Task]]] = {pet: [] for pet in self.owner.pets}
        cursor = to_minutes(self.owner.start_time)
        end = to_minutes(self.owner.end_time)

        # One queue of incomplete tasks per pet, plus a cursor into each.
        queues = {pet: [t for t in pet.tasks if not t.completed] for pet in self.owner.pets}
        idx = {pet: 0 for pet in self.owner.pets}

        # Round-robin: take one task from each pet in turn until all are placed
        # or skipped. (idx always advances, so this terminates.)
        while any(idx[pet] < len(queues[pet]) for pet in self.owner.pets):
            for pet in self.owner.pets:
                if idx[pet] >= len(queues[pet]):
                    continue
                task = queues[pet][idx[pet]]
                idx[pet] += 1
                if cursor + task.duration_minutes <= end:
                    plan[pet].append((to_hhmm(cursor), task))
                    cursor += task.duration_minutes
                # else: no room left in the window for this task -> skip it
        return plan

    def get_pet_schedule(self, pet: Pet) -> list[tuple[str, Task]]:
        """Return one pet's schedule, extracted from the shared conflict-free plan."""
        return self.build_schedule().get(pet, [])

    def format_pet_schedule(self, pet: Pet) -> str:
        """Format one pet's schedule as terminal text."""
        return self._format(pet, self.get_pet_schedule(pet))

    def format_all_schedules(self) -> str:
        """Format every pet's schedule, one block per pet."""
        plan = self.build_schedule()
        return "\n\n".join(self._format(pet, plan[pet]) for pet in self.owner.pets)

    @staticmethod
    def _format(pet: Pet, entries: list[tuple[str, Task]]) -> str:
        """Shared renderer: header line plus one line per scheduled task."""
        lines = [f"Daily plan for {pet.header()}:"]
        if not entries:
            lines.append("  (no tasks scheduled)")
        for time_str, task in entries:
            lines.append(f"  {time_str} — {task}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Demo runner
# ---------------------------------------------------------------------------


def _demo() -> None:
    """Build sample data and print a plan so the logic can be seen end-to-end."""
    jordan = Owner("Jordan", start_time="08:00", end_time="10:00")

    biscuit = Pet("Biscuit", "dog", "Golden Retriever", jordan)
    biscuit.add_task(Task("Morning walk", 30, frequency="daily"))
    biscuit.add_task(Task("Feeding", 10, frequency="daily"))
    jordan.add_pet(biscuit)

    mochi = Pet("Mochi", "cat", "Tabby", jordan)
    mochi.add_task(Task("Feeding", 10, frequency="daily"))
    mochi.add_task(Task("Litter box", 10, frequency="daily"))
    jordan.add_pet(mochi)

    scheduler = Scheduler(jordan)

    print("=== All pets ===")
    print(scheduler.format_all_schedules())

    print("\n=== Just Biscuit ===")
    print(scheduler.format_pet_schedule(biscuit))


if __name__ == "__main__":
    _demo()
