# Experiment design: same-backend bf16 versus MLX affine 8-bit

**Frozen:** 2026-07-15, before new outcome-bearing runs<br>
**Public checkpoint alias:** `dense-27b`<br>
**Public architecture alias:** `dense-hybrid`<br>
**Status:** designed; execution is prohibited until every preflight gate below passes

## 1. Scientific question

> For the same checkpoint, architecture, inference engine/backend, agent harness, task instances, and inference settings, how does weight-only MLX affine 8-bit quantization with group size 64 change task quality relative to bf16 weights?

The intended contrast is a **same-backend weight-precision comparison**. It is not a comparison of unrelated “8-bit” formats or inference engines.

## 2. Conditions and the meaning of “8-bit”

| Public condition alias | Weight representation | Quantized target | Engine/backend |
|---|---|---|---|
| `bf16` | bf16 weights | None | Same pinned oMLX build |
| `mlx-affine-int8-g64` | MLX affine mode, 8-bit codes, group size 64 | Weights only, subject to artifact-declared exceptions | Same pinned oMLX build |

The second condition must be called **MLX affine 8-bit, group size 64** in public material. It must never be called GGUF `Q8_0`, current oMLX `oQ8`, or an undefined `Q8`.

The installed artifacts currently provide strong parity evidence:

- architecture/configuration matches after quantization metadata is removed;
- tokenizer, tokenizer configuration, and generation configuration hashes match;
- the quantized artifact declares affine mode, 8 bits, and group size 64;
- indexed weight shards are complete in both conditions;
- the quantized tensor index contains expected scale and bias auxiliaries.

### Mandatory checkpoint-provenance gate

The inspected metadata does **not yet record the exact upstream snapshot revision clearly enough to claim exact-checkpoint identity**. Before the smoke pair, the ignored private manifest must capture immutable source provenance for both artifacts and prove that it resolves to the same source revision. If this cannot be established, the experiment stops; “same checkpoint family” is not sufficient for a causal precision contrast.

## 3. Estimands

All differences use `mlx-affine-int8-g64 − bf16`, paired by exact task alias and repetition.

### Primary estimands

1. Paired difference in F2P score.
2. Paired difference in P2P score.

Report each task × repetition pair, task-level means, and the aggregate estimate. Neither metric may be replaced by artifact count, job status, or an unverified completion label.

### Guardrail outcome

- Paired binary reward/pass outcome, including the four pair states: both pass, bf16-only pass, affine-8-bit-only pass, neither passes.

### Secondary estimands

- steps;
- input tokens;
- output tokens;
- elapsed time;
- peak context tokens;
- artifact size, loaded memory, and peak runtime memory if measured with a common boundary.

Efficiency is interpreted jointly with quality. Full-outcome summaries come first; successful-only efficiency summaries may be shown only as explicitly conditional secondary views.

### Excluded estimands

- No causal KV-cache claim: cache precision and handling are held fixed.
- No “thought duplication” metric or headline: no validated detector is preregistered.
- No universal quality ranking beyond this checkpoint, engine, artifact pair, task sample, and settings.

### Non-inferiority decision

No non-inferiority margin is declared because no defensible workload-specific margin was available before execution. The analysis will report paired estimates and intervals without a binary equivalence/non-inferiority claim.

## 4. Sample frozen before results

The full matrix uses five task instances, four repetitions, and two conditions:

```text
5 tasks × 4 repetitions × 2 conditions = 40 sequential trials
```

Exact task IDs and manifest indices are kept in the ignored private manifest. Public data uses only these aliases:

| Task alias | Language | Task type | Selection reason |
|---|---|---|---|
| `task-01` | Python | Feature request | Adds a Python feature task with usable prior environment evidence |
| `task-02` | Python | Feature request | Adds a second independent Python repository with usable environment evidence |
| `task-03` | Go | Bugfix | Adds language and bugfix coverage; no prior local run, so smoke validation is mandatory |
| `task-04` | Go | Feature request | Adds Go feature work with usable prior environment evidence |
| `task-05` | TypeScript | Bugfix | Adds a third language and bugfix coverage; no prior local run, so smoke validation is mandatory |

Selection was based on language/task-type coverage and environment evidence, not observed condition scores. Known candidates with prior package-runner, verifier-timeout, or stale-container failures were excluded before new outcomes were inspected.

### Replacement rule

A task may be replaced only when the smoke/preflight demonstrates an environment or verifier defect that persists after the single preregistered repair/rerun path and prevents primary-metric collection. Any replacement must:

1. be chosen before any full-matrix outcome for either condition is inspected;
2. preserve language/task-type coverage where possible;
3. be added by a dated protocol amendment with its reason;
4. receive its own successful paired smoke run;
5. never be chosen using model quality, steps, tokens, or latency.

If no eligible replacement is preregistered, the full study does not start.

## 5. Controlled variables

Only declared weight representation may differ.

| Variable | Frozen value or rule |
|---|---|
| Checkpoint | Public alias `dense-27b`; exact identical immutable source revision required privately before smoke |
| Architecture | Public alias `dense-hybrid`; sanitized configurations must match except quantization metadata |
| Engine | oMLX 0.5.1, build 1878, both conditions |
| Benchmark runner | Pier 0.3.0, both conditions |
| Agent adapter/harness | Identical pinned revision and configuration |
| Tokenizer/chat template | Identical files/hashes and template |
| Thinking | `enable_thinking=true`; `preserve_thinking=true` |
| Thinking budget | Disabled; no active thinking-token budget |
| Maximum output tokens | 32,768 |
| Configured context limit | 221,184 tokens |
| Native context metadata | 262,144 tokens; not used as the configured trial limit |
| Temperature | 0.6 |
| Top-p | 0.95 |
| Top-k | 20 |
| Repetition penalty | 1.0 |
| Seed | Record engine support privately. If unsupported, repetitions remain stochastic and no deterministic-seed claim is made |
| Stopping rules | Identical agent step limit, timeout, stop tokens, and termination policy; exact values frozen in protocol/private manifest before smoke |
| Tools/prompt | Identical system/task prompt, tool policy, repository image, and environment |
| Verifier | Identical task-specific verifier revision and scoring extraction |
| Cache | KV quantization disabled; identical cache dtype and context handling |
| Speculative/prefill options | Speculative prefill and dFlash disabled; any draft-assistance setting identical and privately pinned |
| Scheduling | One trial at a time; no parallel benchmark trials |

Immediately before the smoke pair and full matrix, snapshot API-effective settings privately. Older unused profile records must not be mistaken for active settings.

## 6. Trial identity and execution order

A trial key is:

```text
(task_alias, repetition, precision_alias)
```

Repetitions are numbered 1–4. Within each task/repetition pair, alternate condition order using this frozen rule:

- odd repetitions: `bf16`, then `mlx-affine-int8-g64`;
- even repetitions: `mlx-affine-int8-g64`, then `bf16`.

Tasks execute in alias order. Only one trial runs at a time. Warm-up and cleanup policy must be identical before every recorded trial.

## 7. Attrition and rerun rules

Every discovered trial receives exactly one attempt classification:

- `completed`: valid model/agent attempt reached a normal terminal state;
- `model_agent_timeout`: valid outcome; retained, never rerun merely for being slow or unsuccessful;
- `model_agent_failure`: valid outcome when the harness ran correctly but the agent/model failed;
- `environment_harness_failure`: infrastructure prevented a valid model/agent attempt;
- `verifier_only_failure`: attempt exists, but the verifier failed independently.

Rules:

1. Model/agent timeouts and failures remain outcomes.
2. Environment/harness failures may be repaired and rerun once under a documented, condition-neutral repair.
3. Verifier-only failures may rerun the verifier without rerunning inference when the original artifact is intact; otherwise follow the environment-failure rule.
4. Original failed records remain in the attrition table even when a rerun succeeds.
5. No run is excluded because its score, steps, tokens, latency, repetition, or trajectory looks unusual.
6. A primary paired difference is missing when either member lacks verifier-covered F2P/P2P; missing pairs are counted and shown, not silently dropped.

Report discovered artifacts, valid attempts, verifier-covered attempts, and successful completions separately.

## 8. Analysis frozen before execution

### Primary analysis

1. Validate the expected 40-cell matrix and unique trial keys.
2. Validate parity fields: checkpoint alias/revision proof, architecture, engine, scheme, task alias, and repetition.
3. Compute paired F2P and P2P differences for verifier-covered pairs.
4. Show every task-level point and task-level mean.
5. Compute the aggregate as the equal-weight mean of the five task-level means, so tasks—not stochastic repeats—define the sampling unit.
6. Report the reward/pass pair-state table.

### Uncertainty

Use a task-clustered paired bootstrap:

- fixed public analysis seed: `20260715`;
- 10,000 bootstrap replicates;
- resample the five task aliases with replacement;
- retain all repetitions belonging to each sampled task;
- recompute task-level means and their equal-weight aggregate;
- report the 2.5th and 97.5th percentiles as a descriptive 95% interval.

With only five selected tasks, the interval is descriptive and must not be presented as broad population certainty. Also report all task-level points so heterogeneity remains visible.

### Secondary analysis

For steps, tokens, elapsed time, and peak context:

1. report the complete valid-outcome distribution by condition;
2. report paired differences where both attempts are valid;
3. stratify by reward/F2P/P2P only as clearly conditional secondary analysis;
4. never conclude that fewer steps or tokens are better when task quality is lower;
5. retain timeouts at their preregistered censoring/limit value where appropriate and show counts.

### Sensitivity and missingness

- Show results with all verifier-covered pairs.
- Show task-level completeness and attrition by condition.
- If any primary pair is missing, prohibit a causal or universal headline and label the matrix incomplete.
- Do not impute F2P, P2P, or reward.

## 9. Publication and privacy boundary

Public artifacts may contain only:

- checkpoint and condition aliases;
- architecture alias;
- task aliases;
- repetition number;
- sanitized status, F2P, P2P, reward, steps, token counts, elapsed time, and peak context;
- aggregate and attrition summaries.

Never export exact provider/model identifiers, local paths, exact private task IDs, prompts, patches, raw trajectories, credentials, or hidden-helper identity. The ignored private manifest supplies the alias mapping and source paths to the analyzer.

## 10. Gates before any outcome-bearing full run

- [ ] Exact same immutable checkpoint revision proven for both artifacts.
- [ ] Private alias manifest created and schema-validated.
- [ ] Public protocol copied from and subordinate to this design.
- [ ] Analyzer tests pass, including evidence-gate refusal cases.
- [ ] API-effective engine/model settings snapshotted privately.
- [ ] Orphaned benchmark container and stale result metadata resolved without touching unrelated services.
- [ ] One paired smoke run completes under both conditions with verifier coverage.
- [ ] Smoke validates both no-history task environments or preregistered replacements are selected and smoked.
- [ ] Sequential 40-cell run schedule generated and frozen.

If any gate fails, do not begin the full matrix and do not publish a quantization recommendation.
