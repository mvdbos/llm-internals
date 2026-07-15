# Learning Record 0001: Tensors & Layers

**Date:** 2026-07-13
**Lesson:** [0001-tensors-and-layers.html](../lessons/0001-tensors-and-layers.html)

## Revision status

Superseded by the 2026 course audit. These notes preserve the original learning state but must not be treated as current evidence. Reassessment is required after the revised lesson.

Retracted or uncertain claims in the preserved notes:

- “Knowledge lives entirely in weights” is too absolute: parameters include an embedding lookup, while observed behavior also depends on architecture, tokenizer, context, decoding, and tools.
- The simple embedding → identical Transformer layers → output stack is one architecture pattern, not a universal LLM description.
- The 65% FFN parameter split and claimed universal FFN sensitivity/dominance were not sourced and vary by architecture.
- The bytes-per-parameter memory shortcut omits encoding metadata, mixed/unquantized tensors, loaded representation, retained state, workspaces, and runtime overhead.

## What was learned

- A tensor is just a multi-dimensional grid of numbers — the universal data format in ML
- LLM "knowledge" lives entirely in the weights distributed across layers; there's no separate database
- The transformer stack: embedding → N transformer layers (attention + FFN) → output
- Feed-forward layers hold ~65% of all parameters; they dominate both memory use and quantization sensitivity
- Memory formula: size ≈ num_params × bytes_per_param. FP16=2, Q8=1, Q4=0.5 bytes per param.

## Key insights

- The user already intuitively knows tensors (spreadsheets = 2D tensors, lists = 1D tensors)
- The distinction between tensor *shapes* (the grid dimensions) and tensor *values* (the actual numbers) is important for quantization — quantization changes the precision of values, not the shape
- Most parameters live in FFN layers, so quantizing FFN aggressively gives the biggest memory wins

## Zone of proximal development

- Ready for: how quantization actually works (mapping floats to ints, scale factors, group-wise quantization)
- Not yet: advanced quantization techniques (IQ, AWQ, GPTQ), MoE architectures
