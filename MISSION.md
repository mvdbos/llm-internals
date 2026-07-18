# Goal and intended audience

## Who this course is for

This course is for people who want to run a local language model and have already chosen the model itself.

You do not need to be an LLM engineer. You do need a practical way to choose a model artifact and runtime setup that fits your hardware, performs well enough, and remains useful for the work you actually want to do.

## The goal

By the end of the course, you should be able to make and explain a choice between compatible local-model candidates.

In practice, that means you can:

1. identify what a model download and its labels actually describe;
2. distinguish model-file size from the memory needed while the model runs;
3. rule out candidates that do not fit your runtime, context requirement, or available headroom;
4. compare the remaining candidates on the workload that matters to you; and
5. choose a quality, speed, and memory trade-off while stating what is still uncertain.

The goal is not to find a universally “best” quantization. There is no such answer. A good choice depends on the selected model, your hardware, the runtime you can use, the context you need, and the work you expect the model to perform.

## What this course covers

The main course focuses on the decisions that follow model selection:

- how quantization changes stored weights;
- why a smaller download may still need more runtime memory than expected;
- how to read an artifact, recipe, and runtime label without treating them as interchangeable;
- how to shortlist candidates that fit; and
- how much validation is appropriate before making a choice.

## What it does not try to teach

This is not a course on choosing the best base model, training models, or becoming an expert in quantization implementations.

It also does not offer a universal ranking such as “always choose four-bit” or “the smallest file is best.” Detailed format catalogues, source-level implementation details, and rigorous experimental protocol are available as reference material when you need them.

## How to use the course

Follow the lessons in order the first time. They build the minimum knowledge needed for the next practical decision:

**weights and approximation → runtime memory → candidate identification → choice and validation**

When you are evaluating a real candidate later, return to the decision checklist and the relevant reference pages rather than trying to memorize every format name.
