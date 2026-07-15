# Course QA record

**Date:** 2026-07-15<br>
**Branch:** `course-review-remediation`<br>
**Published-course gate:** `python3 scripts/audit_course.py --allow-planned-lessons`<br>
**Trial-dependent scope:** Lesson 5 and the result-bearing case study are intentionally deferred and were not represented as complete.

## Environment and method

- Served from `http://127.0.0.1:8765/` with Python's static HTTP server.
- Used the Hermes local browser runtime for DOM, accessibility-tree, JavaScript, keyboard, responsive, and print-rule checks.
- Emulated exact page viewports with same-origin iframes at **1280×900** and **390×844**; media queries and layout are evaluated against each iframe's own viewport.
- Attempted a background native Safari capture, but `computer_use` returned no applications/windows. This is an automation-environment limitation, not a course defect; no Safari-specific result is claimed.

## Page and viewport matrix

| Viewport | Pages | Result | Evidence |
|---|---|---|---|
| 1280×900 | Index, Lessons 1 and 4, glossary, all three reference pages, resources | Pass | Every document width equaled the 1280 px viewport; no page overflow; exactly one `<main>` and two course-navigation landmarks on each inspected non-redirect page. |
| 390×844 | Index, mission, Lessons 1–4, glossary, all three reference pages, resources | Pass | Every document width equaled the 390 px viewport; no unexplained horizontal page overflow and no uncontained offending element. |
| 390×844 | All lesson/reference table regions | Pass | Tables wider than 358 px remained inside their 358 px scroll region; the document itself remained 390 px wide. |
| 390×844 | All lesson/reference code/formula blocks | Pass | Blocks wrapped or remained inside their containing table scroll region; none widened the document. |
| Any | Historical Lesson 3 URL | Pass | Visible, `noindex` compatibility redirect to the supported Lesson 3. |
| Any | Lesson 5 and result page | Deferred | These depend on the paused paired trials. The index shows an unlinked deferred status instead of fabricated content. |

## Quiz and keyboard QA

The shared component was exercised against **all 16 quiz questions**:

| Lesson | Questions | Wrong answer | Reveal | Reset | Correct answer |
|---|---:|---|---|---|---|
| Lesson 1 | 4 | Pass | Pass | Pass | Pass |
| Lesson 2 | 3 | Pass | Pass | Pass | Pass |
| Lesson 3 | 4 | Pass | Pass | Pass | Pass |
| Lesson 4 | 5 | Pass | Pass | Pass | Pass |

For every question the runtime check confirmed:

- a wrong answer disables all options;
- the selected option is marked incorrect and the correct option is revealed;
- feedback is non-empty, uses `role="status"`, and receives focus;
- the retry control becomes available;
- reset clears classes and feedback, re-enables options, hides itself, and focuses the first option;
- a correct answer produces the correct-state message and focuses feedback.

A keyboard-only Lesson 4 flow was also performed with `Tab`, `Shift+Tab`, and `Enter`. The focused button showed a **3 px solid accent outline with 3 px offset**. Wrong answer, retry, reset, and correct answer all worked without a pointer.

## Accessibility and presentation checks

| Check | Result | Measurement |
|---|---|---|
| Body text contrast | Pass | 17.21:1 |
| Muted/progress text contrast | Pass | 7.37:1 |
| Link contrast | Pass | 5.11:1 |
| Quiz option contrast | Pass | 17.4:1 |
| Mobile quiz targets | Pass | 15 visible options checked; minimum height 54 px; none below 44 px |
| Reduced motion | Pass | `prefers-reduced-motion: reduce` disables smooth scrolling and reduces transition/animation duration to 0.01 ms |
| Live feedback | Pass | Runtime focus plus `role="status"` verified |
| Console | Pass | No JavaScript messages or uncaught errors after navigation and interaction |

## Print behavior

Print preview was invoked and then cancelled without submitting a print job. The automation runtime could not capture the operating-system preview surface, so no pixel-level print-preview claim is made. Source/CSSOM verification confirms dedicated print rules for:

- 11 pt body text and unconstrained page width;
- hidden navigation, scroll hints, and retry controls;
- visible/non-scrolling table regions;
- worked-answer indicators;
- external-link URL expansion.

This is recorded as a tooling limitation rather than a visual pass in native Safari.

## Issue found and fixed

| ID | Severity | Category | Finding | Fix |
|---|---|---|---|---|
| QA-01 | Low | UX/content | Wrong-answer feedback added a second period when the correct option label already ended in punctuation. | `6a9a5d1` adds sentence-aware punctuation. Fresh-source runtime verification produced one period. |

## Automated corroboration

- `python3 -m unittest discover -s tests -v`: **29/29 pass**.
- `python3 scripts/audit_course.py --allow-planned-lessons`: **pass with zero findings**.
- `node --check assets/quiz.js`: **pass**.
- The same commands passed from a detached clean Git worktree.
