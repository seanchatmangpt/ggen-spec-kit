# Reference: JTBD Framework Terminology

Complete JTBD terminology and definitions.

## Core Concepts

### Job
Something a user needs to accomplish.
Not a feature, not a product—**an outcome or goal.**

Example: "Greet users personally"

### Situation
The context where a job arises.

Example: "When welcoming new users"

### Task
The action the user wants to do.

Example: "I want to greet each user by name"

### Outcome
The desired result.

Example: "So users feel personally welcomed"

### Success Metric
How you measure if job is accomplished.

Example: "Users report feeling welcomed (survey)"

## Framework Structure

```
Job: [What users need to accomplish]

Situation: When [context]
Task: I want to [action]
Outcome: So that [result]

Success Metrics:
- Metric 1: [measurable]
- Metric 2: [measurable]

Implementation:
- Feature 1: Enables this outcome
- Feature 2: Enables this outcome
```

## Related Concepts

### Feature
A system capability that helps accomplish a job.

Example: "Personalized greeting" is a feature
That enables the job: "Greet users"

### User Story
A narrative about a user accomplishing a job.

Example: "As a greeting agent, I want to know user names so I can greet them personally"

### Job Outcome
A specific, measurable result of completing a job.

Example: "Greeting takes < 2 seconds"

### Job Priority
Importance and effort matrix.

```
High Impact + Low Effort = DO FIRST ⭐⭐⭐
High Impact + High Effort = DO SECOND ⭐⭐
Low Impact + Low Effort = DO LATER ⭐
Low Impact + High Effort = DEPRIORITIZE
```

## JTBD Process

1. **Identify Jobs** - What do users need to accomplish?
2. **Define Outcomes** - What results matter?
3. **Measure** - How do we know job is done?
4. **Prioritize** - Which jobs matter most?
5. **Build** - Create features that enable jobs
6. **Track** - Monitor outcome metrics
7. **Improve** - Increase success rate

See: [How-to: Apply JTBD Framework](../guides/jtbd/apply-framework.md)
