# Preregistered paired quantization protocol

**Protocol version:** 1.0<br>
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

Before smoke execution, the ignored manifest must prove that both artifacts resolve to the same immutable source-checkpoint and tokenizer revision. Matching architecture and tokenizer hashes are necessary but not sufficient. Failure to prove exact source parity stops the experiment.

Public artifacts use only aliases. Exact model/provider IDs, source paths, task IDs, and provenance handles remain in the ignored manifest.

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

## Attempt and attrition rules

Every expected cell is classified as one of:

1. `completed` — valid model/agent attempt reached normal termination;
2. `model_agent_timeout` — valid outcome, retained without outcome-motivated rerun;
3. `model_agent_failure` — valid outcome when infrastructure functioned;
4. `environment_harness_failure` — no valid model/agent attempt;
5. `verifier_only_failure` — attempt exists but verifier failed independently.

- Environment/harness failures receive at most one documented, condition-neutral repair/rerun.
- Verifier-only failures rerun the verifier without inference when the original artifact is intact; otherwise they use the same one-rerun infrastructure rule.
- Model/agent timeouts and failures remain outcomes.
- Original failures remain in the attrition table after a successful rerun.
- No run is excluded for score, steps, token use, latency, repetition, or trajectory appearance.
- Missing F2P/P2P is never imputed.
- Discovered artifacts, valid attempts, verifier-covered attempts, and successful completions are reported separately.

## Task replacement rule

A task is replaceable only when paired smoke demonstrates a persistent environment/verifier defect after the one permitted repair/rerun and primary metrics cannot be collected. Replacement occurs before any full-matrix outcome is inspected, preserves coverage where possible, is documented in a dated amendment, and must itself pass paired smoke. Model performance cannot influence replacement.

## Analysis

1. Require unique keys `(checkpoint, architecture, engine, scheme, task alias, repetition, condition)`.
2. Validate the expected 40-cell matrix.
3. Pair exact task alias and repetition only.
4. Compute F2P/P2P paired differences and reward pair states first.
5. Report every pair and every task-level mean.
6. Aggregate by equal-weight mean of the five task-level means.
7. Use task-clustered paired bootstrap uncertainty:
   - seed `20260715`;
   - 10,000 replicates;
   - resample tasks with replacement and retain their repetitions;
   - report 2.5th and 97.5th percentiles as a descriptive 95% interval.
8. Report full secondary-outcome distributions before any successful-only view.
9. Show attrition and primary-metric completeness by condition and task.
10. Block a causal/universal headline whenever the primary matrix is incomplete.

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

None. Any future amendment must include date, rationale, affected fields, and confirmation that no relevant outcomes had been inspected.
