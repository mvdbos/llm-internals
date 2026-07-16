# Preregistered paired quantization protocol

**Protocol version:** 1.1<br>
**Frozen:** 2026-07-15, before new outcome-bearing trials<br>
**Parent design:** [`experiment-design.md`](experiment-design.md)<br>
**Status:** blocked pending all preflight gates

This protocol is subordinate to the parent experiment design. A dated amendment may clarify implementation details before outcome inspection, but may not change the treatment, primary estimands, sample, or exclusion rules in response to results.

## Question and scope

> For the same `dense-27b` checkpoint, `dense-hybrid` architecture, oMLX backend, agent harness, task instances, and inference settings, how does weight-only MLX affine 8-bit quantization with group size 64 change task quality relative to bf16 weights?

This study supports conclusions only for the tested checkpoint revision, artifacts, engine/backend, hardware, task sample, harness, and settings.

## Conditions

| Alias | Treatment | Public wording |
|---|---|---|
| `bf16` | bf16 weights | “bf16 weights” |
| `mlx-affine-int8-g64` | Weight-only MLX affine quantization, 8-bit codes, group size 64, plus artifact-declared exceptions | “MLX affine 8-bit, group size 64” |

Both conditions use the same pinned oMLX build. The treatment condition is not GGUF `Q8_0` and is not current oMLX oQ8. Only weight representation may differ.

## Immutable provenance gate

Before smoke execution, the ignored manifest must prove that both artifacts resolve to the same immutable source-checkpoint and tokenizer revision. Matching architecture and tokenizer hashes are necessary but not sufficient. Failure to prove exact source parity stops the experiment. The manifest must also include a SHA-256 digest of the API-effective settings snapshot, `parity_status: verified`, and `alias_map_status: verified` before the analyzer can return `ready`.

Public artifacts use only approved lowercase slug aliases. Exact model/provider IDs, source paths, task IDs, and provenance handles remain in complete private condition/task maps inside the ignored manifest. The analyzer validates map completeness and same-source parity but never serializes private map values.

## Sample and matrix

The sample was selected before new outcomes based on language/task-type coverage and environment evidence:

| Alias | Language | Type | Preflight note |
|---|---|---|---|
| `task-01` | Python | Feature request | Existing environment evidence |
| `task-02` | Python | Feature request | Existing environment evidence |
| `task-03` | Go | Bugfix | No local history; paired smoke required |
| `task-04` | Go | Feature request | Existing environment evidence |
| `task-05` | TypeScript | Bugfix | No local history; paired smoke required |

The full matrix is:

```text
5 exact tasks × 4 repetitions × 2 conditions = 40 trials
```

All trials run sequentially. Tasks execute in alias order. Condition order alternates within each task/repetition pair:

- odd repetition: `bf16`, then `mlx-affine-int8-g64`;
- even repetition: `mlx-affine-int8-g64`, then `bf16`.

Exact task IDs are resolved from the benchmark's manifest indices, never filesystem order, and stored only in the ignored manifest.

## Frozen execution settings

| Setting | Frozen value |
|---|---|
| Engine | oMLX 0.5.1 build 1878 |
| Runner | Pier 0.3.0 |
| Agent adapter/harness | Same pinned private revision and configuration |
| Thinking enabled | `true` |
| `preserve_thinking` | `true` |
| Thinking budget | Disabled; no active token budget |
| Maximum output tokens | 32,768 |
| Configured context limit | 221,184 |
| Native context metadata | 262,144; not the trial limit |
| Temperature | 0.6 |
| Top-p | 0.95 |
| Top-k | 20 |
| Repetition penalty | 1.0 |
| KV quantization | Disabled |
| Speculative prefill / dFlash | Disabled |
| Draft assistance | Identical private helper and settings in both conditions |
| Tokenizer/chat template | Identical files/hashes/template |
| Tools and prompt | Identical system/task prompt, tool policy, and repository environment |
| Stop policy | Identical step limit, wall timeout, stop tokens, and termination policy; exact private values snapshotted before smoke |
| Verifier | Identical task-specific verifier revision and extraction |
| Scheduling | Exactly one benchmark trial at a time |

If deterministic seed control is unsupported, that fact is recorded; repetitions remain stochastic and no deterministic-seed claim is made. API-effective state is snapshotted privately immediately before smoke and full execution.

## Outcomes

### Primary

- paired F2P difference (`mlx-affine-int8-g64 − bf16`);
- paired P2P difference (`mlx-affine-int8-g64 − bf16`).

### Guardrail

- paired reward/pass outcome, including both-pass, bf16-only, affine-8-bit-only, and neither-pass counts.

### Secondary

- steps;
- input/output tokens;
- elapsed time;
- peak context;
- artifact, loaded, and peak memory when collected under one boundary.

Quality is analyzed first. Efficiency is never interpreted as an improvement when quality is lower without explicitly presenting that trade-off. No causal KV-cache or thought-duplication outcome is registered.

No non-inferiority margin is declared. The study reports estimates and intervals rather than an equivalence verdict.

## Attempt, verifier, and attrition rules

Every attempt has a positive integer `attempt`, a boolean `selected_for_analysis`, and one `attempt_status`:

1. `completed` — valid model/agent attempt reached normal termination;
2. `model_agent_timeout` — valid outcome, retained without outcome-motivated rerun;
3. `model_agent_failure` — valid outcome when infrastructure functioned;
4. `environment_harness_failure` — no valid model/agent attempt.

Verifier state is recorded separately as `complete`, `missing`, or `verifier_only_failure`. A verifier failure does not rewrite the attempt's model/agent status.

- Environment/harness failures receive at most one documented, condition-neutral repair/rerun.
- Verifier-only failures rerun the verifier without inference when the original artifact is intact; otherwise they use the same one-rerun infrastructure rule.
- Model/agent timeouts and failures remain outcomes.
- Original failures remain in the attrition table after a successful rerun.
- Every planned task × repetition × condition cell has exactly one selected attempt. An infrastructure failure cannot be selected; a documented authorized rerun can be selected while the original remains unselected in attrition.
- No run is excluded for score, steps, token use, latency, repetition, or trajectory appearance.
- Missing F2P/P2P is never imputed.
- Discovered artifacts, valid attempts, verifier-covered attempts, and successful completions are reported separately.

## Metric schema

- F2P and P2P are numbers in `[0, 1]` and each carries integer numerator/denominator fields. Denominators are positive, numerators lie between zero and the denominator, and the ratio must equal the reported score.
- Reward is `0`, `1`, or missing. It is paired independently as a guardrail and never determines whether a verifier-covered F2P/P2P pair exists.
- Steps, input tokens, output tokens, elapsed seconds, and peak context tokens are non-negative when present.
- Primary evidence requires a selected valid model/agent attempt, `verifier_status: complete`, and complete F2P/P2P score/count fields in both conditions.

## Task replacement rule

A task is replaceable only when paired smoke demonstrates a persistent environment/verifier defect after the one permitted repair/rerun and primary metrics cannot be collected. Replacement occurs before any full-matrix outcome is inspected, preserves coverage where possible, is documented in a dated amendment, and must itself pass paired smoke. Model performance cannot influence replacement.

## Analysis

1. Require unique attempt keys `(checkpoint, architecture, engine, scheme, task alias, repetition, condition, attempt)`.
2. Require explicit `baseline_condition: bf16` and `treatment_condition: mlx-affine-int8-g64`; never infer delta direction from JSON object order.
3. Validate the frozen five-task × four-repeat × two-condition matrix, sequential schedule, and exactly one selected attempt per cell.
4. Pair exact task alias and repetition only.
5. Compute F2P/P2P paired differences and reward pair states independently, with treatment minus baseline sign.
6. Report every pair and every task-level mean.
7. Aggregate by equal-weight mean of the five task-level means.
8. Use task-clustered paired bootstrap uncertainty:
   - seed `20260715`;
   - 10,000 replicates;
   - resample tasks with replacement and retain their repetitions;
   - report 2.5th and 97.5th percentiles as a descriptive 95% interval.
9. Report full secondary-outcome distributions by condition before any successful-only view, plus paired task means and intervals.
10. Show every attempt in attrition and primary-metric completeness by condition and task.
11. Return `ready` only when provenance, aliases, frozen shape, selected-attempt, verifier, primary, reward-guardrail, and metric-count gates all pass.

The public analyzer is:

```bash
python3 scripts/analyze_case_study.py \
  --manifest case-study/private/manifest.json \
  --trials-out case-study/data/trials.json \
  --summary-out case-study/data/summary.json
```

## Smoke and full-run gates

- [ ] Exact immutable checkpoint parity proven.
- [ ] Private manifest and alias map validated.
- [ ] Analyzer and refusal-path tests pass.
- [ ] Active API settings snapshotted.
- [ ] Stale benchmark container/result state resolved without touching unrelated services.
- [ ] One paired smoke trial completes with verifier coverage.
- [ ] No-history task environments pass smoke or preregistered replacements are amended and smoked.
- [ ] Frozen sequential schedule contains exactly 40 unique cells.

No full run or recommendation is permitted until every box is checked.

## Amendments

**2026-07-16 — Protocol 1.1.** Clarified the fail-closed manifest/analyzer schema: explicit baseline/treatment roles, immutable provenance evidence, safe alias maps, attempt IDs and selection, separate verifier state, numerator/denominator fields, reward independence, task-clustered intervals, and secondary distributions. No treatment, task, repeat, metric, or outcome-dependent rule changed; no new trial outcomes had been collected.

Any future amendment must include date, rationale, affected fields, and confirmation that no relevant outcomes had been inspected.
