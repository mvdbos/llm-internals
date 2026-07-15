# Learning Record 0003: Quantization in Practice

**Date:** 2026-07-13
**Lesson:** [0003-quantization-in-practice.html](../lessons/0003-quantization-in-practice.html)

## What was learned

- Deep-SWE benchmarks quantified the bf16 vs 8-bit gap: 74 steps (bf16) vs 116 steps (8-bit) — a 57% increase
- The root cause isn't slower per-step processing but systematic thought duplication (unique/total thoughts ratio < 1.0)
- Thinking budget doesn't fix quantization degradation — it gives more tokens for fuzzy thoughts, not better thoughts
- Precision sensitivity is task-dependent: creative writing (low) < factual recall (low) < pattern matching (medium) < multi-step reasoning (high) < long-horizon planning (very high)

## Key insights

- For agentic workloads, quantization cost compounds: each slightly-worse thought leads to more correction steps, which adds more context, which makes subsequent thoughts even noisier
- The 35B question: larger models tolerate more aggressive quantization. A 35B at Q4 might beat a 27B at Q8 for reasoning — the extra parameters compensate for fuzzier weights
- A systematic approach: benchmark the SAME task across quants, compare steps + thought uniqueness, test 2-3 diverse tasks before committing
- The step count difference (74 vs 116) is a concrete, measurable proxy for reasoning quality degradation

## Zone of proximal development

- Mastered: quant format selection, decision framework for different task types
- Ready for: hands-on benchmarking, building a personal calibration curve for your models
- Future: comparing across model sizes (27B vs 35B at different quants), oMLX-specific quantization parameters
