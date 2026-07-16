# Learning Record 0002: How Quantization Works

**Date:** 2026-07-13
**Lesson:** [0002-how-quantization-works.html](../lessons/0002-how-quantization-works.html)
**Status:** superseded by the 2026 course audit

This generalized record preserves corrections from the original lesson without personal setup, provider, model, or benchmark details. It is not current evidence; the revised lesson and pinned implementation sources are authoritative.

## Corrections carried forward

- Quantization does not universally mean mapping FP16 weights to integers with one FP16 scale. Targets, mappings, group size, code width, metadata dtypes, and exceptions are separate choices.
- GGUF, GGML tensor labels, llama.cpp recipes, MLX modes, and oMLX oQ recipes belong to distinct artifact/runtime ecosystems and are not portable synonyms.
- Suffixes and broad quality labels do not guarantee one tensor-by-tensor recipe or a universal quality ranking.
- No universal tensor-sensitivity hierarchy, task-sensitivity ranking, or fixed attention/embedding/FFN precision recipe is assumed.
- Unmatched historical artifacts cannot establish a causal effect of quantization.

## Durable concepts

- A quantized representation stores restricted codes plus the metadata needed to reconstruct or compute with approximations.
- Effective bits per weight count codes, metadata, exceptions, and their data types under one declared accounting boundary.
- Group size trades metadata overhead against how locally the mapping can fit value ranges.
- The exact artifact, engine/backend, kernels, hardware, and workload must be identified before comparing memory, speed, or quality.
