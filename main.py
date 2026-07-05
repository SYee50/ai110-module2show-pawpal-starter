"""PawPal+ -- CLI test driver.

Exercises the classes in pawpal_system.py: builds an Owner with two Pets,
adds several Tasks, and prints today's schedule to the terminal.
"""

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    # An owner with a daily availability window of 08:00-10:00.
    jordan = Owner("Jordan", start_time="08:00", end_time="10:00")

    # Pet #1
    biscuit = Pet("Biscuit", "dog", "Golden Retriever", jordan)
    biscuit.add_task(Task("Morning walk", 30, frequency="daily"))
    biscuit.add_task(Task("Feeding", 10, frequency="daily"))
    jordan.add_pet(biscuit)

    # Pet #2
    mochi = Pet("Mochi", "cat", "Tabby", jordan)
    mochi.add_task(Task("Feeding", 10, frequency="daily"))
    mochi.add_task(Task("Litter box", 15, frequency="daily"))
    jordan.add_pet(mochi)

    # Build and print today's schedule across all pets.
    scheduler = Scheduler(jordan)

    print(f"Today's Schedule for {jordan.name}")
    print("=" * 32)
    print(scheduler.format_all_schedules())


if __name__ == "__main__":
    main()
