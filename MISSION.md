# Mission

**I want to understand LLM internals well enough to make smart quantization choices when running local models.**

## Primary goal

When I see model options like `Q4_K_M`, `Q8_0`, `IQ3_XXS`, or `bf16`, I want to know what these actually mean — not just a rule of thumb, but the *why*. What trade-off am I making? When is 4-bit perfectly fine, and when is it hurting me?

## Secondary goal

To get there, I need the prerequisite knowledge: what tensors and layers actually are inside an LLM. Not at a researcher level, but deep enough that quantization isn't just a magic compression knob.

## Context

I run local models regularly and have seen that quantization can affect output quality in subtle ways. I want to understand *why* that happens, so I can make better model choices without blind benchmarking every time.
