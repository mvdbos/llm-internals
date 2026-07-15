# Learning Record 0002: How Quantization Works

**Date:** 2026-07-13
**Lesson:** [0002-how-quantization-works.html](../lessons/0002-how-quantization-works.html)

## What was learned

- Quantization maps FP16 weights to lower-bit integers using per-block scale factors
- The key trick: each group of weights shares one high-precision (FP16) scale factor; individual weights become cheap integers
- GGUF naming decoded: Q/IQ, bit-width, K-quant, S/M/L size variants
- Importance-weighted (IQ) quants are smarter than traditional linear (Q) quants at the same bit-width
- Layer sensitivity varies: embeddings/output > attention > FFN. K-quants exploit this with per-layer-type strategies.

## Key insights

- Q4_K_M (the community sweet spot) uses mixed precision: ~6-bit for attention and embeddings, ~4-bit for FFN
- For agentic/reasoning tasks, precision matters more than for creative/conversational use — long chains of logic can't absorb fuzzy weights
- The perplexity increase from Q8_0 is negligible (~0.01-0.02) but Q4_K_M adds ~0.05-0.15 — enough for subtle reasoning misses
- This explains the Deep-SWE benchmark results: 8-bit quantization degraded agentic SWE performance measurably vs bf16

## Zone of proximal development

- Ready for: practical quant selection for specific models and hardware, benchmarking methodology
- Next: Lesson 3 — applying this to the actual setup (oMLX, Qwen models, Deep-SWE benchmarks)
