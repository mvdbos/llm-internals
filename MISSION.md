# Mission

**Understand LLM internals well enough to make scoped, evidence-backed quantization decisions for local inference.**

## Public learner objective

The course should let a learner:

1. distinguish learned parameters, temporary activations, and architecture-specific retained runtime state;
2. explain quantization as a numeric encode/store/decode process rather than a magic compression knob;
3. separate checkpoints, artifacts, encodings, model-file recipes, inference engines, backends, kernels, and hardware;
4. calculate explicit weight/cache estimates and verify the measured runtime boundary;
5. design a matched workload evaluation and choose among measured Pareto points without relying on universal quality rules.

## Private project context

Regular local-model use motivated the original course. Earlier local artifacts suggested that model choice, precision, runtime configuration, and agent behavior might interact, but those observations were not a controlled quantization study. They used unmatched tasks and repetitions, included architecture and configuration differences, and did not justify a causal claim that quantization degraded reasoning.

That uncertainty is now part of the method rather than the teaching conclusion: define the exact scheme and target, control the comparison, measure task-valid outcomes, and state what remains unknown.

## Evidence and publication boundary

- Canonical facts are pinned to source revisions.
- Numerical examples are labeled as sourced observations or pedagogical calculations.
- Historical and pilot observations cannot become recommendations.
- The controlled comparison is preregistered but its execution is deferred.
- The final capstone and result-dependent recommendation remain unpublished until the paired evidence gate passes.
