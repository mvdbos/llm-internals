# Practical Local-Model Course Revision Implementation Plan

> **For Hermes:** Execute the five independent authoring/audit tracks in parallel Git worktrees. Integrate them on a dedicated branch, then run two parallel reviews followed by serial fixes, structural updates, validation, and deployment. Do not publish a partial course.

**Goal:** Produce a practical first-version course that helps an amateur choose and validate the right quantization and related local-runtime settings for a model they have already selected.

**Architecture:** Keep the main path short and decision-led: foundations → quantization mechanics → memory/fit → format/runtime identification → practical choice and validation. Move exhaustive implementation catalogues and specialist evaluation protocol into reference pages. Publish the general decision method now; defer only the result-bearing controlled case study.

**Tech stack:** Dependency-free static HTML/CSS/JS; `course.json`; shared `assets/style.css` and `assets/quiz.js`; Python `unittest`; `scripts/audit_course.py`.

---

## 1. Governing mission

The course serves this learner:

> **As an amateur, I want to run the best possible local model on my hardware. Once I have selected the model, I need practical guidance to choose the right quantization and other settings that materially affect whether it fits, runs well, and remains useful for my work. I want the supporting knowledge needed to make those choices, not expert training.**

Every main-path section must answer all three questions:

1. **Which practical local-model decision does this support?**
2. **What is the minimum theory needed for that decision?**
3. **What can the learner do differently afterward?**

If a section only demonstrates implementation expertise, enumerates formats, or rehearses specialist methodology, move it to optional/reference material.

“Best” is conditional on the selected checkpoint, hardware capacity and headroom, compatible runtime, speed needs, and intended workload. The course must not invent a universal quant ranking.

### Scope boundary

| In scope | Out of scope unless directly required for a choice |
|---|---|
| Choosing quantization after selecting a base model | Choosing the base checkpoint/model |
| Identifying artifact, quantized target, recipe, runtime, backend, and compatibility | Exhaustive inference-engine configuration |
| File size, loaded memory, retained state, peak memory, context, and headroom | Deep architecture taxonomy and cache derivations |
| Speed and memory on the intended hardware/runtime stack | Serving-fleet and throughput optimization |
| Workload-appropriate quality checks | General LLM evaluation theory |
| Settings that materially change a candidate comparison | Comprehensive prompting or sampling instruction |

### Teaching order versus decision order

The teaching sequence introduces implementation-independent memory concepts before the real-world format taxonomy. The practical decision checklist still runs in this order:

1. Identify the concrete checkpoint, artifact, quantized target, recipe, runtime/backend, and hardware.
2. Calculate or measure that candidate’s memory requirement and headroom.
3. Shortlist compatible candidates that fit.
4. Validate quality and speed in proportion to the stakes.
5. Choose the supported trade-off and state uncertainty.

Agents must not treat the learner sequence and the execution checklist as competing procedures.

---

## 2. Target first-version course

| Lesson | Final path | Practical learner question | Target duration |
|---:|---|---|---:|
| 1 | `lessons/0001-tensors-and-layers.html` | What are the weight numbers and transformations that quantization changes? | 5 min |
| 2 | `lessons/0002-how-quantization-works.html` | What does storing weights with fewer bits do? | 8–10 min |
| 3 | `lessons/0003-model-memory-and-context.html` | Will this candidate actually fit with useful context and headroom? | 6–8 min |
| 4 | `lessons/0004-reading-quantization-formats.html` | What does this label identify, and is the artifact/runtime combination compatible? | 8–10 min |
| 5 | `lessons/0005-choosing-and-validating-a-quant.html` | Which compatible candidate should I use, and how much validation is enough? | 9–11 min |
| 6 | `lessons/0006-controlled-quantization-case-study.html` | What does the preregistered controlled comparison show? | Planned/evidence-gated |

### Publication boundary

- Lessons 1–5 provide a complete practical method without requiring unpublished results.
- Lesson 6 is a controlled case study. Its results and result-dependent recommendation remain unpublished until the evidence gate passes.
- Lesson 5 may teach how to choose; it must not claim that a particular quant universally wins.
- This is the first public version. **Do not create redirects, compatibility pages, or legacy routes.** Remove obsolete pre-release lesson pages and update all internal links directly.

### Tone and lesson constraints

- Concrete and warm, but not cutesy.
- Use “you,” practical scenarios, and plain language.
- Do not use ELI5 labels, institutional compliance prose, or unexplained technical jumps.
- Each lesson teaches one job and ends with a practical next action.
- Main lessons contain only decision-relevant detail; references retain precision and optional depth.
- Every first glossary occurrence uses a term-specific fragment and `class="glossary-link"`.
- Inline glossary targets and the terms footer must match exactly.
- Quizzes use `assets/quiz.js`, semantic fieldsets, explanatory feedback, and an intentional retry path.

---

# Phase 0 — Freeze and prepare parallel worktrees

## Task 0.1: Record the baseline and run the current checks

**Objective:** Start all tracks from the same known-good commit.

**Files:** Read only.

**Step 1: Start at the repository root**

```bash
export COURSE_REPO="$(pwd)"
export BASE="$(git rev-parse HEAD)"
git status --short
git rev-parse HEAD
```

Expected: clean worktree. If not clean, stop and resolve ownership before continuing.

**Step 2: Run baseline verification**

```bash
python3 -m unittest discover -s tests -v
python3 scripts/audit_course.py --allow-planned-lessons
python3 -m py_compile scripts/audit_course.py scripts/analyze_case_study.py
node --check assets/quiz.js
git diff --check
```

Expected: every command exits 0.

## Task 0.2: Create exact parallel branches and worktrees

**Objective:** Give each track exclusive file ownership.

```bash
export WORKTREE_ROOT="$(dirname "$COURSE_REPO")/llm-course-revision-worktrees"
mkdir -p "$WORKTREE_ROOT"

git worktree add "$WORKTREE_ROOT/track-a" -b course/lesson-2 "$BASE"
git worktree add "$WORKTREE_ROOT/track-b" -b course/memory-lesson "$BASE"
git worktree add "$WORKTREE_ROOT/track-c" -b course/format-lesson "$BASE"
git worktree add "$WORKTREE_ROOT/track-d" -b course/choice-lesson "$BASE"
git worktree add "$WORKTREE_ROOT/track-e" -b course/mission-audit "$BASE"
```

### Ownership

| Track | Exclusive write ownership |
|---|---|
| A | `lessons/0002-how-quantization-works.html`, `docs/reviews/2026-07-18-lesson-2-scope-map.md` |
| B | `lessons/0003-model-memory-and-context.html`, `docs/reviews/2026-07-18-memory-source-ledger.md` |
| C | `lessons/0003-reading-quantization-formats.html`, `reference/quantization-formats.html`, `resources.html`, `RESOURCES.md`, track-C review note |
| D | `lessons/0004-measuring-quantization-quality.html`, new `reference/evaluation-protocol.html`, track-D review note |
| E | Audit-only report `docs/reviews/2026-07-18-mission-to-course-map.md` |

No authoring track may edit `course.json`, `index.html`, `AGENTS.md`, `QA.md`, navigation in other lessons, learning records, filenames, or publication status. Those are integration-owned.

---

# Phase 1 — Parallel Track A: Focus Lesson 2

Work in `$WORKTREE_ROOT/track-a`.

## Task A1: Write the lesson scope map

**Objective:** Lock the one learner win before editing prose.

**Create:** `docs/reviews/2026-07-18-lesson-2-scope-map.md`

Record:

- Practical decision: understand the memory/approximation trade-off before comparing quants.
- Minimum theory: fewer levels, shared scale/offset, one encode/decode example, block metadata, local error versus task quality.
- Learner action: explain why nominal four-bit storage is approximate and why a label alone cannot guarantee acceptable quality.
- Material to move out: mapping-family catalogue, duplicate parameterization formulas, full evaluation taxonomy.

Commit:

```bash
git add docs/reviews/2026-07-18-lesson-2-scope-map.md
git commit -m "docs: define lesson 2 practical scope"
```

## Task A2: Correct and scope the opening model

**Modify:** `lessons/0002-how-quantization-works.html`

- Keep the fewer-bits intuition before formulas.
- Do not claim FP16 supplies 65,536 evenly spaced values “in any range.” Label the comparison as simplified and state that floating-point values are unevenly spaced.
- Replace production-looking `Q8`, `Q4`, and `Q2` in the conceptual table with “8-bit codes,” “4-bit codes,” and “2-bit codes” unless a concrete implementation is explicitly identified.
- State: “In this pedagogical example, scale and offset are stored in FP16.”
- Keep one single-weight encode → store → reconstruct → compare walkthrough.

Commit:

```bash
git add lessons/0002-how-quantization-works.html
git commit -m "docs: scope lesson 2 numeric intuition"
```

## Task A3: Remove duplicate and advanced main-path material

**Modify:** `lessons/0002-how-quantization-works.html`

- Keep the group-size trade-off once, following “Why blocks?”
- Replace its later duplicate with a sentence that advances to total storage accounting.
- Move the mapping-family catalogue and duplicate symmetric/affine derivations to `reference/quantization-formats.html` by leaving a concise link/optional callout. Track C owns the reference edit; Track A only removes or compresses the lesson material and records exactly what Track C must preserve in the scope map.
- Retain one concrete affine round trip.
- Replace the dropout/weight-decay causal claim with scoped language: local perturbations may be tolerated, but tolerance depends on model, encoding, and workload.
- Qualify claims about neighbouring weights and local ranges.

Commit:

```bash
git add lessons/0002-how-quantization-works.html docs/reviews/2026-07-18-lesson-2-scope-map.md
git commit -m "docs: remove duplicate and advanced lesson 2 material"
```

## Task A4: Simplify the handoff and quiz

**Modify:** `lessons/0002-how-quantization-works.html`

End with this practical takeaway, adapted to the page voice:

> Quantization replaces exact weight values with approximations. Blocks make that practical by sharing a little metadata across many low-bit values. Next, separate model-file size from the memory a running model actually needs.

Keep three quiz questions assessing:

1. why metadata raises effective storage above nominal code width;
2. why low reconstruction error does not prove workload quality;
3. the group-size trade-off.

Do not introduce product names in the instructional spine. Keep one short implementation-boundary callout that points forward without cataloguing products.

Commit:

```bash
git add lessons/0002-how-quantization-works.html
git commit -m "docs: simplify lesson 2 takeaway and quiz"
```

## Task A5: Validate Track A

```bash
python3 scripts/audit_course.py --allow-planned-lessons
node --check assets/quiz.js
git diff --check
```

Expected: exits 0. Record the final section count and estimated reading time in the scope map, then amend only the last track commit if needed.

---

# Phase 1 — Parallel Track B: Add the Memory and Context Lesson

Work in `$WORKTREE_ROOT/track-b`.

## Task B1: Build the memory source ledger

**Objective:** Ground the new lesson in high-trust sources rather than parametric knowledge.

**Read:**

- `reference/tensors-and-layers.html`
- `reference/glossary.html`
- `resources.html`
- `RESOURCES.md`
- the canonical architecture/runtime sources already referenced by the course

**Create:** `docs/reviews/2026-07-18-memory-source-ledger.md`

For each claim, record its source and scope:

| Claim | Required scope |
|---|---|
| Artifact size differs from loaded/peak memory | General accounting boundary, not one engine |
| Retained state can grow with workload/context | Architecture-specific caveat included |
| Conventional KV cache is one retained-state example | Explicitly not universal |
| Peak memory includes working allocations and overhead | Measurement boundary stated |

If an adequate high-trust source is absent, record the exact source to add during integration; do not edit shared resource files from Track B.

Commit:

```bash
git add docs/reviews/2026-07-18-memory-source-ledger.md
git commit -m "docs: establish memory lesson evidence scope"
```

## Task B2: Create the lesson skeleton and memory buckets

**Create:** `lessons/0003-model-memory-and-context.html`

Use provisional navigation while this page is outside `course.json`:

- Previous: `0002-how-quantization-works.html`
- Next: `0003-reading-quantization-formats.html`

Open with:

> A smaller model file helps, but file size is not the amount of memory a running model needs. To decide whether a candidate will fit, separate what is loaded once from what grows while you use it.

Teach only four buckets:

1. artifact/file size;
2. loaded weights;
3. retained runtime state;
4. temporary workspace and runtime overhead.

Use this accounting model and label it as an estimate, not a universal allocator formula:

```text
peak runtime memory
≈ loaded weights
+ retained runtime state
+ temporary workspace and overhead
```

Commit:

```bash
git add lessons/0003-model-memory-and-context.html
git commit -m "docs: add model memory lesson foundation"
```

## Task B3: Add the practical scenario and fit checklist

**Modify:** `lessons/0003-model-memory-and-context.html`

Use one fictional scenario:

```text
Same 4 GB artifact
Short-context run → lower workload-dependent memory → lower peak
Long-context run → higher workload-dependent memory → higher peak
```

Explain that the file and loaded parameters did not grow; the workload-dependent allocation changed.

Introduce KV cache only as an architecture-specific example:

> In conventional cached attention, retained state is often a KV cache. Other architectures retain different state, so do not apply a KV-cache formula everywhere.

Do not teach head counts, GQA/MQA, cache derivations, or an architecture taxonomy.

End with a checklist that records:

- artifact size;
- loaded/idle memory under a named engine and loading policy;
- prompt length, generated length, and batch;
- peak memory during a representative run;
- remaining headroom.

Commit:

```bash
git add lessons/0003-model-memory-and-context.html
git commit -m "docs: add practical fit and headroom workflow"
```

## Task B4: Add the quiz, glossary links, citations, and handoff

**Modify:** `lessons/0003-model-memory-and-context.html`

Add three quiz questions:

1. why file size is not peak memory;
2. why the same artifact can have different peaks;
3. what must be recorded before claiming a candidate fits.

Add first-occurrence glossary links and an exactly matching terms footer. Link relevant claims to the existing evidence ledger/reference. End by explaining that the next lesson identifies the concrete artifact, quantization recipe, and runtime whose fit must be checked.

Commit:

```bash
git add lessons/0003-model-memory-and-context.html
git commit -m "docs: complete memory lesson practice and references"
```

## Task B5: Validate Track B

The audit scans every lesson HTML page even if it is not yet in `course.json`.

```bash
python3 scripts/audit_course.py --allow-planned-lessons
node --check assets/quiz.js
git diff --check
```

Expected: exits 0. The draft must pass general HTML, local-link, glossary, and quiz contracts; manifest-order validation occurs after integration.

---

# Phase 1 — Parallel Track C: Make Format Reading a Practical Skill

Work in `$WORKTREE_ROOT/track-c`.

## Task C1: Write the lesson/reference allocation map

**Create:** `docs/reviews/2026-07-18-format-lesson-allocation.md`

Record:

- Practical decision: identify what a label describes, establish compatibility inputs, and avoid false equivalences.
- Main lesson: three representative examples and one configuration-reading exercise.
- Reference: complete version-pinned catalogue, source revisions, effective-bpw examples, runtime/kernel boundaries.
- Learner action: produce a complete candidate description rather than trusting a filename.

Commit:

```bash
git add docs/reviews/2026-07-18-format-lesson-allocation.md
git commit -m "docs: define format lesson and reference boundary"
```

## Task C2: Rebuild the opening around three examples

**Modify:** `lessons/0003-reading-quantization-formats.html`

Open with:

> A filename such as `Q4_K_M` looks like an answer, but it is only a label. Before comparing downloads, identify what category each name belongs to and what information is still missing.

Use only these examples in the main teaching table:

| Example | Category | Does not establish |
|---|---|---|
| GGUF | Artifact/container | Encoding of every tensor or runtime performance |
| `Q4_K_M` | Model-file recipe | One universal four-bit tensor representation |
| MLX affine 8-bit/group 64 | Quantization configuration | GGML `Q8_0`, runtime-state precision, or universal compatibility |

Use “one name, one category” as the organizing phrase.

Commit:

```bash
git add lessons/0003-reading-quantization-formats.html
git commit -m "docs: teach format labels through three categories"
```

## Task C3: Move the configuration-reading exercise early

**Modify:** `lessons/0003-reading-quantization-formats.html`

Place the anonymized configuration exercise immediately after the three examples. Require the learner to identify:

- artifact/framework category;
- quantized target;
- encoding/recipe and grouping;
- runtime identity;
- what remains unproven about fit, speed, and quality.

Keep the exercise generalizable and free of personal paths, private model IDs, or unpublished results.

Commit:

```bash
git add lessons/0003-reading-quantization-formats.html
git commit -m "docs: move format inspection practice into main flow"
```

## Task C4: Move catalogue detail to the reference

**Modify:**

- `lessons/0003-reading-quantization-formats.html`
- `reference/quantization-formats.html`
- `resources.html`
- `RESOURCES.md`

The main lesson must not require memorizing Q6_K, IQ variants, MXFP4, NVFP4, oQ recipes, vLLM, or SGLang.

Preserve that material in the reference with its pinned source revisions and exact scope. Also preserve advanced mapping families removed by Track A when they remain useful and sourced.

Do not invent or loosen implementation claims. Update source entries only when needed to preserve adjacent evidence.

Commit:

```bash
git add lessons/0003-reading-quantization-formats.html reference/quantization-formats.html resources.html RESOURCES.md
git commit -m "docs: move format catalogue into reference material"
```

## Task C5: Simplify the checklist, handoff, and quiz

**Modify:** `lessons/0003-reading-quantization-formats.html`

Replace the repeated five-step procedure with one practical output template:

```text
checkpoint
+ artifact/container
+ quantized target
+ encoding/recipe and grouping
+ runtime/backend version
+ intended hardware
```

Acknowledge the memory lesson as prior knowledge. Point forward to choosing among compatible candidates:

> The memory lesson established what to measure for fit. Now that you can describe the candidate and runtime precisely, the next lesson shows how much validation is appropriate before choosing.

Keep three quiz questions plus the configuration exercise:

1. artifact versus runtime;
2. why similarly named eight-bit formats are not interchangeable;
3. what successful loading leaves unknown.

Commit:

```bash
git add lessons/0003-reading-quantization-formats.html
git commit -m "docs: simplify format lesson decision output"
```

## Task C6: Validate Track C

```bash
python3 scripts/audit_course.py --allow-planned-lessons
node --check assets/quiz.js
git diff --check
```

Expected: exits 0. Verify every changed implementation claim against the pinned source before marking the branch ready.

---

# Phase 1 — Parallel Track D: Publish a Practical Choice and Validation Lesson

Work in `$WORKTREE_ROOT/track-d`.

## Task D1: Allocate practical versus specialist evaluation content

**Create:** `docs/reviews/2026-07-18-choice-lesson-allocation.md`

Record:

- Practical decision: choose among compatible candidates that fit.
- Main lesson: hard constraints, shortlist, proportional validation, task quality first, memory/speed second, transparent failures.
- Reference: detailed preregistration, missing-data rules, F2P/P2P/reward definitions, paired statistical reporting, causal-language taxonomy.
- Deferred Lesson 6: only the controlled case-study execution and result.

Commit:

```bash
git add docs/reviews/2026-07-18-choice-lesson-allocation.md
git commit -m "docs: define practical choice versus protocol scope"
```

## Task D2: Create the advanced evaluation reference

**Create:** `reference/evaluation-protocol.html`

Move and preserve advanced, generally useful material from the current lesson:

- mechanism / implementation detail / observation / hypothesis;
- detailed matched-condition fields;
- preregistered missing-data and exclusion rules;
- paired/repeated analysis guidance;
- pooled-mean confounding anti-example;
- optional SWE-agent F2P/P2P/reward example.

Generalize retrospective project-remediation prose. Do not describe private or unpublished historical outcomes.

The reference must use shared CSS, exactly one `<main>`, semantic tables, glossary links and matching footer, and high-trust citations.

Commit:

```bash
git add reference/evaluation-protocol.html
git commit -m "docs: add optional controlled evaluation reference"
```

## Task D3: Rebuild the lesson opening and practical decision path

**Modify:** `lessons/0004-measuring-quantization-quality.html`

Open with:

> Suppose two candidates both work with your runtime and fit in memory. One is smaller or faster; the other may preserve more quality. A suffix cannot settle the choice. Use the amount of validation that matches how important the decision is.

Teach this main path:

1. Apply hard constraints: compatibility, fit, and required context/headroom.
2. Shortlist two or three candidates rather than every available quant.
3. Hold checkpoint, task, runtime settings, prompts/tools, and environment steady.
4. Measure task quality first; interpret memory and speed with quality.
5. Report failures rather than silently dropping them.
6. Choose the supported trade-off and state remaining uncertainty.

Commit:

```bash
git add lessons/0004-measuring-quantization-quality.html
git commit -m "docs: rebuild final lesson around practical choice"
```

## Task D4: Add proportional validation guidance

**Modify:** `lessons/0004-measuring-quantization-quality.html`

Teach three validation levels:

| Stakes | Appropriate validation |
|---|---|
| Casual or reversible use | Representative smoke tests and obvious failure checks |
| Important recurring workload | Matched tasks under each shortlisted candidate; repeat when outputs are stochastic |
| Public, expensive, or causal claim | Preregistered paired/repeated protocol from the advanced reference |

Make clear that an amateur does not need a research-grade experiment for every local choice.

Use a concise workload-to-quality table:

| Workload | Direct quality signal |
|---|---|
| Coding | Verified tests or task-specific checks |
| Classification | Accuracy/F1 or equivalent measure |
| Summarization | Factuality and required-content criteria |
| Chat/writing | Defined rubric or blinded preference |
| Agentic task | Externally verified completion |

Move F2P/P2P/reward details out of the main path and link to `../reference/evaluation-protocol.html`.

Commit:

```bash
git add lessons/0004-measuring-quantization-quality.html
git commit -m "docs: add proportional quant validation guidance"
```

## Task D5: End with an actionable choice template and quiz

**Modify:** `lessons/0004-measuring-quantization-quality.html`

End with:

```text
Selected model/checkpoint: [...]
Hardware and usable memory: [...]
Compatible runtime: [...]
Required context/headroom: [...]
Shortlisted candidates: A / B / C
Validation level: smoke test / matched tasks / controlled study
Primary quality result: [...]
Memory and speed result: [...]
Choice: [...]
Remaining uncertainty: [...]
```

Keep three or four quiz questions assessing:

1. why compatibility and fit are hard constraints;
2. why task quality comes before speed/steps;
3. what level of validation is proportional to the decision;
4. why unmatched tasks cannot isolate a quantization effect.

End by linking the general method to the planned controlled case study without implying that the learner must wait for it.

Commit:

```bash
git add lessons/0004-measuring-quantization-quality.html
git commit -m "docs: complete practical quant choice workflow"
```

## Task D6: Validate Track D

```bash
python3 scripts/audit_course.py --allow-planned-lessons
node --check assets/quiz.js
git diff --check
```

Expected: exits 0.

---

# Phase 1 — Parallel Track E: Mission-to-Course Audit

Work in `$WORKTREE_ROOT/track-e`.

## Task E1: Audit all living course surfaces against the mission

**Objective:** Prevent the rewrite from improving Lessons 2–5 while leaving stale framing elsewhere.

**Read only:**

- `MISSION.md`, `mission.html`
- `index.html`
- Lessons 1–4
- `reference/quantization-decision-checklist.html`
- `reference/tensors-and-layers.html`
- `AGENTS.md`, `QA.md`, `course.json`

**Create:** `docs/reviews/2026-07-18-mission-to-course-map.md`

Use this matrix:

| Surface | Practical job | Supporting knowledge | Learner action | Finding |
|---|---|---|---|---|
| Mission/index | Define learner, scope, and “best” | Conditional trade-offs | Know what course will and will not answer | pass/fix |
| Lesson 1 | Explain only the internals needed for quantization | Tensors, layers, weights | Understand what quantization changes | pass/fix |
| Lesson 2 | Explain approximation/storage mechanics | Levels, blocks, metadata | Understand the quant trade-off | pass/fix |
| New Lesson 3 | Explain fit/headroom | Runtime memory buckets | Measure whether candidate fits | pass/fix |
| Format lesson | Explain labels/compatibility | Category distinctions | Describe candidate completely | pass/fix |
| Choice lesson | Provide practical selection method | Proportional validation | Choose and state uncertainty | pass/fix |
| References | Preserve optional depth | Specialist detail | Look up detail when needed | pass/fix |

Findings must identify exact files/sections and classify blocker / important / polish. Track E does not edit course content.

Commit:

```bash
git add docs/reviews/2026-07-18-mission-to-course-map.md
git commit -m "docs: audit course surfaces against practical mission"
```

---

# Phase 2 — Integrate the Parallel Drafts Serially

## Task 2.1: Create the integration worktree

From the original repository root:

```bash
export INTEGRATION="$WORKTREE_ROOT/integration"
git worktree add "$INTEGRATION" -b course/practical-first-version "$BASE"
cd "$INTEGRATION"
```

## Task 2.2: Cherry-pick the authoring and audit branches

Cherry-pick all commits from each branch in this order:

1. `course/lesson-2`
2. `course/memory-lesson`
3. `course/format-lesson`
4. `course/choice-lesson`
5. `course/mission-audit`

Use the exact commit ranges reported by each track. Do not silently rewrite accepted prose while resolving conflicts. The expected conflicts are limited to reference/resource material; reconcile them by retaining all sourced, non-duplicated material.

After each branch:

```bash
python3 scripts/audit_course.py --allow-planned-lessons
git diff --check
```

If a cherry-pick introduces a failure, stop and resolve it before adding the next track.

## Task 2.3: Install the clean first-version filenames

**Objective:** Produce one clean current sequence with no compatibility routes.

Perform:

```bash
git mv lessons/0003-reading-quantization-formats.html lessons/0004-reading-quantization-formats.html
git mv lessons/0004-measuring-quantization-quality.html lessons/0005-choosing-and-validating-a-quant.html
git rm lessons/0003-quantization-in-practice.html
```

There is no published file for the planned current `0005-choosing-and-validating-a-quant.html`; its manifest entry will become Lesson 6’s case-study path.

Do not create redirects or tombstones. This is the first version.

## Task 2.4: Update the manifest

**Modify:** `course.json`

Use:

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
  "path": "lessons/0005-choosing-and-validating-a-quant.html",
  "title": "Choosing and Validating a Quant",
  "minutes": 10
},
{
  "number": 6,
  "path": "lessons/0006-controlled-quantization-case-study.html",
  "title": "Controlled Quantization Case Study",
  "minutes": 12,
  "status": "planned",
  "gate": "deferred-pending-controlled-evidence"
}
```

Adjust Lesson 2 duration to the final reading scope. Do not retain stale durations.

## Task 2.5: Update all titles, progress labels, and navigation

**Modify:** all five published lessons.

Required sequence:

```text
Lesson 1 → Lesson 2 → Lesson 3: Memory → Lesson 4: Formats → Lesson 5: Choose and Validate
```

- Top and bottom navigation must match.
- Lesson 5 must not link Next to planned Lesson 6.
- Page `<title>`, H1, progress text, and `course.json` must agree.
- Update Track B’s provisional next link and the accepted Track C/D handoffs after renaming.

## Task 2.6: Update living course surfaces

**Modify:**

- `index.html`
- `AGENTS.md`
- `QA.md`
- `reference/quantization-decision-checklist.html`
- `reference/tensors-and-layers.html` only if the mission audit requires it
- `resources.html`, `RESOURCES.md` for accepted source-ledger additions
- `learning-records/0003-quantization-in-practice.md`

Required updates:

- Five published lessons and one planned case study.
- Strict mode becomes the future six-lesson gate.
- Index cards use practical descriptions.
- The index/public course path must show that the general choice method is already published.
- The planned item must be labeled a controlled case study, not the missing practical decision method.
- Remove the obsolete lesson link from the learning record. Describe its historical source as a removed pre-release draft and point its supported concepts to the current Lesson 4/5 paths as appropriate.
- Apply exact blocker/important fixes from Track E’s mission audit.

Do **not** rewrite historical documents in `docs/plans/` or old audit reports. They are records of prior work. Add a supersession note only where a living document explicitly points readers to stale current guidance.

## Task 2.7: Commit structural integration explicitly

Stage only named files, not whole directories blindly:

```bash
git add course.json index.html AGENTS.md QA.md \
  lessons/0001-tensors-and-layers.html \
  lessons/0002-how-quantization-works.html \
  lessons/0003-model-memory-and-context.html \
  lessons/0004-reading-quantization-formats.html \
  lessons/0005-choosing-and-validating-a-quant.html \
  reference/quantization-decision-checklist.html \
  reference/tensors-and-layers.html \
  reference/quantization-formats.html \
  reference/evaluation-protocol.html \
  resources.html RESOURCES.md \
  learning-records/0003-quantization-in-practice.md

git add -u lessons/
git commit -m "docs: install practical five-lesson course sequence"
```

Before committing, inspect `git status --short` and remove duplicate path arguments if needed. Do not stage unrelated files.

---

# Phase 3 — Two Parallel Reviews on the Integrated Draft

Both reviewers inspect `$INTEGRATION` read-only and return full markdown findings. They do not modify files.

## Review R1: Mission, tone, and learner flow

Check every main-path section against:

- practical decision supported;
- minimum theory only;
- learner action enabled;
- adult, direct, approachable tone;
- no cutesy or compliance framing;
- previous lesson prerequisite is actually taught;
- next lesson feels necessary;
- Lesson 5 provides a usable decision now.

Required output: blocker / important / polish findings with exact file and section references, plus explicit passes for each lesson.

## Review R2: Technical evidence, accessibility, and publication contract

Check:

- implementation facts remain version-pinned;
- pedagogical examples are labeled;
- no universal causal claim from an analogy or observation;
- retained-state/cache claims are architecture-scoped;
- all quantitative tables have source/scope captions;
- artifact/encoding/recipe/runtime/backend/kernel categories remain distinct;
- glossary first occurrences and footers match;
- quizzes use shared JS and semantic/live-feedback contracts;
- five published lessons and one planned case study are consistent;
- no personal paths, private IDs, or unpublished results.

Required output: blocker / important / polish findings with exact file and section references, plus successful checks.

## Task 3.1: Write the review reports

The integration owner saves the returned reports as:

- `docs/reviews/2026-07-18-integrated-mission-tone-review.md`
- `docs/reviews/2026-07-18-integrated-technical-review.md`

## Task 3.2: Resolve every blocker and important finding serially

- Apply fixes on `course/practical-first-version`.
- Record each finding → fix → verification in the corresponding report.
- Re-run both reviewers after fixes.
- Do not proceed until both reviewers return no blockers or important findings.

Commit:

```bash
git add <explicit-fixed-files> \
  docs/reviews/2026-07-18-integrated-mission-tone-review.md \
  docs/reviews/2026-07-18-integrated-technical-review.md
git commit -m "fix: resolve integrated course review findings"
```

---

# Phase 4 — End-to-End Verification

## Task 4.1: Run all mechanical checks

From `$INTEGRATION`:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/audit_course.py --allow-planned-lessons
python3 -m py_compile scripts/audit_course.py scripts/analyze_case_study.py
node --check assets/quiz.js
git diff --check
```

Expected: all exit 0.

## Task 4.2: Run a focused privacy scan

Do not scan historical plans/reviews as if they were current public lesson content. Scan the public and living operational surfaces:

```bash
git grep -n '/Users/\|/home/\|Mac Studio\|MacBook\|private model\|local artifact' -- \
  'index.html' 'mission.html' 'MISSION.md' 'AGENTS.md' 'QA.md' \
  'lessons/*.html' 'reference/*.html' 'course.json' 'resources.html' 'RESOURCES.md'
```

Expected: no unintended personal paths, hardware identities, private model IDs, or artifact provenance. Review each match; do not treat an expected warning phrase as a failure without context.

## Task 4.3: Verify learner flow manually

Read Lessons 1–5 in order and record for each:

1. Which decision does this lesson support?
2. Which prior concept does it use?
3. What action can the learner take now?
4. Why does the next lesson follow?

Lesson 5 should answer the first three and end the published path; it need not manufacture a reason to enter the planned case study.

## Task 4.4: Verify responsive, keyboard, and quiz behavior

At desktop width and 390 px:

- no page-level horizontal overflow;
- wide tables have intentional scrolling and a visible hint;
- navigation order is logical;
- focus is visible;
- print output is readable.

For every quiz:

1. choose a wrong answer;
2. verify the correct answer and explanation appear;
3. verify feedback receives focus/is announced;
4. activate retry;
5. choose the correct answer;
6. verify reset behavior.

## Task 4.5: Confirm repository contents

```bash
git status --short
git ls-files 'lessons/*.html'
git log --oneline --decorate -10
```

Expected lesson files include only the five published first-version pages plus any actually supported non-lesson pages. They must not include:

- `lessons/0003-quantization-in-practice.html`
- old duplicate `0003-reading-quantization-formats.html`
- old duplicate `0004-measuring-quantization-quality.html`
- redirects or compatibility pages.

Expected worktree: clean after the final verification commit.

---

# Phase 5 — Merge and Deploy

## Task 5.1: Merge the verified integration branch

Return to the original repository worktree:

```bash
cd "$COURSE_REPO"
git status --short
git switch main
git merge --ff-only course/practical-first-version
```

Expected: clean fast-forward merge. If main advanced, stop and rebase/re-run verification; do not force the merge.

## Task 5.2: Push and verify GitHub Pages

```bash
git push origin main
```

Verify live:

- course home and mission;
- Lessons 1–5 in order;
- glossary fragments from every changed lesson;
- format and evaluation reference pages;
- planned Lesson 6 shown as deferred and unlinked as a published page;
- no obsolete pre-release lesson URLs are advertised anywhere in the site.

Do not report deployment complete until the live pages return the new titles/content.

## Task 5.3: Remove temporary worktrees after live verification

```bash
git worktree remove "$WORKTREE_ROOT/track-a"
git worktree remove "$WORKTREE_ROOT/track-b"
git worktree remove "$WORKTREE_ROOT/track-c"
git worktree remove "$WORKTREE_ROOT/track-d"
git worktree remove "$WORKTREE_ROOT/track-e"
git worktree remove "$WORKTREE_ROOT/integration"
```

Delete merged temporary branches only after confirming all commits are reachable from `main`.

---

## Parallelism and dependency map

```text
Baseline checks + worktrees
        │
        ├── Track A: Lesson 2 chunks ────────────────┐
        ├── Track B: Memory lesson chunks ───────────┤
        ├── Track C: Format lesson/reference chunks ─┼──> Serial draft integration
        ├── Track D: Choice lesson/reference chunks ─┤          │
        └── Track E: Mission audit ──────────────────┘          ▼
                                                    Structural renaming + living docs
                                                                  │
                                                                  ├── Review R1: mission/tone/flow
                                                                  └── Review R2: evidence/a11y/contracts
                                                                             │
                                                                             ▼
                                                                  Serial fixes + re-review
                                                                             │
                                                                             ▼
                                                                   Full QA → merge → deploy
```

### Safe parallel work

- Tracks A–E.
- Reviews R1 and R2.

### Must remain serial

- Cherry-picking track commits.
- Renaming files and deleting obsolete pre-release pages.
- Updating `course.json`, navigation, index, living docs, and learning-record links.
- Resolving integrated review findings.
- Full validation, merge, deployment, and live verification.

---

## Completion criteria

- Five published lessons give an amateur a complete practical method after model selection.
- Lesson 5 teaches choosing and proportional validation now; only the controlled case-study result is deferred.
- The course clearly distinguishes learner sequence from real decision order.
- Lesson 2 contains one quantization walkthrough and one group-size explanation, with scoped claims.
- Lesson 3 enables a fit/headroom measurement without requiring architecture expertise.
- Lesson 4 teaches category/compatibility reading through three representative examples; catalogue detail remains optional reference.
- Lesson 5 starts from compatible candidates and ends with a concrete, proportional choice template.
- No backward-compatibility files, redirects, or obsolete pre-release lesson pages remain.
- Historical plans/reviews remain intact; living docs describe five published lessons and one planned controlled case study.
- Both integrated reviews have no blocker or important findings.
- All automated, glossary, navigation, privacy, responsive, keyboard, quiz, and live-site checks pass.
