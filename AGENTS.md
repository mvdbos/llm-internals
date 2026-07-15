# AGENTS.md — LLM Internals Course

This repository is a dependency-free static course. Keep every public page generalizable, evidence-backed, accessible, and deployable directly on GitHub Pages.

## Canonical learner path

Lesson order, titles, durations, and paths live in `course.json`. Every lesson, worked example, quiz, takeaway, and reference card must reinforce this decision procedure in exactly this order:

1. **Identify the backend and quantized targets.** Name the artifact format, engine, mode, group/block size, calibration or importance recipe, and whether weights, activations, or cache are quantized.
2. **Calculate memory.** Prefer measured artifact/runtime allocation; otherwise estimate weights from effective bits per weight and estimate architecture-appropriate retained state/cache plus headroom separately.
3. **Shortlist formats that fit.** Include kernel/runtime compatibility and measured speed, not only size.
4. **Evaluate the exact workload.** Use paired task instances, controlled settings, repetitions where stochastic, and task-specific quality metrics.
5. **Choose the Pareto point.** Select the supported quality/latency/memory trade-off and state residual uncertainty.

Do not introduce a competing shortcut, score, threshold, or task matrix.

## Foundation-portability boundary

Lessons 1 and 2 teach implementation-independent foundations. Their instructional spine, worked examples, exercises, quizzes, and takeaways must not rely on product, container, framework, backend, runtime, or production quantization-scheme names. Use neutral terms such as `model artifact`, `inference engine`, `numeric format`, and `retained runtime state`.

Lesson 2 may end with one short callout named **“The same mechanics, different implementations.”** Its only purpose is to distinguish category names and link to Lesson 3. It must not include format details, size/quality/speed claims, compatibility statements, or recommendations.

Architecture-specific mechanisms must always be labeled as such. A conventional KV cache is not universal to recurrent, state-space, linear-attention, or hybrid models.

## Terminology and evidence

Keep these categories distinct:

- checkpoint/model;
- artifact/container;
- quantization scheme and quantized target;
- inference engine/runtime;
- kernels/hardware.

GGUF is an artifact/container format, not a runtime. Never apply GGUF/llama.cpp labels to MLX artifacts. Use `Q8_0` only for the exact GGML/GGUF encoding; name MLX affine 8-bit with its group size explicitly. Version runtime-support and compatibility claims.

Label claims as one of:

- **Mechanism** — implementation-independent mathematics or architecture;
- **Implementation detail** — behavior pinned to a named upstream revision;
- **Empirical observation** — measured result with artifact/model scope and raw provenance;
- **Hypothesis** — a proposed explanation not established by the evidence.

Every numerical or implementation-specific table needs an adjacent caption naming the source revision and model/artifact scope. Do not use blogs, videos, or community posts as primary sources. Public pages must not expose provider/model identities, personal setup details, local paths, private prompts/patches, or raw trajectories. Use stable aliases in public case-study artifacts.

## Glossary-linking contract

Every technical term with an entry in `reference/glossary.html` must link its first instructional occurrence per lesson using a term-specific stable slug:

```html
<dt id="kv-cache">KV Cache</dt>
<a href="../reference/glossary.html#kv-cache" class="glossary-link">KV cache</a>
```

Letter headings are only for A–Z navigation. Never target them from instructional glossary links. Do not link the same target twice in one lesson, and do not put glossary links inside quiz options or code examples.

At the bottom of every lesson, add a `.terms-footer` whose target set exactly equals the set of inline `.glossary-link` targets—no missing, extra, or duplicate targets.

## Quizzes

- Use `assets/quiz.js`; do not duplicate or inline answer-checking logic.
- Group each question in `<fieldset class="quiz-question" data-quiz>` with a `<legend>`.
- Every button declares `type="button"`.
- Every question has exactly one `data-correct="true"` option.
- Keep answer options equal in word length as closely as possible.
- Give immediate explanatory feedback: why the selected answer is wrong and why the correct answer is right.
- Reveal correctness with icon/text plus color, disable options after submission, and provide an intentional reset path.
- Feedback uses `role="status"` or `aria-live="polite"`, receives focus after submission, and reset returns focus predictably.

## HTML, responsive, and accessibility contract

- Every non-redirect page has exactly one `<main>`.
- Put navigation in real `<nav>` landmarks. Lessons have matching top and bottom Previous/Home/Next navigation derived from `course.json`.
- Tables use `<caption>`, `<thead>`, `<tbody>`, and scoped `<th>` cells. Wrap wide tables in `.table-scroll` with a visible horizontal-scroll hint or provide a mobile-card alternative.
- Do not waive page-level overflow without a specific `data-overflow-explanation`.
- Keep keyboard focus visible with `:focus-visible`; do not communicate state by color alone.
- Verify 390 px presentation, quiz wrong-answer behavior, keyboard order, live announcements, and print output before release.

## Required checks

Run after every course change:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/audit_course.py
```

During the temporary five-lesson migration only, planned lessons may be ignored explicitly:

```bash
python3 scripts/audit_course.py --allow-planned-lessons
```

Before release, remove every `status: "planned"` value and run strict mode. Also run `git diff --check` and confirm the worktree contains no private benchmark data.
