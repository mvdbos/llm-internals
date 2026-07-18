# LLM Course Flow and Tone Revision Implementation Plan

> **For Hermes:** Execute the independent content tracks in parallel, then perform the structural integration and verification serially. Do not publish partial tracks.

**Goal:** Turn the current four-lesson course into a clearer learner journey—mechanics, memory, real-world format labels, then controlled evaluation—while retaining evidence discipline, glossary/a11y contracts, and the course’s concrete, approachable voice.

**Architecture:** Add a focused memory lesson between mechanics and format selection. Simplify the main paths of Lessons 2, 4, and 5; retain version-pinned format detail and advanced evaluation methodology in reference material rather than forcing them into every learner’s first pass. Preserve public paths that move by serving explicit compatibility redirects.

**Tech stack:** Dependency-free static HTML/CSS/JS; `course.json` manifest; `assets/quiz.js`; Python `unittest` and `scripts/audit_course.py` validation.

## Governing mission check

This plan is successful only if it serves this learner:

> **As an amateur, I want to run the best possible local model on my hardware. Once I have selected the model, I need practical guidance to choose the right quantization and other settings that materially affect whether it fits, runs well, and remains useful for my work. I want the supporting knowledge needed to make those choices, not expert training.**

For every proposed addition, rewrite, table, exercise, or reference move, the implementer must answer:

1. **Which practical decision does this help the learner make?** Examples: does it fit with headroom; which artifact/runtime combination is compatible; which candidates merit testing; how should quality, memory, and speed be compared?
2. **What is the minimum theory required for that decision?** Teach that in the main path; put implementation catalogues, source-level detail, and specialist protocols in reference/optional depth.
3. **What would an amateur do differently after this section?** If there is no clear answer, remove it from the main lesson or turn it into reference material.

“Best” is conditional—not a universal quant ranking. It means the best supported trade-off for the selected model, available hardware/headroom, compatible runtime, speed needs, and intended workload. Model selection itself is out of scope; this course covers the practical choices that follow it.

---

## Target learner sequence

| Published order | Target path | Learner question | Intended duration |
|---|---|---|---:|
| 1 | `lessons/0001-tensors-and-layers.html` | What are the numbers and transformations inside an LLM? | 5 min |
| 2 | `lessons/0002-how-quantization-works.html` | What does storing a weight with fewer bits actually do? | 8–10 min |
| 3 | `lessons/0003-model-memory-and-context.html` | Why can a model file that fits on disk still fail to fit at runtime? | 6–8 min |
| 4 | `lessons/0004-reading-quantization-formats.html` | What does a real quantization label identify—and what does it leave unknown? | 8–10 min |
| 5 | `lessons/0005-measuring-quantization-quality.html` | How can I fairly choose among candidates that fit? | 8–10 min |
| 6 | `lessons/0006-choosing-and-validating-a-quant.html` | Apply the method to controlled evidence. | Planned/evidence-gated |

### Non-negotiable teaching and publication constraints

- Keep the course voice **concrete and warm, but not cutesy**. Use “you” and practical examples. Avoid ELI5 labels, slogans, compliance vocabulary, and unexplained jumps.
- A main lesson should teach one job. Dense catalogues, protocol details, and version-pinned implementation facts belong in a reference page or clearly labeled optional material.
- Do not weaken the evidence gate for the planned capstone. The new lesson adds a published foundation; it does not fabricate Lesson 6 results or recommendations.
- Keep every first glossary occurrence linked with a term-specific fragment and `class="glossary-link"`; the terms footer target set must match exactly.
- Any moved currently-public page requires a compatibility redirect (`data-course-redirect="true"`), not a dead link. A redirect should name the supported replacement and preserve the old URL.
- Preserve the older `lessons/0003-quantization-in-practice.html` redirect; it remains a separate historical URL and must not become the new memory lesson.

---

# Phase 0 — Freeze the editorial contract (serial)

### Task 0.1: Record the baseline and create parallel work areas

**Objective:** Make independent changes reviewable and prevent contributors from editing the same file.

**Files:**
- Create: `docs/plans/2026-07-18-course-flow-revision-contract.md`
- Read only: `MISSION.md`, `course.json`, `index.html`, `AGENTS.md`, all `lessons/*.html`, `reference/*.html`, `resources.html`, `QA.md`

**Step 1: Record repository identity and clean state**

Run:
```bash
cd /Users/matthijs/Projects/llm-teach
git status --short
git rev-parse HEAD
```

Expected: clean worktree and a recorded baseline commit.

**Step 2: Write the editorial contract**

Put this mission gate at the top of the contract:

```markdown
## Mission gate (required for every track)
For each retained or newly introduced section, name:
1. the practical local-model decision it supports;
2. the minimum supporting knowledge it teaches; and
3. the learner action it enables.

A section that only demonstrates implementation expertise, enumerates formats, or rehearses evaluation protocol without changing a practical decision belongs in optional/reference material, not the main learner path.
```

Then create the contract with these acceptance statements:

```markdown
## Lesson 2 acceptance
- The first screen explains fewer representable values before formulas.
- It has one block-scale walkthrough and one metadata/group-size explanation.
- It does not repeat the group-size trade-off.
- It labels its numerical walkthrough as pedagogical.

## Lesson 3 acceptance
- A learner can distinguish file size, loaded weights, retained runtime state, temporary workspace, and peak memory.
- Conventional KV cache is explicitly architecture-specific.
- No runtime/product names are required to understand the lesson.

## Lesson 4 acceptance
- The learner classifies a real label by category before seeing a broad catalogue.
- The main lesson uses at most three representative format examples.
- Detailed version-pinned cataloguing remains in reference material.

## Lesson 5 acceptance
- It begins with a decision between two candidates, not an evidence taxonomy.
- It teaches matched tasks, task-quality-first metrics, repeated trials when relevant, and transparent failure handling.
- SWE-specific F2P/P2P/reward detail is optional/reference material, not a prerequisite for general learners.
```

**Step 3: Create separate branches/worktrees or isolated agent tasks**

Allocate non-overlapping ownership:

| Track | Owns | Must not edit |
|---|---|---|
| A | Current Lesson 2 only | manifest, index, navigation, other lessons |
| B | New memory-lesson draft only | manifest, index, existing lessons |
| C | Current Lesson 3 plus quantization-format reference only | manifest, index, Lessons 2/4 |
| D | Current Lesson 4 plus optional evaluation reference only | manifest, index, Lessons 2/3 |
| E | Integration after A–D are approved | all structural files; no independent prose redesign |

**Step 4: Commit the contract**

```bash
git add docs/plans/2026-07-18-course-flow-revision-contract.md
git commit -m "docs: define course flow revision contract"
```

---

# Phase 1 — Parallel editorial tracks

All tracks can begin from the same frozen baseline. Each output is a reviewable patch or branch. Do **not** merge, rename, or deploy yet.

## Track A — Lesson 2: keep the bridge, reduce the load

### Task A.1: Create a lesson-2 scope map

**Objective:** Identify duplicated teaching and separate core mechanics from optional detail.

**Files:**
- Modify: `lessons/0002-how-quantization-works.html`
- Create: `docs/reviews/2026-07-18-lesson-2-scope-map.md`

**Step 1: Mark the retained main path**

Retain this exact instructional progression:

1. Fewer bits → fewer available numeric levels.
2. A shared scale/offset makes low-bit storage usable.
3. Walk one weight through encode → stored code → reconstructed approximation.
4. Blocks trade metadata overhead against local fit.
5. Nominal bits are not the complete storage story.
6. Local reconstruction error is not proof of task quality.

**Step 2: Remove duplicate group-size instruction**

Keep the explanation following “Why blocks?” and replace the later repeat under “Metadata changes the true storage cost” with a forward-moving line such as:

```html
<p>The storage calculation below makes that same block-size trade-off measurable: it counts both low-bit codes and their shared metadata.</p>
```

Do not use the glossary link again in that later sentence; it has already been linked earlier in the lesson.

**Step 3: Move advanced mapping taxonomy out of the main path**

Reduce the main lesson’s “Compare mapping families” and detailed symmetric/affine equations to a short optional callout or a link to `reference/quantization-formats.html`. Retain the one concrete affine walkthrough; it is the primary worked example.

**Step 4: Tighten universal claims**

Replace claims like these with scoped wording:

| Current idea | Replacement direction |
|---|---|
| FP16 has “65,536 values in any range” | Explain that floating-point values are unevenly spaced; label the initial table as a simplified intuition, not a FP16 specification. |
| Scale and offset “stay in full precision” | “In this pedagogical example, scale and offset are stored in FP16.” |
| Models tolerate error because of dropout/weight decay | “Models can sometimes tolerate small local perturbations because their computations combine many values; tolerance depends on the model, encoding, and workload.” |
| Neighbouring weights “usually” share a range | “A smaller block can describe a local set of values more closely than one scale for an entire layer.” |

**Step 5: Keep the implementation boundary small**

Retain one short end callout titled **“The same mechanics, different implementations.”** It may distinguish category types and link forward, but must not become a product catalogue.

**Step 6: Update the quiz**

Keep three questions. They should assess:

- why metadata can make effective storage exceed nominal code width;
- why a low reconstruction error does not prove task quality;
- the group-size trade-off.

**Step 7: Validate the isolated patch**

```bash
python3 scripts/audit_course.py --allow-planned-lessons
node --check assets/quiz.js
git diff --check
```

Expected: all pass. Record the before/after main-section count in the scope map.

**Step 8: Commit track output**

```bash
git add lessons/0002-how-quantization-works.html docs/reviews/2026-07-18-lesson-2-scope-map.md
git commit -m "docs: focus quantization mechanics lesson"
```

---

## Track B — New memory lesson draft

### Task B.1: Author an implementation-independent memory lesson

**Objective:** Create the missing bridge between compression mechanics and format selection without restoring the overloaded old Lesson 1.

**Files:**
- Create: `lessons/0003-model-memory-and-context.html`
- Create: `docs/reviews/2026-07-18-memory-lesson-requirements.md`
- Read: `reference/glossary.html`, `reference/tensors-and-layers.html`, `assets/style.css`, `assets/quiz.js`

**Step 1: Write the single learner promise**

Use this opening direction:

> A smaller model file helps, but file size is not the amount of memory a running model needs. To decide whether a model will fit, separate what is loaded once from what grows while you use it.

**Step 2: Use four concrete memory buckets**

Teach only these buckets:

| Bucket | Plain-language explanation | What tends to change it |
|---|---|---|
| Artifact/file size | Bytes stored on disk | Encoding and included metadata |
| Loaded weights | Parameters held ready by the inference engine | Checkpoint/encoding and loading policy |
| Retained runtime state | Information intentionally kept as generation continues | Architecture, context length, batch, state format |
| Temporary workspace and overhead | Short-lived working memory plus engine allocation overhead | Engine, operations, batch, execution plan |

Use a concise formula:

```text
peak runtime memory
≈ loaded weights
+ retained runtime state
+ temporary workspace and overhead
```

Immediately say it is an estimate/measurement model, not a universal allocator formula.

**Step 3: Add one concrete scenario**

Use fictional, rounded values—not a real product or personal hardware:

```text
Same 4 GB artifact
Run A: short prompt → lower retained state → lower peak
Run B: long prompt → more retained state → higher peak
```

Make the conclusion explicit: the parameter file did not grow; the workload-dependent part did.

**Step 4: Explain context carefully**

Use “retained runtime state” as the primary term. Introduce KV cache only as a linked, architecture-specific example:

> In conventional cached attention, retained state is often a KV cache. Other architectures retain different state, so do not apply a KV-cache formula everywhere.

Do not teach head counts, cache formulas, grouped-query attention, or architecture taxonomies here. Those are reference material.

**Step 5: Add an actionable measurement checklist**

Teach learners to record:

- artifact size;
- loaded/idle memory under a named engine and loading policy;
- prompt length, generated length, and batch;
- peak memory during a representative run;
- remaining headroom.

**Step 6: Add three simple quiz questions**

Assess:

1. Why file size is not peak memory.
2. Why two runs with the same artifact can use different peak memory.
3. What must be recorded before claiming that a candidate fits.

Use `assets/quiz.js`, fieldsets, live feedback, reset controls, glossary links only outside options, and matching terms footer.

**Step 7: Create a requirements ledger**

The ledger must explicitly confirm:

- no framework/runtime/product names needed for the spine;
- no unexplained formula;
- conventional cache correctly scoped;
- first glossary targets and footer set match;
- one clear handoff to format reading.

**Step 8: Validate the draft page locally**

Run the course audit after temporarily adding only the draft page if the audit scans all HTML pages; otherwise use the audit after integration. Validate HTML structure manually: exactly one `<main>`, two matching nav landmarks, shared quiz script, three semantic tables/blocks as applicable.

**Step 9: Commit track output**

```bash
git add lessons/0003-model-memory-and-context.html docs/reviews/2026-07-18-memory-lesson-requirements.md
git commit -m "docs: draft model memory and context lesson"
```

---

## Track C — Current Lesson 3: formats as a practical classification skill

### Task C.1: Reduce Lesson 3 to three representative examples

**Objective:** Turn format reading from an encyclopedia into a skill: classify a label and identify what remains unknown.

**Files:**
- Modify: current `lessons/0003-reading-quantization-formats.html` (will be renamed only during integration)
- Modify: `reference/quantization-formats.html`
- Modify if required: `resources.html`, `RESOURCES.md`

**Step 1: Rewrite the main promise**

Open with a concrete situation:

> A filename such as `Q4_K_M` looks like an answer, but it is only a label. Before comparing two downloads, identify what category the label belongs to and what else you still need to know.

**Step 2: Teach only three representative examples in the main lesson**

Use exactly these examples:

| Example | Category | Does not establish |
|---|---|---|
| GGUF | Artifact/container | The encoding of every tensor or runtime performance |
| `Q4_K_M` | Model-file recipe | A universal four-bit representation |
| MLX affine 8-bit/group 64 | Quantization configuration | That it is GGML `Q8_0`, or that runtime state is eight-bit |

Use “one name, one category” as the lesson’s sole organizing phrase.

**Step 3: Move the catalogue to the reference page**

Keep the full version-pinned table and its source revisions in `reference/quantization-formats.html`, including:

- Q8_0/Q6_K/IQ labels;
- MLX affine, MXFP4, NVFP4;
- oMLX oQ recipes;
- runtime and kernel compatibility boundaries;
- effective-bpw empirical examples.

Every implementation-specific fact stays pinned and linked through the evidence ledger. Do not discard precision; relocate it.

**Step 4: Move the configuration exercise early**

Place an anonymized configuration-field exercise immediately after the three examples. The learner should infer category stacks from fields, not filenames.

**Step 5: Defer decision-procedure detail**

Replace the current long five-step section with one brief transition:

> Once you can name the artifact, recipe, target, and runtime, you can check whether it fits. The next lesson separates file size from peak runtime memory.

The full canonical procedure remains in `reference/quantization-decision-checklist.html` and can recur briefly after all its prerequisites have been taught.

**Step 6: Correct stale references**

Remove or rewrite “after Lesson 1’s memory accounting.” The final integrated lesson order makes memory the direct predecessor to format selection.

**Step 7: Keep only three quiz questions plus the configuration exercise**

Assess:

1. artifact vs runtime;
2. why similarly named eight-bit formats are not automatically interchangeable;
3. what successful loading leaves unknown.

**Step 8: Verify source and glossary contracts**

```bash
python3 scripts/audit_course.py --allow-planned-lessons
git diff --check
```

Audit every changed implementation claim against its pinned source before submitting the track.

**Step 9: Commit track output**

```bash
git add lessons/0003-reading-quantization-formats.html reference/quantization-formats.html resources.html RESOURCES.md
git commit -m "docs: focus format reading lesson on classification"
```

---

## Track D — Current Lesson 4: evaluation as an answer to a practical choice

### Task D.1: Restructure the evaluation lesson around the decision

**Objective:** Preserve rigorous evaluation requirements while giving general learners a natural, practical entry point.

**Files:**
- Modify: current `lessons/0004-measuring-quantization-quality.html` (will be renamed only during integration)
- Optional create/modify: `reference/evaluation-protocol.html` or existing `case-study/protocol.md` only if it can be linked as a rendered static HTML page

**Step 1: Replace the opening with a decision scenario**

Use this direction:

> Suppose two artifacts both fit in memory. One is smaller; the other may preserve more quality. A suffix cannot settle the choice. Compare them on the workload you actually care about, with everything else held steady.

**Step 2: Teach the four-question main path**

Organize the main lesson around:

1. **What stays the same?** Checkpoint, tokenizer, task, engine settings, prompts/tools, and environment.
2. **What changes?** Exact declared quantization condition.
3. **What do you measure?** Task quality first, then memory and speed.
4. **How do you compare fairly?** Same task under both conditions; repeats if stochastic; failures reported rather than silently removed.

**Step 3: Keep evidence categories as a short guardrail**

Retain mechanism / implementation detail / observation / hypothesis, but place it after the decision scenario and label it “How to describe your result honestly.” Keep one concise example of each.

**Step 4: Make the main metrics general**

Keep a compact table mapping workload types to direct quality signals:

| Workload | Primary quality signal |
|---|---|
| Coding | Verified tests or task-specific checks |
| Classification | Accuracy/F1 or equivalent task measure |
| Summarization | Factuality/content criteria |
| Chat or writing | Defined rubric or blinded preference |
| Agentic task | Externally verified completion |

Move F2P/P2P/reward definitions to an optional SWE-agent example or a reference page. Do not require them to understand the core lesson.

**Step 5: Generalize project-remediation prose**

Replace the retrospective anti-example with a universal warning about unmatched tasks, architectures, repetitions, and completion definitions. Do not narrate prior project audit history in the main instructional path.

**Step 6: Preserve the key anti-example and paired-design practice**

Retain a short pooled-mean confounding example and the exercise that asks the learner to reject an invalid causal comparison. It is the best concrete demonstration of why pairing matters.

**Step 7: End with an actionable mini-protocol**

End with a learner-ready template:

```text
Candidate A: [artifact + declared encoding]
Candidate B: [artifact + declared encoding]
Held constant: [checkpoint, task, engine settings, prompt/tools]
Run: each task under both candidates [and repeats if stochastic]
Record: task quality, peak memory, latency, failures
Conclusion: scoped to this model, stack, workload, and settings
```

**Step 8: Keep the evidence-gated capstone boundary**

Link to the deferred capstone and state that this lesson teaches how to prepare a comparison, not a result-dependent recommendation.

**Step 9: Validate and commit**

```bash
python3 scripts/audit_course.py --allow-planned-lessons
git diff --check
git add lessons/0004-measuring-quantization-quality.html
git commit -m "docs: make evaluation lesson decision-led"
```

---

# Phase 2 — Editorial review gates (parallel)

### Task 2.1: Tone and learner-flow review

**Objective:** Verify that each track is concrete, adult, and accessible rather than bureaucratic or cutesy.

**Files:**
- Read: Track A–D changed files
- Create: `docs/reviews/2026-07-18-course-flow-tone-review.md`

Review against these questions:

- Does each lesson open with a learner problem rather than a definition or policy?
- Is every analogy doing explanatory work rather than adding cheerfulness?
- Are implementation details deferred until the learner has a reason to need them?
- Does a learner know why the next lesson follows from the current one?
- Are there unexplained terms, equations, or design choices?

Classify issues as blocker / important / polish. No changes during this review.

### Task 2.2: Technical and evidence review

**Objective:** Protect the audit remediation gains while simplifying presentation.

**Files:**
- Read: Track A–D changed files, `reference/quantization-formats.html`, `resources.html`, `course.json`
- Create: `docs/reviews/2026-07-18-course-flow-evidence-review.md`

Review for:

- implementation facts still pinned to source revisions;
- correct distinctions between artifact, encoding, recipe, runtime, backend, and kernel;
- no universal causal claim based on a toy example or observation;
- architecture-specific cache claims clearly scoped;
- quantitative tables accurately captioned and sourced;
- no personal details, local paths, private artifacts, or unvalidated experiment results.

### Task 2.3: Resolve blockers before integration

**Objective:** Accept only tracks that pass both reviews.

For each track, record one of:

- **Accepted** — ready for integration;
- **Revise** — list exact section and required fix;
- **Reject** — explain which contract constraint failed.

Do not start renaming pages or modifying `course.json` until all accepted tracks are available.

---

# Phase 3 — Structural integration (serial; one owner)

### Task 3.1: Install the new ordered lesson paths

**Objective:** Insert memory before format selection without breaking existing URLs.

**Files:**
- Create: `lessons/0003-model-memory-and-context.html` (accepted Track B draft)
- Rename: `lessons/0003-reading-quantization-formats.html` → `lessons/0004-reading-quantization-formats.html`
- Rename: `lessons/0004-measuring-quantization-quality.html` → `lessons/0005-measuring-quantization-quality.html`
- Update planned manifest path: `lessons/0005-choosing-and-validating-a-quant.html` → `lessons/0006-choosing-and-validating-a-quant.html`
- Create redirect: `lessons/0003-reading-quantization-formats.html`
- Create redirect: `lessons/0004-measuring-quantization-quality.html`

**Step 1: Rename the two published lesson files and update internal paths.**

The old path files must become compatibility redirects rather than duplicate lessons. Each redirect must include:

```html
<meta name="robots" content="noindex">
<title>Moved lesson — Reading Quantization Formats</title>
<body data-course-redirect="true">
  <p>This lesson moved to <a href="0004-reading-quantization-formats.html">Lesson 4: Reading Quantization Formats</a>.</p>
</body>
```

Use the analogous title/target for the former measuring-quality path.

**Step 2: Handle the planned lesson path deliberately.**

If no published `0005-choosing-and-validating-a-quant.html` file exists, update only its `course.json` path to `0006-choosing-and-validating-a-quant.html`. If a public stub exists, replace it with a redirect/tombstone appropriate to its actual prior publication state.

**Step 3: Do not alter the older practical-guide redirect.**

`lessons/0003-quantization-in-practice.html` continues to redirect to the now-supported format/decision destination determined during integration. Update its target text only if needed; retain `data-course-redirect="true"`.

### Task 3.2: Update the manifest, course map, and all navigation

**Objective:** Make every visible course surface agree on title, number, path, status, and duration.

**Files:**
- Modify: `course.json`
- Modify: `index.html`
- Modify: `mission.html` only if it promises a stale sequence
- Modify: all published `lessons/0001-*.html` through `lessons/0005-*.html`
- Modify: `AGENTS.md`
- Modify: `QA.md`
- Modify: relevant documents in `docs/plans/` or `docs/reviews/` that describe the current public sequence

**Step 1: Set the new manifest**

Use these lesson entries:

```json
{
  "number": 3,
  "path": "lessons/0003-model-memory-and-context.html",
  "title": "Will It Fit? Model Memory and Context",
  "minutes": 7
},
{
  "number": 4,
  "path": "lessons/0004-reading-quantization-formats.html",
  "title": "Reading Quantization Formats",
  "minutes": 9
},
{
  "number": 5,
  "path": "lessons/0005-measuring-quantization-quality.html",
  "title": "Measuring Quantization Quality",
  "minutes": 9
},
{
  "number": 6,
  "path": "lessons/0006-choosing-and-validating-a-quant.html",
  "title": "Choosing and Validating a Quant",
  "minutes": 12,
  "status": "planned",
  "gate": "deferred-pending-controlled-evidence"
}
```

Adjust Lesson 2 duration to the final measured scope; do not leave “15 min” if the simplified lesson is materially shorter.

**Step 2: Update top and bottom navigation symmetrically**

Required published chain:

```text
Lesson 1 → Lesson 2 → Lesson 3: Memory → Lesson 4: Formats → Lesson 5: Evaluation
```

Published Lesson 5 must not link “Next” to planned Lesson 6. The index may show Lesson 6 as deferred but must not present it as a completed lesson.

**Step 3: Update `index.html` descriptions**

Use concise learner-facing cards, for example:

- **Lesson 3:** “Why a model file that fits on disk can still need more memory at runtime. File size, context, peak memory, and headroom. ~7 min.”
- **Lesson 4:** “Read real quantization labels without mistaking a file format, recipe, encoding, and runtime for the same thing. ~9 min.”
- **Lesson 5:** “Compare candidates fairly on the workload that matters: task quality first, then memory and speed. ~9 min.”

**Step 4: Update operational documentation**

Revise `AGENTS.md` and `QA.md` from “four published lessons and one planned lesson” to “five published lessons and one planned lesson.” Preserve the migration-mode and evidence-gate rules.

### Task 3.3: Reconcile references and links

**Objective:** Ensure lesson handoffs, reference links, redirects, and glossary contracts all point to the integrated sequence.

**Files:**
- Modify as needed: `reference/quantization-decision-checklist.html`, `reference/tensors-and-layers.html`, `reference/quantization-formats.html`, `resources.html`, `RESOURCES.md`

**Step 1: Update lesson references in copy**

- Lesson 2 must point to the memory lesson as next.
- Memory lesson must point to the format lesson.
- Format lesson must point to evaluation.
- Evaluation must link to the deferred capstone publication status, not promise a current next lesson.

**Step 2: Audit local fragments and legacy paths**

Run:

```bash
python3 scripts/audit_course.py --allow-planned-lessons
```

Expected: no missing local files or fragments; redirects exempt from main-landmark checks.

**Step 3: Commit integration separately**

```bash
git add course.json index.html mission.html AGENTS.md QA.md lessons reference resources.html RESOURCES.md docs
git commit -m "docs: add memory lesson and reorder learner path"
```

---

# Phase 4 — End-to-end verification (serial)

### Task 4.1: Run all mechanical checks

**Objective:** Verify course contracts after all content and path changes.

Run from repository root:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/audit_course.py --allow-planned-lessons
python3 -m py_compile scripts/audit_course.py scripts/analyze_case_study.py
node --check assets/quiz.js
git diff --check
git grep -l '/Users/\|/home/\|/Users/.*Projects/\|Mac Studio\|MacBook\|prefers\|personal\|local artifact\|private model' -- '*.html' '*.md' '*.json' '*.py' '*.js' '*.css'
```

Expected:

- unit tests pass;
- audit exits 0;
- Python/JS checks exit 0;
- no whitespace errors;
- privacy scan has no unintended public findings.

### Task 4.2: Verify learner flow manually at narrow and desktop widths

**Objective:** Test the actual learning path rather than only static contracts.

**Step 1: Read each lesson in sequence**

For Lessons 1–5, answer in a review note:

- What question did this lesson answer?
- What prior lesson knowledge did it use?
- What specific question does it make the next lesson feel necessary to answer?

Any lesson that cannot answer all three is returned to its owning editorial track.

**Step 2: Verify at 390 px and desktop width**

Check:

- every table has intentional horizontal handling or remains readable;
- no page-level horizontal overflow;
- visible focus remains clear;
- navigation order is logical;
- redirects explain their destination.

**Step 3: Exercise every quiz with wrong and correct answers**

For every quiz:

- choose a wrong option;
- verify correct answer is revealed and explanation is meaningful;
- verify live feedback receives focus/announces;
- activate “Try again”; 
- choose the correct option;
- verify reset behavior is intentional.

### Task 4.3: Review deployment diff and publish

**Objective:** Deploy only the integrated, verified course.

**Step 1: Review the release diff**

```bash
git status --short
git diff HEAD~1..HEAD --stat
git log --oneline -5
```

Expected: only approved course content, reference, manifest, documentation, and redirect changes.

**Step 2: Commit any verification-only fixes separately**

```bash
git add <verified-fix-files>
git commit -m "fix: polish reordered course flow"
```

**Step 3: Push and verify GitHub Pages**

```bash
git push origin main
```

Then inspect the live pages:

- home/index;
- all five published lessons;
- both moved old URLs;
- glossary fragments from each changed lesson.

---

## Dependency and parallelism map

```text
Phase 0 contract/freeze
        │
        ├── Track A: Lesson 2 simplification ───────┐
        ├── Track B: new memory lesson draft ───────┤
        ├── Track C: format lesson + reference ─────┼──> Phase 2 parallel reviews
        └── Track D: evaluation lesson ─────────────┘
                                                       │
                                                       ▼
                                        Phase 3 serial integration / renumbering
                                                       │
                                                       ▼
                                         Phase 4 serial QA, deploy, live check
```

**Safe parallel units:** Tracks A–D and the two Phase 2 reviews.

**Must remain serial:** structural renaming/redirects, `course.json`, index/navigation changes, `AGENTS.md`/`QA.md` publication-state changes, final audit, deployment.

---

## Risks and mitigation

| Risk | Mitigation |
|---|---|
| Adding a memory lesson breaks public URLs or course navigation | Preserve moved page paths as explicit `data-course-redirect` pages; integrate paths only after all content tracks pass review. |
| Parallel prose rewrites drift in voice | Freeze the editorial contract; run a dedicated tone/flow review before integration. |
| Simplification accidentally deletes evidence discipline | Keep version-pinned catalogue and protocol content in references; run a technical/evidence review. |
| New lesson reintroduces old Lesson 1 overload | Restrict it to four memory buckets and one workload scenario; no cache formulas or architecture taxonomy. |
| Lesson 2 becomes inaccurate while restoring baseline intuitions | Label simple representations as pedagogical; scope FP16/metadata/tolerance claims; retain exact technical detail only where sourced. |
| Existing audit assumes four published lessons | Update `AGENTS.md`, `QA.md`, and any actual test/manifest assumptions during serial integration; run full tests after the manifest changes. |
| Planned capstone accidentally becomes navigable | Keep Lesson 6 `status: "planned"`; do not add a Lesson 5 next link; run audit only with explicit planned-lessons flag. |

## Completion criteria

- Five published lessons and one clearly deferred capstone are represented consistently in `course.json`, index, page titles, progress labels, and navigation.
- A learner can travel from “weights are numbers” to “I can describe, size, shortlist, and fairly compare candidates” without unexplained conceptual leaps.
- Lesson 2 does not duplicate the group-size trade-off or overclaim from a toy example.
- Lesson 3 explains runtime memory without framework names or universal KV-cache assumptions.
- Lesson 4 teaches label classification before showing detailed catalogues; detailed version-pinned facts remain in reference material.
- Lesson 5 starts with a real decision and keeps evaluation methodology proportional to the learner’s task.
- All automated checks, glossary contracts, responsive/keyboard/quiz checks, privacy scans, redirects, and live pages pass.
