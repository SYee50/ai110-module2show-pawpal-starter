"""Tests for PawPal+ core classes."""

import os
import sys

# Put the project root on sys.path so `import pawpal_system` works when
# pytest is run from anywhere.
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pawpal_system import Owner, Pet, Task


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
