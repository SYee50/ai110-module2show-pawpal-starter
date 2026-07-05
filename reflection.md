# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial UML design includes the classes, attributes, and methods that will be used for the PawPal+ app to create a daily schedule of pet care tasks for pet owners. The app will allow owners to enter information about themselves, including their priorities and constraints, as well as information about their pets and required tasks. This data will then be used to create a daily schedule that takes into account the owner's available time, priorities, constraints, and number of pets. The UML contains four classes: Owner, Pet, Task, and Scheduler. The Owner, Pet, and Task classes are primarily used to store data. For example, the Owner class contains the owner's name, priorities, constraints, and list of pets. The Pet class contains the pet's name, the owner's name, and a list of tasks. The Task class contains the task name, duration, and priority. Finally, the Scheduler class is responsible for generating the daily schedule by organizing tasks based on their priority while considering the owner's available time, constraints, and the tasks that need to be completed for all pets.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

The design did change during implementation. One change was replacing the owner's name (stored as a string) in the Pet class with a reference to the Owner object. This allows Pet objects to directly access Owner attributes and methods if needed, making the design more flexible. Another change was refining the purpose of the method that retrieves all tasks. Initially, it could have been used to generate an overall daily task plan, but the project requires daily plans to be pet-specific. Instead, the method is now intended only for features such as task prioritization and scheduling conflict detection across multiple pets, while each pet's daily plan is generated separately. Both changes were made after I asked Claude about potential missing relationships and logic bottlenecks.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

My scheduler considers two time-based constraints. The first is the owner's daily availability window. The scheduler only places tasks that fit inside this window and skips any task that would run past the end time, so the daily plan never exceeds the time the owner has available. The second constraint is each task's preferred time, which is used for sorting (tasks are ordered chronologically by their "HH:MM" time) and conflict detection (two incomplete tasks that request the same start time are flagged as a conflict).

I decided that time was the constraint that mattered most for the scheduler because often times in a real world scenario a pet owner's primary problem is fitting a fixed set of daily care tasks into a limited window without double-booking themselves. Preferred time and the availability window directly address these problems. Keeping the constraints to time and availability made the logic simpler, easier to test, and a better fit for the purpose of the app.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff that my scheduler makes is that it detects scheduling conflicts only when two tasks have the exact same start time. It does not check whether tasks with different start times overlap based on their durations. This tradeoff is reasonable because it keeps the scheduling algorithm simple, easy to understand, and easy to test. Detecting overlapping tasks would require comparing task time ranges, handling durations, and accounting for additional edge cases. Since the scheduler is intended to manage and organize a small number of pet care tasks that are entered and reviewed by an owner, checking for exact start-time conflicts is sufficient for catching the most common scheduling mistakes while keeping the implementation straightforward.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI for design brainstorming, debugging, and refactoring. During the design phase, I used AI to help brainstorm features, such as the scheduling constraints to implement and how to organize my classes and their relationships. For debugging, I asked AI to identify edge cases, suggest additional test scenarios that I had not considered, and generate pytest cases to verify my implementation. During refactoring, I used AI to help improve existing code as my design evolved. The most helpful prompts were asking AI to suggest additional tests to make my test suite more robust and to evaluate whether a section of code correctly implemented the intended functionality or could be improved through refactoring.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

One moment where I did not accept an AI suggestion as-is was when it suggested adding a test for None preferred task times, since this value is optional in the app. Instead of immediately adding the suggested test, I was unsure what behavior it was trying to verify and why it was relevant. I asked the AI to explain the purpose of the test and how it related to the app. Based on that discussion, the AI explained what the test was intending to verify and why it was important for the app and produced a slightly revised version of the test. After looking over the explanation and the updated pytest, I decided that it covered an important edge case and added the test to the test suite.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested the behaviors of each class, with a focus on the scheduling logic. For tasks, I verified that marking a task complete changes its status, adding a task increases the pet's task count, and completing a daily or weekly task creates the next occurrence with its due date advanced correctly (+1 day or +7 days), while a non-recurring task does not create a follow-up task. For the Scheduler, I tested filtering (by status, by pet, and with no filter), sorting (chronological order with untimed tasks placed at the end), and conflict detection (matching start times produce a warning without crashing, while distinct times do not). I also tested these features with one pet, multiple pets, and no pets to confirm that empty inputs return empty results instead of causing errors. These tests were important because they cover the primary logic that the app depends on. The current task table utilizes filtering and sorting, while the Generate Schedule button utilizes conflict detection and schedule building. The recurrence logic required thorough testing because it is one of the more complex parts of the program, making it more susceptible to subtle bugs. The zero pet and untimed task cases are important edge cases because they represent common potentailly problematic scenarios that the app could encounter and should be able to handle.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am fairly confident that my scheduler works correctly. I tested the main scheduling functionality, recurrence logic, filtering, sorting, conflict detection, and several edge cases, including empty inputs and untimed tasks. Running these tests gave me confidence that the scheduler behaves as expected under normal use and common edge cases. If I had more time, I would test more unusual combinations of filters and sorting options, as well as larger numbers of pets and tasks to ensure the scheduler continues to behave correctly as the amount of inputs increases.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The part of this project I am most satisfied with is how seamlessly the UI connected with the backend logic. I was surprised by how easily the frontend components interacted with the underlying classes and scheduling functionality. Seeing the completed app in the browser, where a user could immediately enter information and generate daily plans, was surprising because I expected there to be a few hiccups. Watching everything work together as intended was very satisfying.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

If I had another iteration, I would improve the conflict detection by making it more nuanced. Instead of only checking whether tasks have the same start time, I would incorporate task durations to detect overlapping tasks. I would also add more scheduling flexibility by allowing tasks to have a secondary preferred time or a maximum delay window, giving the scheduler more options for generating a conflict-free schedule.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

One important thing I learned is that it is valuable to understand the reasoning behind AI-generated suggestions rather than accepting them immediately. Asking the AI to explain its logic helped me better understand the design decisions, verify that the suggestions fit my program's requirements, and make more informed choices about what to incorporate into the project.
