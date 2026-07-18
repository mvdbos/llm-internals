# Mission

**As an amateur, I want to run the best possible local model on my hardware.**

## Primary goal

Once I have selected a model, I want practical guidance for choosing the right quantization and the other settings that materially affect whether it fits, runs well, and remains useful for my work. When I see options like `Q4_K_M`, `Q8_0`, `IQ3_XXS`, or `bf16`, I want to know what trade-off I am making—not just follow a rule of thumb.

## Supporting knowledge

I want to learn the supporting knowledge that helps me make those choices confidently: what weights are, why quantization approximates them, why file size differs from runtime memory, what a format label does and does not identify, and how to compare candidates on the work I actually do.

I am not trying to become an expert in LLM internals, quantization implementations, or evaluation methodology. Technical detail belongs in the course only when it explains a practical local-model decision; deeper detail should remain available as reference material.

## What “best” means

There is no universal best quant or local setup. The best choice depends on the selected model, available hardware and headroom, runtime compatibility, speed needs, and intended workload. The aim is to make a well-scoped choice and validate it when the trade-off matters—not to memorize a universal ranking or blindly benchmark everything.
