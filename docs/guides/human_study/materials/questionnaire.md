# Questionnaire

Scales: 1 = Strongly disagree ... 5 = Strongly agree unless stated. Items marked (R) are reverse-scored. Items are adapted in the style of established instruments (trust-in-automation scales, SUS, NASA-TLX); wording is project-specific and has not been psychometrically validated.

## A. Background (once)
- Role: student / faculty / staff / other
- Field: economics-finance / public policy / computer science / other
- Years of study or work in the field
- Familiarity with budget analysis (1-5), familiarity with machine learning (1-5)

## B. Per-case confidence (after each pre and post split)
"How confident are you in your proposed split?" 1 (not at all) ... 5 (completely)

## C. Trust in the system (T1-T8; trust_mean = mean after reversing R items)
- T1 I trusted the system's recommendations.
- T2 The system's recommendations were reliable.
- T3 I felt I could depend on the system.
- T4 I am wary of the system. (R)
- T5 I understood why the system made its recommendations.
- T6 I could tell when the system was likely to be wrong.
- T7 I would use this system in my own work as one input among others.
- T8 I would follow the system's recommendation without checking it. (R)

## D. Usability (10 SUS-style items; sus_score = SUS scoring, 0-100)
1. I think I would like to use this system frequently.
2. I found the system unnecessarily complex. (R)
3. I thought the system was easy to use.
4. I would need technical support to use this system. (R)
5. The functions in the system were well integrated.
6. There was too much inconsistency in the system. (R)
7. Most people would learn to use this system quickly.
8. I found the system very cumbersome to use. (R)
9. I felt very confident using the system.
10. I needed to learn a lot before I could get going. (R)

SUS scoring: odd items (score-1), even items (5-score); sum x 2.5.

## E. Workload (short NASA-TLX; 0-100 slider each; tlx_mean = mean of six)
Mental demand; Physical demand (optional, may drop); Temporal demand; Performance (0 = perfect, 100 = failure); Effort; Frustration.

## F. Understanding quiz (quiz_score = number correct of 5; conditions B/C only items 1-4 apply, A answers all as "cannot tell")
Answers key to be filled by researchers from the actual dashboard before use.
1. Which sector was pushing the recommended Health share UP most for the last case? (choose from the 4 sectors / cannot tell)
2. A negative explanation value for a feature means it ... (raises / lowers the predicted share / no effect)
3. What does a warning that a case is "outside the training range" imply for the recommendation? (more reliable / less reliable / no change)
4. If a country's GDP per capita were higher in a what-if scenario, what would you expect for the recommended Education share? (describe direction from the displayed scenario / cannot tell)
5. True/False: The recommended split is a prediction of the officially adopted allocation, not a guarantee it is the best allocation.

## G. Open comments
- What information did you rely on most?
- When did you decide to ignore the system and why?
