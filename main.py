"""PawPal+ -- CLI test driver.

Exercises the classes in pawpal_system.py: builds an Owner with two Pets,
adds Tasks out of order, then demonstrates the Scheduler's sorting and
filtering methods in the terminal.
"""

from pawpal_system import Owner, Pet, Scheduler, Task


def show(label: str, tasks: list[Task]) -> None:
    """Print a labeled list of tasks, one per line."""
    print(f"\n{label}")
    for task in tasks:
        status = "done" if task.completed else "todo"
        print(f"  {task.time or '(no time)':>9}  [{status}]  {task}")


def main() -> None:
    jordan = Owner("Jordan", start_time="08:00", end_time="10:00")

    # Pet #1 -- tasks added OUT of chronological order, one already completed.
    biscuit = Pet("Biscuit", "dog", "Golden Retriever", jordan)
    biscuit.add_task(Task("Evening walk", 30, time="17:00"))
    biscuit.add_task(Task("Morning walk", 30, time="08:00", completed=True))
    biscuit.add_task(Task("Lunch feeding", 10, time="12:00"))
    biscuit.add_task(Task("Give meds", 5, time="12:00"))  # same-pet clash at 12:00
    jordan.add_pet(biscuit)

    # Pet #2 -- also out of order.
    mochi = Pet("Mochi", "cat", "Tabby", jordan)
    mochi.add_task(Task("Litter box", 15, time="15:00"))
    mochi.add_task(Task("Breakfast", 10, time="09:00", completed=True))
    mochi.add_task(Task("Midday play", 20, time="12:00"))  # cross-pet clash at 12:00
    jordan.add_pet(mochi)

    scheduler = Scheduler(jordan)

    print("PawPal+ sorting & filtering demo")
    print("=" * 34)

    # --- Sorting: tasks were added out of order; sort_by_time fixes that. ----
    all_tasks = jordan.get_all_tasks()
    show("All tasks (insertion order):", all_tasks)
    show("All tasks (sorted by time):", scheduler.sort_by_time(all_tasks))

    # --- Filtering: by completion status and by pet name. --------------------
    show("Filter -> incomplete only:", scheduler.filter_tasks(completed=False))
    show("Filter -> completed only:", scheduler.filter_tasks(completed=True))
    show("Filter -> Biscuit's tasks:", scheduler.filter_tasks(pet_name="Biscuit"))

    # --- Combine: Mochi's remaining tasks, sorted by time. ------------------
    mochi_todo = scheduler.filter_tasks(completed=False, pet_name="Mochi")
    show("Filter+sort -> Mochi's remaining tasks by time:",
         scheduler.sort_by_time(mochi_todo))

    # --- Conflict detection: warn on tasks scheduled at the same time. -------
    print("\nConflict check:")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"  {warning}")
    else:
        print("  No conflicts found.")


if __name__ == "__main__":
    main()
