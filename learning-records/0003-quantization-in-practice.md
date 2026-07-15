# Learning Record 0003: Choosing the Right Quantization

**Date:** 2026-07-13
**Lesson:** [0003-quantization-in-practice.html](../lessons/0003-quantization-in-practice.html)

## What was learned

- Quant selection is a 3-axis problem: task type, hardware budget, model size
- Task precision sensitivity spectrum: creative writing (low) → agentic coding (very high)
- Hardware headroom matters: target ≤70% of available RAM for the model
- Larger models tolerate more aggressive quantization — a 35B at Q4 may beat a 27B at Q8
- The KV cache snowball: quantization noise compounds across long agentic loops
- Thinking budget doesn't compensate for fuzzy weights — more tokens ≠ better thoughts

## Key insights

- A systematic benchmarking method: same task × multiple quants, measure steps + output quality
- The case study (27B model, bf16 vs 8-bit on coding tasks) showed 57% more steps with 8-bit due to thought duplication
- Short conversations (5-10 turns) show almost no quality difference between Q8 and bf16 — degradation needs long contexts to become visible

## Zone of proximal development

- Ready for: hands-on benchmarking with own models
- Future: comparing model families (Llama vs Qwen vs DeepSeek at equivalent quants), inference engine differences (llama.cpp vs MLX vs vLLM)
