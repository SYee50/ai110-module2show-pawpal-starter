import streamlit as st

# Bring the backend classes into the UI so button clicks can drive real logic.
from pawpal_system import FREQUENCIES, Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# Persist the Owner in st.session_state so it survives Streamlit's reruns.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")

# Convenience handle to the persisted owner for the rest of the script.
owner = st.session_state.owner

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# --- Owner settings ---------------------------------------------------------
# Writing back to the persisted owner keeps these edits across reruns.
st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)
col_start, col_end = st.columns(2)
with col_start:
    owner.start_time = st.text_input("Available from (HH:MM)", value=owner.start_time)
with col_end:
    owner.end_time = st.text_input("Available until (HH:MM)", value=owner.end_time)

st.divider()

# --- Add a pet --------------------------------------------------------------
# Owner.add_pet() is the method that handles the submitted pet data.
st.subheader("Add a Pet")
with st.form("add_pet_form", clear_on_submit=True):
    new_pet_name = st.text_input("Pet name", value="Mochi")
    new_pet_species = st.selectbox("Species", ["dog", "cat", "other"])
    new_pet_breed = st.text_input("Breed", value="")
    if st.form_submit_button("Add pet"):
        if new_pet_name.strip():
            owner.add_pet(Pet(new_pet_name, new_pet_species, new_pet_breed, owner))
            st.success(f"Added {new_pet_name}.")
        else:
            st.warning("Please enter a pet name.")

st.divider()

# --- Add a task to a pet ----------------------------------------------------
# Pet.add_task() attaches the task to the chosen pet.
st.subheader("Add a Task")
if not owner.pets:
    st.info("Add a pet first, then you can give it tasks.")
else:
    with st.form("add_task_form", clear_on_submit=True):
        target_pet_name = st.selectbox("For which pet?", [p.name for p in owner.pets])
        description = st.text_input("Task description", value="Morning walk")
        col1, col2, col3 = st.columns(3)
        with col1:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        with col2:
            frequency = st.selectbox("Frequency", list(FREQUENCIES), index=list(FREQUENCIES).index("daily"))
        with col3:
            # Preferred time drives sorting and conflict detection in Scheduler.
            preferred_time = st.text_input("Preferred time (HH:MM, optional)", value="")
        if st.form_submit_button("Add task"):
            pet = owner.find_pet(target_pet_name)
            time_value = preferred_time.strip() or None
            pet.add_task(
                Task(description, int(duration), frequency=frequency, time=time_value)
            )
            st.success(f"Added '{description}' to {pet.name}.")

st.divider()

# --- Current pets & tasks (sorted & filtered via the Scheduler) -------------
st.subheader("Current Pets & Tasks")
if not owner.pets:
    st.info("No pets yet. Add one above.")
else:
    scheduler = Scheduler(owner)

    # Filter controls -> Scheduler.filter_tasks(); "All" maps to None.
    col_pet, col_status = st.columns(2)
    with col_pet:
        pet_choice = st.selectbox(
            "Filter by pet", ["All pets"] + [p.name for p in owner.pets]
        )
    with col_status:
        status_choice = st.selectbox(
            "Filter by status", ["All", "To do", "Completed"]
        )

    pet_filter = None if pet_choice == "All pets" else pet_choice
    completed_filter = (
        None if status_choice == "All" else (status_choice == "Completed")
    )

    # Ask the Scheduler for the filtered set, then sort it by preferred time.
    tasks = scheduler.filter_tasks(completed=completed_filter, pet_name=pet_filter)
    tasks = scheduler.sort_by_time(tasks)

    if tasks:
        st.table(
            [
                {
                    "Time": t.time or "—",
                    "Pet": t.pet.name if t.pet else "—",
                    "Task": t.description,
                    "Duration (min)": t.duration_minutes,
                    "Frequency": t.frequency,
                    "Status": "✅ Done" if t.completed else "⏳ To do",
                }
                for t in tasks
            ]
        )
        st.caption(f"Showing {len(tasks)} task(s), sorted by preferred time.")
    else:
        st.info("No tasks match these filters.")

st.divider()

# --- Build schedule ---------------------------------------------------------
# Scheduler reads the persisted owner, warns about timing conflicts, and
# produces a conflict-free daily plan.
st.subheader("Build Schedule")
if st.button("Generate schedule"):
    if not owner.pets:
        st.warning("Add a pet and some tasks first.")
    else:
        scheduler = Scheduler(owner)

        # Surface preferred-time collisions BEFORE showing the plan, so the
        # owner reads the caveat first. One warning per conflicting slot.
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            for warning in conflicts:
                st.warning(warning)
            st.info(
                "These tasks share the same preferred time. The plan below "
                "already spaces them out into separate slots — but you may "
                "want to adjust their preferred times so the schedule matches "
                "your routine."
            )
        else:
            st.success("No timing conflicts — every task has a clear slot 🎉")

        # Show the generated conflict-free plan, one table per pet.
        plan = scheduler.build_schedule()
        for pet in owner.pets:
            st.markdown(f"**Daily plan for {pet.header()}**")
            entries = plan[pet]
            if entries:
                st.table(
                    [
                        {
                            "Time": time_str,
                            "Task": task.description,
                            "Duration (min)": task.duration_minutes,
                        }
                        for time_str, task in entries
                    ]
                )
            else:
                st.caption("No tasks scheduled.")
