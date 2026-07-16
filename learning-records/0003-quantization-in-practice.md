# Learning Record 0003: Choosing Quantization

**Date:** 2026-07-13
**Historical lesson:** [withdrawn notice](../lessons/0003-quantization-in-practice.html)
**Supported replacement:** [0003-reading-quantization-formats.html](../lessons/0003-reading-quantization-formats.html)
**Status:** superseded by the 2026 course audit

This generalized record documents why the historical practical guide was withdrawn. It contains no personal setup details and publishes no historical benchmark outcomes.

## Corrections carried forward

- Quantization choice is not reducible to a universal task-type, memory-percentage, or model-size rule.
- A larger model at lower precision cannot be assumed to outperform a smaller model at higher precision without matched workload evidence.
- Conventional KV caches retain key/value vectors; they do not store accumulated attention scores. Cache precision is a separate experimental variable.
- More generated tokens do not prove better or worse reasoning, and step counts alone are not output quality.
- Unmatched tasks, repetitions, architectures, discovered artifacts, and verifier coverage cannot support a causal precision comparison.

## Durable decision procedure

1. Identify checkpoint provenance, artifact format, quantized targets, engine/backend, kernels, and hardware.
2. Calculate artifact, loaded, retained-state, measured-peak, and headroom requirements separately.
3. Shortlist only candidates that satisfy compatibility and deployment constraints.
4. Evaluate exact paired tasks with verifier-backed outcomes, attrition rules, and uncertainty.
5. Apply hard constraints, then choose among feasible nondominated trade-offs.
