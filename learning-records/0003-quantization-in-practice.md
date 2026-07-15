# Learning Record 0003: Choosing the Right Quantization

**Date:** 2026-07-13
**Lesson:** [0003-quantization-in-practice.html](../lessons/0003-quantization-in-practice.html)

## Revision status

Superseded by the 2026 course audit. These notes preserve the original learning state but must not be treated as current evidence. Reassessment is required after the revised lesson.

Retracted or uncertain claims in the preserved notes:

- The three-axis selection rule and task-sensitivity spectrum are incomplete and were presented as universal without evidence.
- The 70% RAM rule, the claim that larger models tolerate lower precision, and the bf16/Q8/Q4 labels lacked backend, architecture, and accounting scope.
- The “KV-cache snowball” mechanism was unsupported: a conventional cache stores retained keys/values, not accumulated attention scores, and cache format is a separate variable.
- The thinking-budget conclusion and short-conversation claim were unsupported empirical generalizations.
- The old 57% step comparison used unmatched tasks/repetitions and mixed architectures; no stored metric established “thought duplication,” so neither the percentage nor the causal explanation is valid evidence about quantization.
- Steps alone are not output quality; controlled evaluation requires paired quality outcomes, verifier coverage, attrition rules, and uncertainty.

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
