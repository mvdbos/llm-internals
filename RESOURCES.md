# Resources

*Curated, high-trust resources for learning about LLM internals and quantization.*

## Primary sources (text)

| Resource | Why it's good | URL |
|---|---|---|
| **ML Journey: Quantized LLMs Explained (Q4 vs Q8 vs FP16)** | Comprehensive, practical guide with decision framework. Good analogies (ruler). Covers group-wise, asymmetric quantization. | [mljourney.com](https://mljourney.com/quantized-llms-explained-q4-vs-q8-vs-fp16/) |
| **Demystifying LLM Quantization Suffixes** | Explains GGUF suffixes (Q4_K_M, Q8_0, IQ3_XXS, etc.) and what the letters mean. Practical download decisions. | [Medium/@paul.ilvez](https://medium.com/@paul.ilvez/demystifying-llm-quantization-suffixes-what-q4-k-m-q8-0-and-q6-k-really-mean-0ec2770f17d3) |
| **LLM Hardware Quantization Guide** | Focused on VRAM formulas and hardware tradeoffs. Good for "which quant fits my GPU?" | [llmhardware.io](https://llmhardware.io/guides/llm-quantization-guide) |
| **Sebastian Raschka: Recent Developments in LLM Architectures** | Deep technical but very clear. Covers layer types, KV sharing, MoE. | [magazine.sebastianraschka.com](https://magazine.sebastianraschka.com/p/recent-developments-in-llm-architectures) |

## Primary sources (video)

| Resource | Why it's good | URL |
|---|---|---|
| **3Blue1Brown: Transformers (Deep Learning Ch. 5)** | The gold standard visual explanation of how data flows through transformer layers. Grant Sanderson. | [YouTube](https://www.youtube.com/watch?v=wjZofJX0v4M) |
| **Andrej Karpathy: Intro to Large Language Models** | 1-hour talk. Covers the full stack from training to inference, including quantization pragmatics. | [YouTube](https://www.youtube.com/watch?v=zjkBMFhNj_g) |

## Reference / canonical

| Resource | Why it's good | URL |
|---|---|---|
| **llama.cpp GGUF quantization types** | The source of truth for what Q4_K_M, Q8_0, IQ3_XXS actually mean. | [GitHub: ggerganov/llama.cpp](https://github.com/ggerganov/llama.cpp) |
| **The Illustrated Transformer (Jay Alammar)** | Classic visual walkthrough of transformer internals. | [jalammar.github.io](https://jalammar.github.io/illustrated-transformer/) |

## For later (wisdom / community)

| Resource | What it's for |
|---|---|
| **r/LocalLLaMA** | The go-to community for running models locally. Practical quantization advice, benchmarks, real-world experiences. |
| **Hugging Face model cards** | Per-model quantization benchmarks and community discussion in the comments. |
