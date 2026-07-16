# LLM Internals Course Remediation Implementation Plan

**Source audit:** [`../reviews/2026-07-15-llm-course-audit.md`](../reviews/2026-07-15-llm-course-audit.md)

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Convert the current three-lesson draft into a technically reliable, accessible five-lesson course that teaches one reproducible process for choosing local-model quantization.

**Architecture:** Keep the site dependency-free and statically deployable. Add a small Python-standard-library audit/test layer, a shared quiz component, a five-lesson learner path, versioned evidence tables, and a separately gated case-study pipeline. Public pages remain generalized; exact local model/provider identities and raw trajectories stay in gitignored private manifests.

**Tech Stack:** Static HTML5, CSS, vanilla JavaScript, Python 3 standard library (`unittest`, `html.parser`, `json`, `csv`, `statistics`), GitHub Pages, Pier/Deep-SWE for the optional controlled case-study rerun.

---

## 1. Scope, baseline, and non-negotiable rules

- Baseline repository: `$COURSE_REPO`
- Baseline HEAD: `ee8d240`
- Baseline state: clean working tree
- Public course rule: do not expose provider/model names, personal setup details, local paths, prompts, private patches, or raw trajectories.
- Evidence rule: mechanism, implementation detail, empirical observation, and hypothesis must be labeled separately.
- Foundation-portability rule: Lessons 1 and 2 must teach implementation-independent concepts without relying on product, container, framework, backend, or runtime names in their instructional spine, worked examples, exercises, quizzes, or takeaways. Architecture-specific mechanisms must be labeled as such. Lesson 2 may end with one short named-ecosystem preview whose only purpose is to show that real implementations map the shared mechanics differently; it must not teach format details or make recommendations.
- Ecosystem-naming rule: distinguish checkpoint/model, artifact/container, quantization scheme, inference engine/runtime, and kernels/hardware. GGUF is a container/artifact format, not a runtime. GGUF/llama.cpp labels must never be applied to MLX/oMLX artifacts, and runtime compatibility claims must be versioned.
- Experimental rule: do not restore the 57%/thought-duplication claim. Publish a new result only after the exact-model matched-data gate passes.
- Draft-state rule: immediately mark the current `0003-quantization-in-practice.html` as draft and keep it out of the recommended learner path until the comparison is designed, preregistered, executed, analyzed, and the lesson is rewritten.
- “Q8” naming rule: use `Q8_0` only for the exact GGUF/llama.cpp format; the current local default is MLX affine 8-bit with group size 64 and must be named accordingly.
- Benchmark rule: run Pier/Deep-SWE jobs **sequentially, never in parallel**.
- Dependency rule: use Python standard library and browser-native APIs; do not add npm or Python dependencies unless a later blocker proves one necessary.
- Source rule: pin implementation-specific claims to a named upstream revision and a named reference model/artifact.
- Learning-record rule: do not silently rewrite history as though the learner had mastered revised material. Mark old records superseded and add new learning evidence only after the revised lessons are completed.

## 2. Target learner path

| Lesson | Path | Single learner win |
|---|---|---|
| 1 | `lessons/0001-tensors-and-layers.html` | Trace text from tokenization through runtime state and distinguish weights, activations, and cache |
| 2 | `lessons/0002-how-quantization-works.html` | Encode and decode one block using correct symmetric/affine math and calculate effective bpw |
| 3 | `lessons/0003-reading-quantization-formats.html` | Identify backend, scheme, metadata, and effective size without conflating GGUF and MLX |
| 4 | `lessons/0004-measuring-quantization-quality.html` | Design a valid paired evaluation and choose metrics appropriate to the workload |
| 5 | `lessons/0005-choosing-and-validating-a-quant.html` | Apply one five-step decision procedure to a complete memory/workload scenario |

Preserve the old `lessons/0003-quantization-in-practice.html` URL as a tiny compatibility redirect to Lesson 5. Mark it `data-course-redirect="true"` so audits exclude it from lesson counts.

## 3. Canonical decision procedure

Every promise, worked example, quiz, takeaway, and reference card must use this exact sequence:

1. **Identify the backend and quantized targets.** Name artifact format, engine, mode, group/block size, calibration/importance recipe, and whether weights, activations, or cache are quantized.
2. **Calculate memory.** Prefer measured artifact/runtime allocation; otherwise estimate weights using effective bpw and separately estimate architecture-appropriate runtime state/cache plus headroom.
3. **Shortlist formats that fit.** Include kernel/runtime compatibility and speed, not only size.
4. **Evaluate the exact workload.** Use paired task instances, controlled settings, repeated trials where stochastic, and task-specific quality metrics.
5. **Choose the Pareto point.** Select the quality/latency/memory trade-off supported by the evidence; state residual uncertainty.

## 4. Required formulas and caveats

Use these consistently:

```text
weight_bytes ≈ parameter_count × effective_bits_per_weight / 8
```

Prefer actual artifact size where available. Always label GB versus GiB.

For a conventional full-attention cache only:

```text
kv_bytes ≈ 2 × batch × sequence_length × layers
           × n_kv_heads × head_dim × bytes_per_element
```

State that GQA/MQA, sliding-window attention, cache quantization, linear attention, SSM/recurrent state, and hybrid architectures require model-specific formulas.

Teach quantization parameterizations separately:

```text
symmetric:                 x_hat = scale × q
affine integer zero point: x_hat = scale × (q - zero_point)
scale plus offset/minimum: x_hat = scale × q + offset
```

Do not imply that all formats store two FP16 metadata values per group.

---

# Phase A — Build the safety rails first

### Task 1: Start the remediation branch and preserve the baseline

**Objective:** Establish an isolated implementation branch and capture the pre-change state.

**Files:** None.

**Steps:**

1. Run:
   ```bash
   git status --short
   git rev-parse --short HEAD
   git switch -c course-review-remediation
   ```
2. Expected: empty status, HEAD `ee8d240`, new branch created.
3. Record the baseline HEAD in the first commit message; do not copy the review into public course pages.

**Verification:** `git branch --show-current` prints `course-review-remediation`.

---

### Task 1A: Quarantine the current Lesson 3 as a draft

**Objective:** Stop presenting the current empirical claims as settled guidance while the replacement experiment is being designed and run.

**Files:**
- Modify: `lessons/0003-quantization-in-practice.html`
- Modify: `index.html`
- Modify: `assets/style.css`

Add a high-contrast reusable draft-banner style and all of the following before any other public content changes:

```html
<meta name="robots" content="noindex">
<body data-course-status="draft">
  <aside class="status-banner status-banner--draft" role="note">
    <strong>Draft — evidence under review.</strong>
    The bf16-versus-8-bit comparison on this page was not a controlled experiment.
    Do not use its numerical claims or recommendations for model selection yet.
  </aside>
```

On `index.html`, mark the current Lesson 3 card **Draft — controlled comparison in progress** and remove language implying that it is a completed or validated decision guide. Keep the page reachable for review, but exclude it from the recommended learner path until Task 27 replaces it.

Do not attempt to repair the existing case-study prose in this quarantine task. Its later rewrite is hard-blocked on Task 20A and Tasks 23–26: experiment definition, preregistration, execution, and evidence-gated analysis.

**Verification:**

- The draft label is visible without scrolling on desktop and mobile.
- Search engines receive `noindex` for the draft page.
- The index does not present the draft as completed course material.
- No unsupported numerical claim appears before the draft warning.

**Commit:** `docs: mark quantization practice lesson as draft`

---

### Task 2: Write the first failing audit test

**Objective:** Define a testable API for course-wide structural checks before implementing the audit tool.

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_audit_course.py`

**Step 1: Write the failing test**

```python
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.audit_course import audit_workspace


class CourseAuditTests(unittest.TestCase):
    def test_reports_missing_local_fragment(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text(
                '<a href="reference.html#missing">broken</a>',
                encoding="utf-8",
            )
            (root / "reference.html").write_text(
                '<h1 id="present">Reference</h1>',
                encoding="utf-8",
            )
            issues = audit_workspace(root)
            self.assertTrue(any(i.code == "broken-fragment" for i in issues))
```

**Step 2: Verify RED**

Run:
```bash
python3 -m unittest tests.test_audit_course.CourseAuditTests.test_reports_missing_local_fragment -v
```

Expected: import failure because `scripts.audit_course` does not exist.

**Step 3: Commit only the failing test**

```bash
git add tests
git commit -m "test: define course audit contract"
```

---

### Task 3: Implement the minimal audit core

**Objective:** Make the broken-file/fragment contract pass using only the Python standard library.

**Files:**
- Create: `scripts/__init__.py`
- Create: `scripts/audit_course.py`

**Implementation API:**

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Issue:
    code: str
    path: Path
    detail: str


def audit_workspace(root: Path) -> list[Issue]:
    """Return deterministic structural issues for every HTML file below root."""
```

Implement an `HTMLParser` subclass that records IDs and hrefs, then reports:

- missing local files;
- missing fragments;
- duplicate IDs.

The CLI must print one issue per line and exit `1` when issues exist:

```bash
python3 scripts/audit_course.py
```

**Verification:**

```bash
python3 -m unittest tests.test_audit_course -v
```

Expected: PASS.

**Commit:**

```bash
git add scripts tests
git commit -m "test: add dependency-free course audit core"
```

---

### Task 4: Add the course manifest contract

**Objective:** Make lesson order, title, duration, and navigation machine-checkable.

**Files:**
- Create: `course.json`
- Modify: `tests/test_audit_course.py`
- Modify: `scripts/audit_course.py`

**Step 1: Add a failing test** asserting that every non-redirect lesson in `course.json` exists, has the expected `<title>` and `<h1>`, and declares the same duration shown on `index.html`.

**Manifest schema:**

```json
{
  "title": "LLM Internals for Quantization Decisions",
  "lessons": [
    {
      "number": 1,
      "path": "lessons/0001-tensors-and-layers.html",
      "title": "From Tokens to Runtime State",
      "minutes": 8
    }
  ]
}
```

Populate all five target lessons, even though Lessons 3–5 do not exist yet. During migration, allow an explicit `"status": "planned"`; remove every planned status before final release.

**Verification:**

```bash
python3 -m unittest tests.test_audit_course -v
python3 scripts/audit_course.py --allow-planned-lessons
```

**Commit:** `test: add course manifest and sequence contract`

---

### Task 5: Add glossary-contract tests

**Objective:** Prevent shared-letter anchors, duplicate first-occurrence links, and footer drift.

**Files:**
- Modify: `tests/test_audit_course.py`
- Modify: `scripts/audit_course.py`

**RED cases:**

- two `<dt>` entries resolving to the same `id`;
- glossary `<dt>` without an ID;
- duplicate `glossary-link` target in one lesson;
- inline glossary target missing from `.terms-footer`;
- footer target missing from inline links;
- fragment targeting a letter heading instead of a term `<dt>`.

**Required issue codes:**

```text
glossary-term-missing-id
glossary-anchor-shared
glossary-link-duplicate
glossary-footer-missing
glossary-footer-extra
glossary-target-not-term
```

**Verification:** watch each new test fail before implementing its corresponding check, then run the full suite.

**Commit:** `test: enforce term-specific glossary contract`

---

### Task 6: Add accessibility and quiz-contract tests

**Objective:** Turn the audit’s semantic and interaction requirements into executable checks.

**Files:**
- Modify: `tests/test_audit_course.py`
- Modify: `scripts/audit_course.py`

For non-redirect HTML pages, check:

- exactly one `<main>`;
- navigation is inside `<nav>`;
- every table has `<caption>`, `<thead>`, `<tbody>`, and scoped `<th>` cells;
- every button has `type="button"`;
- every quiz question has one correct option;
- quiz feedback has `role="status"` or `aria-live="polite"`;
- lessons use `../assets/quiz.js` and contain no inline `checkAnswer` implementation;
- top and bottom navigation match `course.json`;
- no whole-page horizontal overflow marker is waived without an explanation.

Implement each check through a RED → GREEN cycle using small fixture strings.

**Verification:**

```bash
python3 -m unittest discover -s tests -v
```

**Commit:** `test: codify accessibility and quiz requirements`

---

### Task 7: Protect private benchmark material

**Objective:** Prevent exact model/provider identities and raw trajectories from reaching the public repository.

**Files:**
- Create or modify: `.gitignore`
- Create: `case-study/private/README.md`

**Required ignore rules:**

```gitignore
case-study/private/*
!case-study/private/README.md
case-study/raw/
```

The README must explain that the private directory contains exact checkpoint IDs, provider names, local paths, prompts, and raw job mappings; public artifacts use stable aliases.

**Verification:** create a temporary ignored file, confirm `git status --short` does not show it, then delete it.

**Commit:** `chore: protect private benchmark metadata`

---

# Phase B — Establish content governance and shared components

### Task 8: Replace the stale authoring rules

**Objective:** Make future edits preserve the corrected course contract.

**Files:**
- Modify: `AGENTS.md`

Replace single-letter glossary guidance with:

```html
<dt id="kv-cache">KV Cache</dt>
<a href="../reference/glossary.html#kv-cache" class="glossary-link">KV cache</a>
```

Add explicit rules for:

- term-specific stable slugs;
- first-occurrence-only links and exact footer parity;
- mechanism/implementation/evidence/hypothesis labels;
- backend/quantization-scope identification;
- the Lessons 1–2 foundation-portability boundary, including the single permitted end-of-Lesson-2 ecosystem preview;
- source revision and model scope on numerical tables;
- public anonymization;
- equal-length quiz options and immediate explanatory feedback;
- semantic table/landmark/navigation requirements;
- commands:
  ```bash
  python3 -m unittest discover -s tests -v
  python3 scripts/audit_course.py
  ```

**Verification:** no examples using `#T`, `#W`, or other shared-letter anchors remain.

**Commit:** `docs: codify corrected course authoring rules`

---

### Task 9: Build the source and evidence ledger

**Objective:** Replace blog-led sourcing with a versioned claim-to-source map before rewriting claims.

**Files:**
- Modify: `RESOURCES.md`
- Modify: `resources.html`

Use three sections with stable IDs:

1. `#canonical` — official source/docs, format specs, exact model configs, original papers, raw experiment artifacts.
2. `#explainers` — 3Blue1Brown, Raschka, Illustrated Transformer, selected blogs.
3. `#community` — forums and practitioner discussion.

For implementation claims, record:

- source URL;
- resolved commit/revision;
- access date;
- exact claim supported;
- model/artifact scope.

Minimum canonical sources:

- Transformer paper;
- current llama.cpp quantize README and `src/llama-quant.cpp` at one pinned revision;
- GGUF specification and canonical acronym source;
- GGML block structures;
- MLX quantization API and oMLX quantization documentation;
- exact public model configuration for the 8-bit artifact;
- peer-reviewed/high-trust quantization evaluation papers;
- KV-cache mechanics documentation.

**Verification:** every quantitative table planned for the course has a corresponding canonical source entry; no blog/video is labeled primary.

**Commit:** `docs: replace source taxonomy with evidence ledger`

---

### Task 10: Create and test the shared quiz component

**Objective:** Fix wrong-answer behavior once and remove three duplicated scripts.

**Files:**
- Create: `assets/quiz.js`
- Modify: `assets/style.css`
- Modify temporarily: all current `lessons/*.html`
- Modify: `tests/test_audit_course.py`

**Behavior contract:**

- clicking an incorrect option marks it incorrect;
- the correct option is visibly and semantically marked;
- feedback explains why the selected answer is wrong and why the correct answer is right;
- all options disable after submission;
- a reset button restores the question when retry is enabled;
- feedback is announced with `aria-live="polite"`;
- keyboard focus moves to feedback, then returns predictably on reset;
- correctness is not communicated by color alone.

Use markup such as:

```html
<fieldset class="quiz-question" data-quiz>
  <legend>...</legend>
  <button type="button" class="quiz-option" data-correct="true">...</button>
  <p class="quiz-feedback" aria-live="polite" tabindex="-1"></p>
  <button type="button" class="quiz-reset" hidden>Try again</button>
</fieldset>
<script src="../assets/quiz.js" defer></script>
```

First make the static contract test fail on current inline scripts, then migrate all three current lessons and make it pass.

**Runtime verification:** serve locally, choose a wrong and correct answer in each distinct quiz configuration, and inspect option classes/feedback using browser tools.

**Commit:** `fix: centralize accessible quiz feedback`

---

### Task 11: Add the responsive and accessibility CSS foundation

**Objective:** Provide reusable styles before rewriting pages.

**Files:**
- Modify: `assets/style.css`

Add and test:

- `.page-shell`, `main`, `.course-nav`, `.lesson-progress`;
- `.table-scroll` with visible “Scroll horizontally” hint;
- mobile card alternative for prose-heavy comparison tables;
- `:focus-visible` styles for links/buttons;
- `.sr-only` utility;
- quiz correct/incorrect icons and text, not color alone;
- responsive pipeline/diagram styles;
- `@media (max-width: 640px)` rules;
- print rules that expose URLs and worked answers appropriately.

**Acceptance:** at 390px, the document width equals viewport width; only intentional `.table-scroll` children may overflow.

**Commit:** `style: add responsive accessible course components`

---

# Phase C — Repair canonical references and terminology

### Task 12: Give every glossary term a unique anchor

**Objective:** Fix the glossary’s navigation and targeting without yet rewriting all definitions.

**Files:**
- Modify: `reference/glossary.html`
- Modify: every HTML file containing glossary hrefs

**Steps:**

1. Give each `<dt>` a stable slug ID, e.g. `attention`, `bf16`, `blockwise-quantization`, `effective-bpw`, `kv-cache`, `quantization`, `tensor`, `token`, `transformer`.
2. Keep letter heading IDs only for A–Z navigation.
3. Add the missing V navigation item.
4. Update every lesson/reference/footer href to term slugs.
5. Run the glossary audit and resolve all target errors.

**Verification:** no glossary link resolves to a letter heading; every `<dt>` ID is unique.

**Commit:** `fix: add term-specific glossary anchors`

---

### Task 13: Correct and expand glossary definitions

**Objective:** Make the glossary the canonical vocabulary source for the revised lessons.

**Files:**
- Modify: `reference/glossary.html`

Correct at minimum:

- Attention: causal mask and model variants.
- Attention head: learned projections without assigning guaranteed semantic roles.
- bf16 versus FP16: same storage width, different range/precision.
- Embedding: learned token lookup; contextual meaning emerges later.
- FFN: gated modern variants and architecture-specific dimensions; not “the thinking part.”
- GGUF: **GGML Universal File**.
- IQ: non-linear/codebook-style formats; importance matrix nuance.
- K-quant: superblock encoding versus `_M` file recipe.
- Layer Norm/RMSNorm: distinguish them.
- Parameter/weight/bias/norm scale: do not equate every parameter with a weight.
- Quantization: include target scope.
- Scale factor/zero point/offset: mathematically distinct.
- Thinking budget: empirical control, not guaranteed remedy or harm.
- Thought duplication: remove as settled quantization symptom; if retained, label it a diagnostic requiring an operational definition.
- Transformer: “most”/hybrid qualification, not “all modern LLMs.”

Add terms needed by the new course: activation, affine quantization, causal mask, decoding, effective bits per weight, hidden state, symmetric quantization, runtime state.

Remove personal/tool-specific terms from the general glossary unless required by a clearly labeled case-study appendix.

**Verification:** a terminology search finds no `bf16 (FP16)`, “all modern LLMs,” “every parameter is a weight,” or wrong GGUF expansion.

**Commit:** `docs: correct quantization and transformer glossary`

---

### Task 14: Rebuild the tensors-and-layers reference

**Objective:** Align the quick reference with modern decoder/hybrid architectures and the memory model.

**Files:**
- Modify: `reference/tensors-and-layers.html`

Required sections:

1. Token IDs → embeddings → hidden states → logits → decoding.
2. Shape versus values.
3. Learned weights versus activations versus retained runtime state.
4. Causal attention formula:
   ```text
   softmax((QK^T / sqrt(d_k)) + causal_mask)V
   ```
5. GQA/MQA, gated FFNs, RMSNorm, residuals, and hybrid architecture caveats.
6. Weight-memory formula and standard KV formula with explicit limits.
7. One complete worked memory example using GB/GiB labels.

Remove universal 65/30/5 parameter splits and any assertion that FFNs dominate precision sensitivity.

**Verification:** all substantive definitions link to the corrected glossary and cite canonical sources.

**Commit:** `docs: rebuild tensors and runtime-state reference`

---

### Task 15: Rebuild the quantization-formats reference

**Objective:** Turn the current decoder ring into an accurate backend-aware quick reference.

**Files:**
- Modify: `reference/quantization-formats.html`

Required structure:

1. “Identify the backend first.”
2. GGUF/llama.cpp underlying tensor encoding versus file recipe.
3. MLX/oMLX quantization mode/group-size section.
4. Nominal label versus raw block bpw versus full-model effective bpw.
5. One versioned llama.cpp table for a named reference model and pinned revision.
6. IQ and importance-matrix caveats.
7. No undefined “quality versus FP16” percentages.
8. Link to the five-step decision reference rather than another independent task matrix.

Remove the old personal benchmark table entirely until the new case-study gate passes.

**Verification:** searches find no universal `95% quality`, no `8-bit = Q8_0`, and no fixed attention/FFN bit assignment.

**Commit:** `docs: replace quantization decoder with backend-aware reference`

---

### Task 16: Add the canonical decision checklist reference

**Objective:** Give learners one printable procedure shared by Lessons 4 and 5.

**Files:**
- Create: `reference/quantization-decision-checklist.html`

Include:

- the five decision steps verbatim;
- inputs needed for each step;
- weight/cache formulas with units;
- evidence table template;
- paired-evaluation checklist;
- red flags: unmatched tasks, mixed architectures, artifact counts called completions, missing verifier data, generic bit labels, undefined quality percentages;
- a blank decision record and a completed generic example.

**Verification:** the checklist is useful without reading the lessons and introduces no independent heuristic.

**Commit:** `docs: add canonical quantization decision checklist`

---

# Phase D — Rebuild the learner journey

### Task 17: Rewrite Lesson 1 around the complete dataflow

**Objective:** Remove prerequisite gaps before quantization is introduced while keeping the foundation independent of any artifact format, framework, backend, or runtime.

**Files:**
- Modify: `lessons/0001-tensors-and-layers.html`

Teach in this order:

1. Text → tokens → IDs.
2. IDs → token embeddings.
3. One small vector/matrix multiplication with explicit shapes and values.
4. Contextual hidden states through attention/FFN/residual/norm blocks.
5. Final logits → softmax/decoding → next token.
6. Three numeric domains: learned weights, activations, retained state/cache.
7. What weight-only quantization changes and does not change.

Use neutral terms such as `model artifact`, `inference engine`, `numeric format`, and `retained runtime state`. Do not use GGUF, MLX/oMLX, llama.cpp, vLLM, SGLang, or production quantization labels as explanatory examples. Present a KV cache as one retained-state mechanism used by conventional attention, not as a universal property of every LLM; name the existence of recurrent, state-space, linear-attention, and hybrid alternatives without detouring into their implementations.

Replace “all intelligence lives in weights; no lookup table” with bounded language: learned behavior is primarily encoded in parameters, including the embedding lookup, while observed behavior also depends on architecture, tokenizer, prompt, decoding, and external context/tools.

Add:

- one worked round trip;
- one retrieval quiz;
- one scenario asking which object is being quantized;
- citations beside claims;
- accurate duration and navigation.

**Verification:** learner can answer “what is stored, what flows, and what is retained between decoding steps?” without reading Lesson 2; the instructional content contains no ecosystem-specific artifact, framework, backend, runtime, or quantization-scheme names.

**Commit:** `docs: rebuild lesson one around model dataflow`

---

### Task 18: Rewrite Lesson 2 as quantization mechanics only

**Objective:** Preserve the strong numerical example while correcting its mathematics, reducing cognitive load, and teaching a portable mechanism rather than one ecosystem's encoding.

**Files:**
- Modify: `lessons/0002-how-quantization-works.html`

Required flow:

1. FP16/bf16 are floating-point formats with nonuniform spacing; do not describe FP16 as 65,536 linear values in any range.
2. Symmetric and affine parameterizations taught separately.
3. A clearly labeled pedagogical toy scheme with 8–16 values and an explicit encode/store/decode/error calculation; do not present it as any production format.
4. Block/group metadata and effective bpw.
5. Smaller groups versus metadata overhead and outliers.
6. Dot-product error:
   ```text
   y_hat - y = sum_i(error_i × activation_i)
   ```
   Explain why errors can partly cancel and why outliers/sensitive directions still matter.
7. Production formats differ from the toy scheme.

Use `4-bit` and `8-bit` only as code widths inside the named toy scheme, never as complete production-format identities or quality levels. Move all production labels, decoder rings, block-layout details, perplexity, agentic guidance, case-study claims, compatibility claims, and decision matrices out of this lesson.

End with one brief callout titled **“The same mechanics, different implementations”**. It may name GGUF/llama.cpp `Q8_0`, MLX affine 8-bit, vLLM, and SGLang only to establish that containers, schemes, frameworks, and runtimes are different categories and do not implement an undefined “8-bit” identically. Keep the callout to one short paragraph or compact taxonomy row, make no quality or compatibility recommendation, and link directly to Lesson 3 for the implementation details.

**Verification:** one lesson, one portable mechanism, one complete calculation, and no production ecosystem term outside the single closing preview or its Lesson 3 link. The preview contains no size, quality, speed, support, or compatibility claim and no GGUF decoder ring.

**Commit:** `docs: focus lesson two on correct quantization mechanics`

---

### Task 19: Create Lesson 3 on formats and runtimes

**Objective:** Teach learners how to identify an artifact without translating labels across ecosystems.

**Files:**
- Create: `lessons/0003-reading-quantization-formats.html`

Required flow:

1. Begin with a taxonomy that separates checkpoint/model, artifact/container, quantization scheme, inference engine/runtime, and kernels/hardware.
2. Classify GGUF as a container/artifact, MLX as a framework/ecosystem, and llama.cpp, vLLM, and SGLang as inference engines/runtimes; state that exact format and quantization support is version-dependent.
3. Start artifact inspection with the backend/runtime identification question.
4. Decompose a GGUF example into container, underlying tensor type, file recipe, and measured effective bpw.
5. Decompose an MLX example into mode, group size, dtype, and quantized target.
6. Contrast `Q8_0` with MLX affine 8-bit explicitly.
7. Explain K superblocks versus `_S/_M/_L` mixture recipes.
8. Explain IQ without “important weights receive extra bits.”
9. Show why implementation version and architecture matter; do not add an unversioned cross-runtime compatibility matrix.
10. End with an artifact-inspection exercise using two anonymized config snippets.

**Verification:** the correct quiz answer depends on config fields, not the word “8-bit.”

**Commit:** `docs: add backend-aware format lesson`

---

### Task 20: Create Lesson 4 on measuring quality

**Objective:** Replace the false “perplexity versus agents” split with a valid evaluation framework.

**Files:**
- Create: `lessons/0004-measuring-quantization-quality.html`

Teach:

- perplexity/KL divergence as intrinsic next-token-distribution measures;
- downstream task metrics for chat, classification, summarization, reasoning, coding, safety, and agents;
- why similar perplexity does not prove equal task behavior;
- success/F2P/P2P/reward as primary SWE outcomes;
- steps, tokens, latency, and cost as secondary outcomes interpreted with quality;
- exact matched tasks, repetitions/seeds, controlled settings, attrition, uncertainty;
- empirical observation versus causal mechanism;
- a miniature example showing how mixed architectures manufacture a misleading mean.

Use the invalid old `n=29/n=7` aggregation only as an anonymized **methodological anti-example**, never as evidence about quantization. State that exact-model filtering changed the descriptive step delta from 57% to 17.4% and still did not establish causality.

**Verification:** quiz asks learners to reject an unmatched comparison and select appropriate primary metrics.

**Commit:** `docs: add controlled-evaluation lesson`

---

# Phase E — Rebuild the case study under an evidence gate

### Task 20A: Design the bf16-versus-Q8 experiment before touching the lesson

**Objective:** Freeze the scientific question, the exact meaning of “Q8,” the estimands, sample, and analysis rules before creating or inspecting new comparison results.

**Files:**
- Create: `case-study/experiment-design.md`

**Step 1: Resolve what “Q8” means**

Choose exactly one same-backend comparison and record the decision:

- **Default for the current local stack:** bf16 weights versus **MLX affine 8-bit, group size 64** from the same dense checkpoint family, both served by the same oMLX revision. Public wording must say “MLX affine 8-bit,” not `Q8_0`.
- **Alternative only if the intended question is literally GGUF `Q8_0`:** convert the same base checkpoint to GGUF BF16/F16 and GGUF `Q8_0`, run both through the same pinned llama.cpp backend, and do not mix those results with MLX/oMLX runs.

Do not compare MLX affine 8-bit with GGUF `Q8_0`, and do not use `Q8` as an undefined umbrella label in the final lesson.

**Step 2: Define the question and estimands**

Primary question:

> For the same checkpoint family, backend, agent harness, task instances, and inference settings, how does the selected 8-bit weight format change task quality relative to bf16?

Pre-register:

- primary estimands: paired differences in F2P and P2P;
- guardrail outcome: binary reward/pass rate;
- secondary estimands: steps, input/output tokens, elapsed time, and peak context, interpreted jointly with quality;
- no causal KV-cache or thought-duplication estimand;
- a non-inferiority margin only if it is justified before running; otherwise report estimation and confidence intervals without a pass/fail equivalence claim.

**Step 3: Select the sample before results**

Default full design:

- five exact task-instance IDs;
- at least two languages/task types, with known environment-flaky tasks excluded by a stated rule rather than by observed scores;
- four repetitions per task and condition;
- two conditions;
- **40 sequential trials total**.

Use `$DEEP_SWE_DIR/tasks/manifest.json` to resolve IDs and indices. Record why each task was selected. If compute constraints force a smaller pilot, label it a pilot and prohibit general recommendations until the full design is completed.

**Step 4: Freeze controlled variables**

Record exact values for:

- checkpoint identity/architecture alias;
- backend and revisions;
- quantization scheme/group size and quantized targets;
- tokenizer/chat template;
- `preserve_thinking`, thinking-budget state, max output tokens, context limit;
- temperature, top-p, seed support, stopping rules;
- Pier/agent/tool policy and verifier configuration;
- cache precision and context handling.

Only weight precision may differ between conditions unless the design explicitly names another factor.

**Step 5: Predefine analysis and attrition**

- Pair by exact task-instance ID and repetition.
- Cluster uncertainty by task; report task-level points as well as the aggregate.
- Use a paired bootstrap or permutation interval implemented with a fixed public analysis seed.
- Count discovered artifacts, valid attempts, verifier-covered attempts, and successful completions separately.
- Treat model/agent timeouts as outcomes.
- Repair and rerun environment/verifier failures according to a predeclared rule; retain them in the attrition table.
- Never condition efficiency conclusions on a cherry-picked successful subset without also showing the full outcome distribution.

**Verification:** an independent reviewer can implement the run matrix and analysis from `experiment-design.md` without asking what Q8 means or choosing rules after seeing results.

**Commit:** `docs: design controlled bf16 versus eight-bit experiment`

---

### Task 21: Write failing tests for the case-study analyzer

**Objective:** Prevent the exact aggregation mistakes that caused the original conclusion.

**Files:**
- Create: `tests/test_case_study_analysis.py`
- Create: `tests/fixtures/case-study/`

Synthetic fixtures must prove that the analyzer:

- groups by exact checkpoint alias, architecture, engine, scheme, task-instance ID, and repetition;
- never combines dense and MoE artifacts because both contain `bf16`;
- reports discovered, valid-attempt, verifier-covered, and successful counts separately;
- classifies environment failures separately from model/agent failures;
- keeps model/agent timeouts as outcomes rather than silently excluding them;
- pairs only identical task-instance IDs;
- refuses to produce a causal headline when pairs or primary metrics are missing;
- computes paired F2P/P2P/reward first and step/token/latency deltas second;
- never emits a thought-duplication claim because no validated metric exists.

**Verify RED:** import of `scripts.analyze_case_study` fails.

**Commit:** `test: define case-study evidence gate`

---

### Task 22: Implement the case-study analyzer

**Objective:** Produce deterministic sanitized trial and summary artifacts from private job mappings.

**Files:**
- Create: `scripts/analyze_case_study.py`
- Modify: `tests/test_case_study_analysis.py`

**CLI:**

```bash
python3 scripts/analyze_case_study.py \
  --manifest case-study/private/manifest.json \
  --trials-out case-study/data/trials.json \
  --summary-out case-study/data/summary.json
```

Public trial schema:

```json
{
  "checkpoint_alias": "dense-27b",
  "precision_alias": "mlx-affine-int8-g64",
  "architecture": "dense-hybrid",
  "task_alias": "task-01",
  "repetition": 1,
  "attempt_status": "valid",
  "verifier_status": "complete",
  "reward": 0,
  "f2p": 0.80,
  "p2p": 1.0,
  "steps": 100,
  "input_tokens": 0,
  "output_tokens": 0,
  "elapsed_seconds": 0
}
```

Do not export local paths, raw task content, provider/model IDs, prompts, or patches.

**Verification:** all synthetic tests pass and generated JSON is stable across repeated runs.

**Commit:** `feat: add controlled case-study analyzer`

---

### Task 23: Pre-register the benchmark protocol

**Objective:** Decide the comparison before seeing new results.

**Files:**
- Create: `case-study/protocol.md`
- Create: `case-study/private/manifest.example.json`
- Create privately: `case-study/private/manifest.json` (ignored)

Default protocol, copied from and subordinate to `case-study/experiment-design.md`:

- Same dense checkpoint family and architecture in both conditions.
- Condition A: bf16 weights.
- Condition B: the exact same-backend 8-bit scheme selected in Task 20A. For the current local default this is MLX affine 8-bit, group size 64; it must not be called GGUF `Q8_0`.
- Same oMLX/Pier version, prompt/template, tool policy, `preserve_thinking`, no thinking budget, max tokens, max context, stopping rules, and verifier config.
- Five selected task-instance IDs representing at least two task types/languages, chosen before running from `tasks/manifest.json`.
- Four repetitions per task and condition: 40 total trials.
- Sequential execution only.
- Primary: paired F2P and P2P differences; reward/pass rate as a guardrail.
- Secondary: steps, input/output tokens, elapsed time, and peak context, interpreted jointly with quality.
- Predeclared attrition categories: environment/harness failure, verifier-only failure, valid model/agent timeout, completed attempt.
- Environment/verifier failures are repaired/rerun and retained in the attrition table; model/agent failures remain valid outcomes.
- Paired task-level points plus a task-clustered bootstrap/permutation interval using a fixed analysis seed.
- No universal conclusion beyond the tested checkpoint, engine, scheme, tasks, and settings.

Use public aliases in `protocol.md`; keep exact local model/provider IDs in the ignored manifest.

**Verification:** a reviewer can identify every controlled variable and exclusion rule before any run starts.

**Commit:** `docs: preregister paired quantization case study`

---

### Task 24: Run the benchmark preflight

**Objective:** Prove both conditions and all task indices are configured identically before spending compute.

**Files:** private manifest only; no public commit.

**Steps:**

1. Resolve selected task indices from `$DEEP_SWE_DIR/tasks/manifest.json`; never use filesystem order.
2. Start Docker if needed with `open -a Docker`.
3. Verify oMLX exposes both private model IDs.
4. Snapshot effective model settings into the ignored manifest.
5. Run one smoke task per condition sequentially.
6. Confirm job output contains trajectory and verifier artifacts and the analyzer classifies both correctly.
7. If settings differ, stop and fix them before the full matrix.

**Run template:**

```bash
source case-study/private/models.env
DEEP_SWE_DIR="$DEEP_SWE_DIR" \
DEEP_SWE_MODEL="$MODEL_ID" \
bash /Users/matthijs/.bin/deep-swe <<< "$MANIFEST_INDEX"
```

Never launch the second command until the first job has finished and Docker resources are clean.

**Verification:** smoke results appear as two valid, same-task, exact-model pairs in analyzer output.

---

### Task 25: Execute the 40-trial paired matrix sequentially

**Objective:** Collect the preregistered evidence required for a scoped bf16-versus-eight-bit comparison.

**Files:** ignored private manifests/raw artifacts only during execution.

**Steps per trial:**

1. Record planned condition/task/repetition in the private manifest.
2. Run one Pier job.
3. Wait for completion.
4. Verify trajectory, result, and reward artifacts.
5. Classify environment, verifier, or model/agent failure according to the preregistered rules.
6. Repair verifier/environment failures without altering model output; rerun the whole trial only when the protocol requires it.
7. Update the manifest and proceed to the next trial.

**Hard rule:** no parallel runs.

**Completion gate:** every planned cell has either a valid outcome or a documented non-model attrition followed by the prescribed replacement.

---

### Task 26: Analyze and publish only what passes the evidence gate

**Objective:** Produce a scoped public case study without resurrecting unsupported causal language.

**Files:**
- Create: `case-study/data/trials.json`
- Create: `case-study/data/summary.json`
- Create: `case-study/results.html`

Report:

- planned/discovered/valid/verifier-covered/successful counts;
- per-task paired F2P/P2P/reward distributions;
- paired secondary deltas with uncertainty or at minimum individual paired points;
- all exclusions and attrition;
- exact public scheme/architecture descriptions;
- limitations and non-generalizability.

Decision gate:

- If primary metrics are incomplete or mixed, publish “inconclusive” and the method.
- If no successful trials exist in either condition, do not claim equal accomplished work.
- If steps differ but primary quality does not support equivalence, do not call the step difference an efficiency penalty.
- Do not publish thought duplication or KV-cache causality.

**Verification:** `python3 scripts/analyze_case_study.py ...` reproduces both committed JSON files exactly.

**Commit:** `docs: publish controlled quantization case study`

---

# Phase F — Finish the practical course and synchronize all surfaces

### Task 27: Rebuild Lesson 5 around the five-step decision

**Objective:** Replace the quarantined draft only after the controlled comparison has been analyzed, giving the learner one executable capstone rather than competing rules.

**Hard dependency:** Do not begin this rewrite until Tasks 20A and 23–26 are complete. If the full experiment is not complete, keep the current page marked draft; do not promote pilot or historical observations into a finished lesson.

**Files:**
- Rename: `lessons/0003-quantization-in-practice.html` → `lessons/0005-choosing-and-validating-a-quant.html`
- Create: `lessons/0003-quantization-in-practice.html` compatibility redirect

Required content:

1. The canonical five steps verbatim.
2. A generic worked scenario with explicit parameters, effective bpw, context, architecture, cache precision, GB/GiB, and headroom.
3. Two candidate artifacts from the same backend, then a workload evaluation design.
4. Larger-lower-precision versus smaller-higher-precision framed as an empirical candidate comparison, not a redundancy law.
5. Thinking budget framed as a separately measured variable.
6. No fixed 70% law, 2–4 GB cache allowance, 10/30% step thresholds, task-type universal ranking, “creative fuzziness,” or “below Q4 is unsuitable.”
7. Link to `case-study/results.html` only after Task 26; if evidence is inconclusive, say so plainly.

**Applied capstone:** provide a new scenario, learner worksheet, immediate checks for arithmetic/metric choices, and a complete worked answer/rubric.

**Verification:** a learner can reach one justified recommendation and state what evidence could change it.

**Commit:** `docs: rebuild final quantization decision lesson`

---

### Task 28: Generalize the mission and rebuild the index

**Objective:** Make the public entry path consistent with the revised course and keep private motivation out of the teaching spine.

**Files:**
- Modify: `mission.html`
- Modify: `MISSION.md`
- Modify: `index.html`
- Modify: `course.json`

Rules:

- Keep the private motivation in `MISSION.md` as context, but remove unsupported “I have seen quantization degrade reasoning” conclusions.
- Make `mission.html` a universal learner objective.
- Do not claim the course is based on an 8-bit-versus-4-bit benchmark when the study is bf16 versus MLX affine 8-bit.
- Add five lesson cards in manifest order.
- Synchronize lesson titles and realistic durations.
- Link the three reference pages, decision checklist, case study, resources, and glossary.

**Verification:** the index promise maps to one lesson outcome, exercise, takeaway, and reference for each promised skill.

**Commit:** `docs: align mission and five-lesson course index`

---

### Task 29: Repair all page structure, navigation, and tables

**Objective:** Apply the shared accessibility contract to every public page.

**Files:**
- Modify: all non-redirect `.html` files
- Modify: `assets/style.css`

For each page:

- one `<main>`;
- real `<nav>` landmarks;
- consistent top and bottom navigation;
- correct Previous/Home/Next for lessons;
- `<caption>`, `<thead>`, `<tbody>`, and `scope` on tables;
- row headers where appropriate;
- responsive wrapper/card treatment;
- explicit `type="button"`;
- no raw ampersands;
- descriptive titles and meta descriptions;
- print behavior checked.

**Verification:** the semantic audit reports zero issues and keyboard focus remains visible.

**Commit:** `fix: apply semantic page and navigation contract`

---

### Task 30: Synchronize glossary links, citations, and terms footers

**Objective:** Make every page satisfy the authoring contract after all prose has stabilized.

**Files:**
- Modify: all lessons and reference pages
- Modify: `reference/glossary.html`

**Steps:**

1. Link each glossary term only on its first instructional occurrence, excluding quizzes/code.
2. Generate or manually reconcile each `.terms-footer` from inline canonical targets.
3. Put citations next to quantitative and implementation-specific claims.
4. Give every evidence table a source/model/revision caption.
5. Remove stale personalized Deep-SWE/oMLX glossary entries unless used in the labeled case study.
6. Run the glossary and local-link audits until clean.

**Verification:** zero duplicate links, zero footer mismatch, zero shared anchors, zero broken fragments.

**Commit:** `docs: synchronize glossary and claim citations`

---

### Task 31: Mark stale learning records as superseded

**Objective:** Prevent the old KV-cache, sensitivity, 57%, and thinking-budget claims from re-entering future lessons without fabricating new learner mastery.

**Files:**
- Modify: `learning-records/0001-tensors-and-layers.md`
- Modify: `learning-records/0002-how-quantization-works.md`
- Modify: `learning-records/0003-quantization-in-practice.md`

Add an audit revision block to each:

```markdown
## Revision status

Superseded by the 2026 course audit. These notes preserve the original learning state but must not be treated as current evidence. Reassessment is required after the revised lesson.
```

List the specific retracted or uncertain claims. Do not add new “learned” facts or quiz scores until the learner completes the revised material.

**Verification:** search all learning records for the old causal claims and ensure they appear only inside explicit retraction/context.

**Commit:** `docs: mark pre-audit learning records superseded`

---

# Phase G — Automation, browser QA, and release gate

### Task 32: Add continuous structural checks

**Objective:** Run dependency-free course contracts on every change.

**Files:**
- Create: `.github/workflows/course-checks.yml`

Workflow:

```yaml
name: Course checks
on:
  push:
  pull_request:
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python3 -m unittest discover -s tests -v
      - run: python3 scripts/audit_course.py
```

Do not make external URL checks blocking; network failures are nondeterministic. Run them manually before release.

**Verification:** validate YAML locally if available and confirm both commands pass on a clean checkout.

**Commit:** `ci: enforce course structure and evidence contracts`

---

### Task 33: Run desktop, mobile, keyboard, and quiz QA

**Objective:** Verify actual presentation and behavior rather than trusting source inspection.

**Files:**
- Create: `QA.md`

Test at minimum:

- 1280×900 desktop;
- 390×844 mobile;
- index, shortest lesson, longest lesson, Lesson 5, glossary, both reference pages, case study;
- document width versus viewport width;
- all table/card behavior;
- code/formula wrapping;
- top/bottom navigation;
- first-occurrence glossary targets;
- wrong and correct answer on every quiz implementation;
- reset behavior;
- Tab/Shift-Tab focus order and visible focus;
- feedback announcement semantics;
- print preview for reference pages.

Use a local server:

```bash
python3 -m http.server 8765 --bind 127.0.0.1
```

Record viewport, page, result, issue, and fix commit in `QA.md`.

**Verification:** no unexplained horizontal page overflow at 390px; the correct answer is revealed after every wrong selection.

**Commit:** `test: document desktop mobile and interaction QA`

---

### Task 34: Run the final claim and cohesion audit

**Objective:** Prove every review finding has been closed or explicitly accepted.

**Files:** no new production files unless fixes are needed.

Checklist:

- no wrong zero-point/offset math;
- no linear “65,536 values in any range” FP16 claim;
- GGUF expanded correctly;
- no nominal bits presented as universal effective bpw;
- no universal quality percentages or perplexity bands;
- no universal tensor-sensitivity hierarchy;
- no `8-bit = Q8_0` conflation;
- no KV-cache snowball or attention-score cache claim;
- no unsupported thought-duplication or 57% headline;
- no “more thinking never helps,” “creative fuzziness,” or universal sub-Q4 ban;
- one five-step decision procedure everywhere;
- public model/provider names anonymized;
- all quantitative claims have adjacent source/scope;
- index promises are introduced, demonstrated, practiced, assessed, summarized, and referenced;
- old URLs redirect cleanly;
- tests/audits pass;
- repository is clean.

Run:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/audit_course.py
git diff --check
git status --short
```

Expected: all tests pass, audit prints no issues, no whitespace errors, only intentional committed changes.

**Commit:** `fix: close final course audit findings` if any final fixes were required.

---

### Task 35: Final repository review and release

**Objective:** Validate the branch as a complete course, not a collection of individually correct edits.

**Steps:**

1. Review the full diff from `ee8d240`.
2. Re-read in learner order: index → mission → Lessons 1–5 → capstone → references → glossary → resources.
3. Confirm the case-study result is scoped or explicitly inconclusive.
4. Confirm `.gitignore` excludes private benchmark data.
5. Verify GitHub Pages locally through the same relative links used in deployment.
6. Push the branch and open a reviewable PR.
7. Merge only after structural checks and final visual QA pass.

**Release acceptance criteria:**

- [ ] Current Lesson 3 remains visibly marked draft until the full evidence gate passes.
- [ ] Five coherent, short lessons with one win each after the gated rewrite.
- [ ] The final comparison names the exact same-backend 8-bit scheme; `Q8_0` is used only if the experiment actually uses GGUF/llama.cpp `Q8_0`.
- [ ] One canonical five-step decision procedure.
- [ ] Correct weight/activation/cache distinction.
- [ ] Correct symmetric/affine quantization math.
- [ ] Backend-specific format guidance and versioned bpw tables.
- [ ] Controlled or explicitly inconclusive case study.
- [ ] No unsupported universal quality/threshold claims.
- [ ] Applied capstone with worked feedback.
- [ ] Unique glossary anchors and exact footer parity.
- [ ] Shared accessible quiz behavior.
- [ ] Semantic landmarks/tables/navigation.
- [ ] No page-level mobile overflow at 390px.
- [ ] Public anonymization preserved.
- [ ] All automated checks pass.
- [ ] Course repository clean after commit.

---

## 5. Risks and trade-offs

### Benchmark cost

The default 40-trial matrix can take many hours because runs are sequential. This is intentional: parallel Pier runs are unsafe on this machine. If compute constraints force a smaller pilot, the pilot cannot support general recommendations and Lesson 3 remains marked draft. The course must remain publishable without a positive empirical result; “inconclusive” is an acceptable outcome.

### Anonymization versus external reproducibility

Public aliases protect provider/model identity but limit independent reproduction. Mitigation: disclose architecture, parameter class, backend, quantization mode/group size, engine revision, task protocol, and full trial-level metrics while keeping exact identities private.

### Upstream drift

llama.cpp and oMLX format behavior changes. Pin claims to revisions and label numeric tables as examples for named artifacts, not permanent constants.

### Architecture-specific memory

The simple KV formula is not valid for every hybrid/linear-attention model. Keep it explicitly scoped and teach learners to inspect the model configuration before applying it.

### Historical learning records

Rewriting records as if the corrected content had already been learned would be misleading. Supersede and reassess instead.

### URL stability

Renaming Lesson 3 would break deployed links. Keep the old file as a visible redirect with a canonical target and verify it in the local-link audit.

## 6. Files likely to change

**Create:**

- `.gitignore`
- `course.json`
- `scripts/__init__.py`
- `scripts/audit_course.py`
- `scripts/analyze_case_study.py`
- `tests/__init__.py`
- `tests/test_audit_course.py`
- `tests/test_case_study_analysis.py`
- `tests/fixtures/case-study/*`
- `assets/quiz.js`
- `lessons/0003-reading-quantization-formats.html`
- `lessons/0004-measuring-quantization-quality.html`
- `lessons/0005-choosing-and-validating-a-quant.html`
- `reference/quantization-decision-checklist.html`
- `case-study/private/README.md`
- `case-study/private/manifest.example.json`
- `case-study/experiment-design.md`
- `case-study/protocol.md`
- `case-study/data/trials.json`
- `case-study/data/summary.json`
- `case-study/results.html`
- `.github/workflows/course-checks.yml`
- `QA.md`

**Modify:**

- `AGENTS.md`
- `MISSION.md`
- `RESOURCES.md`
- `index.html`
- `mission.html`
- `resources.html`
- `assets/style.css`
- all five lesson pages plus the Lesson 3 compatibility redirect
- `reference/glossary.html`
- `reference/tensors-and-layers.html`
- `reference/quantization-formats.html`
- all three existing learning records

## 7. Verification command set

```bash
python3 -m unittest discover -s tests -v
python3 scripts/audit_course.py
python3 scripts/analyze_case_study.py \
  --manifest case-study/private/manifest.json \
  --trials-out case-study/data/trials.json \
  --summary-out case-study/data/summary.json
git diff --check
git status --short
```

Plan complete. Execute in order: safety rails → governance/assets → canonical references → lessons → paired evidence → final lesson → accessibility/QA → release gate.
