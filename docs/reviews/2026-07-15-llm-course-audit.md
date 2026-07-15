# LLM Internals course review

**Baseline:** repository commit `ee8d240`  
**Implementation plan:** [`../plans/2026-07-15-apply-llm-course-review-improvements.md`](../plans/2026-07-15-apply-llm-course-review-improvements.md)

## Executive verdict

The course has a strong mission, an approachable visual system, and several effective teaching devices—especially the concrete encode/decode example in Lesson 2. The current version is **not yet reliable enough as a decision guide**, however. The main blockers are evidentiary rather than cosmetic:

1. The bf16-versus-8-bit case study is an unpaired, unbalanced observational sample but is presented as a controlled causal result.
2. A GGUF/llama.cpp framework is applied to an MLX/oMLX 8-bit artifact as though it were `Q8_0`; these are different formats.
3. The “KV-cache snowball” is both mechanistically inaccurate and mismatched to the hybrid architecture used in the case study.
4. Several universal numbers and recommendations—effective bits, quality percentages, perplexity deltas, layer sensitivity, memory thresholds, task thresholds—are unsupported or materially oversimplified.

Recommendation: treat the live course as a draft. Correct the evidence and backend distinctions before polishing the presentation further.

## Scope and checks

Reviewed:

- `index.html`, `mission.html`, `resources.html`
- all three lessons
- all three reference pages and the glossary
- all three learning records
- `assets/style.css`, `AGENTS.md`, `MISSION.md`, `RESOURCES.md`, `NOTES.md`

Checks performed:

- desktop render at 1280×900 and narrow render at 390×844
- local link and fragment audit: **0 broken local targets**
- HTML parser pass: completed
- glossary/terms-footer consistency audit
- wrong-answer quiz execution in a browser
- current local case-study artifact analysis
- claim verification against current llama.cpp source/docs, oMLX docs, and quantization studies
- repository remained clean at `ee8d240`; no course files were edited

## 1. Legibility and story flow

### What works

- The 38rem text measure, generous line height, high contrast, and restrained callouts make normal prose comfortable on desktop.
- The landing page is clean and gives the course a clear practical promise.
- Lesson 1 starts at an accessible level and ties memory arithmetic to the mission quickly.
- Lesson 2’s encode → decode → compare example is the strongest instructional unit in the course. It makes quantization error concrete rather than magical.
- Framework-before-case-study is the right macro-order for Lesson 3.
- All local links resolve.

### Main story problem: Lesson 2 does too many jobs

Lesson 2 is 2,118 words, 9 tables, 4 code blocks, and roughly 10.6 minutes of text at 200 wpm before interaction. The index promises ~7 minutes; the page says ~10. It currently teaches:

- scalar quantization math
- block size trade-offs
- GGUF suffixes
- K/IQ implementation claims
- layer sensitivity
- perplexity
- task-completion evaluation
- agentic failure mechanisms
- a decision framework

That is several lessons, not one. Lesson 3 then repeats task sensitivity, memory, model-size trade-offs, benchmarking, and decision tables. The narrative advances strongly through the first half of Lesson 2, then stalls in repetition.

**Fix:** separate mechanism, format, evaluation, and selection.

Recommended arc:

1. **From text to runtime state** — tokens, IDs, embeddings, hidden states, learned weights, activations, cache.
2. **Quantization mechanics** — symmetric vs affine, scale/offset, groups, effective bits per weight, one round trip.
3. **Reading format labels** — GGUF/llama.cpp in one section; MLX/oMLX in another; never equate their labels.
4. **Measuring quality** — perplexity plus downstream/task metrics, latency, memory, and uncertainty.
5. **Choosing and validating a quant** — one decision procedure plus a properly controlled case study.

### Prerequisite gaps in Lesson 1

`lessons/0001-tensors-and-layers.html:55–101` jumps from “weights are knowledge” to “words → embeddings → transformer → next word” without teaching:

- text is tokenized before embedding
- embeddings begin as context-independent token vectors; contextual representations emerge through later blocks
- weights are persistent learned tensors, while activations/hidden states and caches are runtime tensors
- most local quant files are weight-only; KV-cache quantization is a separate choice
- the output path is logits → probabilities/decoding → next token

This missing distinction directly enables the later KV-cache confusion.

**Fix:** add a compact three-state table: learned weights, runtime activations, runtime cache. Then add one matrix-vector example and a full text → token → ID → embedding → hidden state → logits → token round trip.

### Mobile legibility

The prose remains readable at 390 px, but the tables do not. Four- and five-column tables compress into narrow word stacks, particularly in Lessons 2 and 3. Long diagrams and procedural `pre` blocks require horizontal scrolling without an affordance; the Lesson 1 transformer pipeline is visibly clipped.

**Fix:**

- wrap data tables in an overflow container with an explicit scroll hint, or convert high-priority tables to stacked cards below ~640 px
- give tables a sensible `min-width`; do not force every column into 342 px of content width
- convert decision procedures and benchmark methods from code blocks to semantic ordered lists/cards
- replace the long ASCII pipeline with a wrapping diagram
- add top breadcrumb navigation and symmetric Previous / Home / Next controls

### Quiz feedback is broken

All three lessons say an incorrect answer will reveal the correct option in green. The script only adds `.incorrect` to the clicked button and disables every option; it never marks the correct button. Browser execution confirmed the correct answer remains unmarked. Feedback is also only “Correct” / “Not quite,” so it tests recognition without teaching the misconception.

Answer lengths range from 3 to 12 words, which can cue the answer and violates the equal-length course convention.

**Fix:** move duplicated logic into `assets/quiz.js`; reveal and explain the correct answer; add retry/reset intentionally; use `aria-live`; maintain visible focus; equalize option length.

### Exercises stop at recognition

The nine quiz questions are short multiple-choice checks. They mostly test recall of labels or stated recommendations; none asks the learner to calculate a memory budget, identify a quantization scheme from an exact config, select an evaluation metric, or justify a Pareto choice. Lesson 3's practical exercise has no worked answer or rubric.

**Fix:** retain short retrieval checks, then add one capstone worksheet: given a backend, model configuration, available memory, context length, and workload, calculate fit, shortlist two artifacts, choose metrics, and explain what evidence would settle the choice.

### Structural accessibility needs a systematic pass

Across the course there are 26 tables, but no `<caption>`, `<thead>`, or `<tbody>` elements; all 76 `<th>` cells lack `scope`. All 36 quiz buttons omit an explicit `type`, and none of the HTML pages has a `<main>` landmark.

**Fix:** add semantic landmarks and table structure, explicit button types, fieldset/legend grouping where appropriate, and verify keyboard and screen-reader behavior after the visual fixes.

## 2. Claim correctness

### P0 — Case study does not support its conclusion

Affected:

- `lessons/0002-how-quantization-works.html:176–215`
- `lessons/0003-quantization-in-practice.html:103–134`
- `reference/quantization-formats.html:75–83`
- `learning-records/0002-how-quantization-works.md:16–19`
- `learning-records/0003-quantization-in-practice.md:8–19`

The course says the same work was run at bf16 and 8-bit, producing 74 versus 116 steps, and attributes the delta to measured thought duplication.

The artifacts do not establish that:

- The aggregation behind the course's `n=29` bf16 number mixed **two different model architectures**: a 27B dense bf16 model and a 35B-A3B MoE bf16 model. Current top-level result metadata contains 8 dense-27B bf16 files, 20 35B-A3B bf16 files, and 7 dense-27B 8-bit files. This is not a same-model comparison.
- Restricting the analysis to the dense 27B model and excluding one obvious two-step bf16 failure leaves seven nontrivial runs in each precision group. Their descriptive means are 98.4 versus 115.6 steps—a 17.4% difference, not the published 57%—but the task instances and repeat counts remain unmatched, so even this does not identify a causal quantization effect.
- Verifier results exist for only 7 of the 8 dense-27B bf16 artifacts and 5 of the 7 8-bit artifacts; no inspected artifact in either exact-model group has full binary reward 1.
- No `unique_thoughts` or thought-duplication metric exists in the JSON artifacts.
- Task-level results are mixed; aggregate step means remain confounded by task selection, failed/short runs, repetition, and outcome quality.

“Tasks completed: n=29 / n=7” is especially misleading: it mixes model architectures and counts artifacts/trajectories rather than completed tasks.

**Correct treatment:** label the existing numbers “exploratory, unmatched observations” or remove them. They cannot validate causality. Re-run a paired experiment before using them in a lesson or quiz.

### P0 — `8-bit` is not `Q8_0`

Affected:

- `lessons/0002-how-quantization-works.html:183–189`
- `lessons/0003-quantization-in-practice.html:103–115`
- `reference/quantization-formats.html:75–83`

The benchmark artifact is an MLX model. Its published config uses 8-bit **affine** quantization with group size 64. llama.cpp `Q8_0` is a different GGML/GGUF scheme. The current course moves from one to the other without qualification.

**Fix:** always state backend, quantized target, mode, group size, calibration/importance recipe, engine/version, and whether KV/activations are quantized. Use `8-bit MLX affine, group 64` for this artifact—not `Q8_0`.

### P0 — KV-cache snowball is an invented causal mechanism

Affected:

- `lessons/0002-how-quantization-works.html:194–215`
- `lessons/0003-quantization-in-practice.html:117–128`
- `learning-records/0003-quantization-in-practice.md:12,19`

The explanation says an attention score is computed, then its K/V vectors are stored, and each cache entry becomes progressively noisier. The order is wrong: K and V projections are computed before attention scores; attention scores themselves are not what the KV cache stores. Old cache entries are not repeatedly rewritten and made noisier. Weight quantization and KV-cache quantization are separate mechanisms.

The architecture used in the cited artifact also has 48 linear-attention layers and only 16 full-attention layers, so a standard-transformer KV-cache story is a poor model of the actual case.

Sequence-level divergence may exist, but the cited literature describes the underlying causal mechanism as incomplete or speculative. Present it as an open hypothesis, not established fact.

### Quantization math mixes incompatible schemes

`lessons/0002-how-quantization-works.html:34–47` presents one formula but mixes two parameterizations:

- affine form: `x_hat = scale × (q - integer_zero_point)`
- offset/min form: `x_hat = scale × q + stored_min`

It calls the float minimum an integer zero point and says both scale and zero point are always FP16. That is not true across GGML types: some are symmetric and have no offset; K-quants use hierarchical metadata, including quantized sub-scales/mins.

**Fix:** teach symmetric and affine quantization separately, then state that actual formats choose different metadata layouts.

### FP16 and GGUF are defined incorrectly

Affected:

- `lessons/0002-how-quantization-works.html:18–27`
- `reference/glossary.html:147–148`

FP16 has 65,536 bit patterns, not 65,536 uniformly spaced finite values “in any range.” Its spacing is nonuniform, its exponent fixes the representable range, and its bit patterns include signed zeros, infinities, and NaNs. The ruler analogy should therefore compare blockwise Q4 reconstruction levels with FP16's nonuniform floating-point precision rather than presenting both as linear grids.

The glossary expands GGUF as “GPT-Generated Unified Format.” llama.cpp's canonical `gguf-py` documentation expands it as **GGML Universal File**.

**Fix:** correct both definitions and add canonical citations beside them.

### Format tables use nominal bits as effective bits

Affected:

- `lessons/0002-how-quantization-works.html:108–130`
- `reference/quantization-formats.html:16–29,43–73`
- `reference/glossary.html:177–179,241–245`

Current llama.cpp documentation for one 8B reference model reports approximately:

- `Q8_0`: 8.5008 bpw
- `Q6_K`: 6.5633 bpw
- `Q4_K_M`: 4.8944 bpw
- `IQ4_XS`: 4.4597 bpw

The number in the label is a nominal family label, not generally the final file-average bpw. `_M` recipes are architecture- and tensor-aware mixtures; “K means different block sizes per layer type” and “Q4_K_M = attention 6-bit, FFN 4-bit, embeddings 6-bit” are not valid universal decoders.

**Fix:** distinguish nominal label, underlying tensor type, mixture recipe, and measured file-average bpw. Pin tables to an upstream commit/model and label them examples, not constants.

### Quality percentages and universal perplexity ranges are unsupported

Affected:

- `reference/quantization-formats.html:17–28`
- `lessons/0002-how-quantization-works.html:109–118,159–192`
- `reference/glossary.html:233–234`

“99% quality,” “95% quality,” and universal perplexity deltas have no defined metric or cited dataset. Perplexity is useful but not a task label: it is not specifically “the signal for chat/writing,” and one-shot autoregressive generation can still propagate errors. Recent controlled evaluations show non-monotonic, model- and task-specific behavior; schemes with similar perplexity can differ on reasoning or instruction following.

**Fix:** remove universal percentages. Show one cited, model-specific table with separate columns for perplexity and downstream metrics, then teach that both are evidence—not interchangeable quality scores.

### Layer sensitivity and “thinking” language are too categorical

Affected:

- `lessons/0002-how-quantization-works.html:135–144`
- `reference/glossary.html:121–134,177–179,208–209`
- `reference/tensors-and-layers.html:47–59`

The fixed hierarchy “embedding/output > attention > FFN” is not a universal rule. Sensitivity varies by tensor, layer, model architecture, method, and calibration data. Current llama.cpp mixture logic gives special handling to output, token embeddings, attention V, FFN-down, architecture, layer position, GQA/MoE, and shape fallbacks. The reference also contradicts itself: FFNs are called least sensitive in one place but said to “dominate precision sensitivity” elsewhere.

Calling the FFN or transformer blocks “the thinking part” should be framed as analogy only; attention, MLPs, residual paths, normalization, sampling, and external context all contribute to behavior.

### Absolute guidance conflicts with evidence

Affected:

- `lessons/0003-quantization-in-practice.html:65–74,130–161`
- `lessons/0002-how-quantization-works.html:219–242`

Examples:

- “Thinking longer does not work” is too strong. Controlled reasoning studies find that longer reasoning can improve quantized models over a range, though gains and optimal budgets differ.
- “Below Q4 is unsuitable” is not universal; some 3-bit formats retain useful performance on some models/tasks.
- “Creative fuzziness can add variety” is not a principled creativity control.
- “Bigger models tolerate rougher quants” has supporting examples, but the specific 35B-Q4 versus 27B-Q8 claim is untested here and must be a hypothesis.
- RAM multipliers, 70% headroom, 10/30% step thresholds, and fixed 1–2 GB/2–4 GB overhead are uncited heuristics with ambiguous units.

**Fix:** replace absolutes with a backend-aware shortlist and a validation procedure. Teach a KV-memory formula instead of a fixed allowance.

## 3. Guidance and terminology cohesion

### One course currently contains three incompatible decision logics

1. “Q4_K_M is the community sweet spot.”
2. A RAM-multiplier ladder in Lesson 2.
3. A task-type decision matrix in Lesson 3.

These compete rather than compose. Use one ordered procedure everywhere:

1. Identify backend and what is quantized.
2. Calculate model + cache + runtime headroom.
3. Shortlist formats that fit.
4. Evaluate the exact workload with paired trials.
5. Choose the best quality/latency/memory Pareto point.

The index, lessons, quiz, takeaway, and reference card should all use those same five steps.

### Mission and evidence do not match

`mission.html:23–25` says the course is motivated by an 8-bit-versus-4-bit benchmark, but the presented case study compares bf16 with an unspecified MLX 8-bit artifact. The public pages also retain first-person setup details, named runtimes, and “your benchmarks” language in the core teaching path.

**Fix:** make the public mission a universal learner outcome; state exactly which comparison the evidence contains; move environment-specific details into a clearly labeled, anonymized, sourced case study.

### Glossary contract is not being met

Mechanical audit found:

- 16 letter anchors are shared by multiple glossary entries; links land at a letter section rather than the requested definition.
- The A–Z navigation omits **V** even though Vector and Vocabulary entries exist.
- Lesson 1 links Embedding Layer, Output Layer, and Transformer twice.
- Lesson 2 links FP16 twice.
- Terms footers do not equal the inline glossary-link set; several footer-only and inline-only terms exist.

**Fix:** give every `<dt>` a stable term slug (`#weight`, `#kv-cache`, etc.), update AGENTS.md, repair first-occurrence links, and make the audit compare canonical targets.

### Source taxonomy is backwards

`RESOURCES.md:5–26` labels commercial blogs and a Medium post “primary sources,” while official code/docs are under “Reference / canonical.” Quantitative claims in lessons have no adjacent citations.

**Fix:** classify as:

- Primary/canonical: source code, official format docs, model configs/cards, original papers, raw experiment artifacts.
- Secondary explainers: 3Blue1Brown, Raschka, Illustrated Transformer, blogs.
- Community/wisdom: Reddit and comments.

Pin implementation claims to a version/commit and cite tables directly.

### Learning records will reintroduce fixed errors

Even if lessons are corrected, the learning records currently preserve the KV-snowball, universal sensitivity hierarchy, 57% causal claim, and thinking-budget absolute as mastered knowledge. Update them in the same change set as the lessons and references.

## 4. Actionable improvement plan

| Priority | Action | Files | Definition of done |
|---|---|---|---|
| P0 | Quarantine unsupported claims | Lessons 2–3, both reference pages, glossary, learning records | No causal 57%/duplication claim; current data labeled exploratory or removed; no quiz tests it as fact |
| P0 | Separate GGUF from MLX/oMLX | Lessons 2–3, quant reference, glossary | Every format example names backend, scheme, group size/effective bpw, and quantized target; MLX 8-bit is never called Q8_0 |
| P0 | Replace KV-cache mechanism | Lessons 1–3, glossary, records | Weights/activations/cache are distinguished; standard KV operation is correct; architecture-specific behavior is labeled; causal mechanism remains hypothesis unless measured |
| P0 | Correct tables and math | Lesson 2, quant reference | Symmetric and affine formulas are correct; effective bpw includes metadata; no undefined “quality %”; version/model/source shown on every numeric table |
| P0 | Re-run the case study properly | New `case-study/` or linked analysis | Same exact task instances under both configs; identical checkpoint/harness/template/sampling/context; ≥3 repetitions where stochastic; F2P/P2P and success primary; steps/tokens/latency secondary; paired deltas + uncertainty; raw artifacts linked |
| P1 | Split the instructional arc into five lessons | `lessons/`, `index.html` | Each lesson has one win, one worked example, one retrieval check, one cited source; no repeated decision matrix |
| P1 | Install one five-step decision procedure | Lesson 5, index, quant reference, quiz | Backend → memory → shortlist → paired evaluation → Pareto choice appears consistently everywhere |
| P1 | Add an applied capstone | Final lesson, quiz/worksheet assets | Learner calculates fit, identifies the exact scheme, chooses metrics and two candidates, and receives a worked answer/rubric |
| P1 | Add real memory budgeting | Lessons 1 and 5, references | Effective weight bpw formula plus KV-cache formula and runtime headroom; fixed 70%/2–4 GB rules demoted to labeled examples |
| P2 | Make narrow layouts usable | `assets/style.css`, all lessons | No clipped diagram; wide tables scroll with affordance or become cards; procedural content is semantic HTML, not horizontally scrolling code |
| P2 | Repair quizzes/accessibility | new `assets/quiz.js`, lessons, CSS | Wrong answer reveals and explains correct answer; retry policy clear; `aria-live`, focus styles, semantic grouping; balanced options |
| P2 | Repair glossary/navigation | glossary, AGENTS.md, lessons, CSS | Unique term IDs; exact footer/inline target match; Home/Previous/Next at top and bottom; audit passes except reviewed homonyms |
| P3 | Upgrade source governance and CI | resources pages, `scripts/`, optional CI | Correct source taxonomy; inline citations; pinned commits/versions; automated HTML/local-link/glossary/quiz checks |

### Recommended execution order

1. **Evidence correction pass** — remove or qualify P0 claims across every duplicated file.
2. **Narrative refactor** — split lessons and add the missing runtime-state foundation.
3. **Controlled case-study rebuild** — only then restore empirical recommendations.
4. **Responsive/accessibility pass** — tables, diagrams, quizzes, navigation, glossary.
5. **Final consistency audit** — promises, claims, references, records, mobile render, quiz execution, clean repository.

## Bottom line

The course is visually promising and pedagogically well-intentioned, but it currently teaches a compelling causal story that the evidence does not establish. The highest-value improvement is not more polish; it is to separate backend-specific mechanisms, rebuild the case study as a paired evaluation, and reduce every recommendation to one cited, reproducible decision procedure.

## Sources used for verification

- llama.cpp quantize documentation (reviewed at `aff6eb6e7503538fec1532dec2f584bc7a4a4e4d`): https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md
- llama.cpp tensor-type selection (same revision): https://github.com/ggml-org/llama.cpp/blob/master/src/llama-quant.cpp
- GGUF specification: https://github.com/ggml-org/ggml/blob/master/docs/gguf.md
- Canonical GGUF acronym/package documentation: https://github.com/ggml-org/llama.cpp/blob/master/gguf-py/README.md
- NVIDIA precision-format overview: https://docs.nvidia.com/deeplearning/tensorrt/latest/inference-library/accuracy-considerations.html
- oMLX quantization documentation: https://github.com/jundot/omlx/blob/main/docs/oQ_Quantization.md
- Unified llama.cpp quantization evaluation: https://arxiv.org/abs/2601.14277
- Quantized reasoning models study: https://arxiv.org/abs/2504.04823
- ACL 2024 quantization evaluation: https://aclanthology.org/2024.findings-acl.726/
