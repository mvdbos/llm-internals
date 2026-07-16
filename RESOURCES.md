# Resources and evidence ledger

*Accessed 2026-07-15. Implementation sources are pinned to immutable revisions. Claims must not be generalized beyond the scope column.*

<a id="canonical"></a>
## Canonical sources

| Source | Resolved revision | Exact claim supported | Scope | URL |
|---|---|---|---|---|
| **Attention Is All You Need** | NeurIPS 2017; arXiv `1706.03762v7` | Introduces scaled dot-product and multi-head attention, position-wise FFNs, residuals/norms, and causal decoder masking. | Original translation architecture; not proof that every modern LLM uses conventional full attention. | [NeurIPS](https://papers.nips.cc/paper/7181-attention-is-all-you-need), [arXiv v7](https://arxiv.org/abs/1706.03762v7) |
| **llama.cpp quantize README** | `3b53219361a61b53e7741c479b81b755ec6096b1` | Documents `llama-quantize`, versioned `_S`/`_M`/`_L` recipe labels, the `--imatrix` input and tensor overrides, and a model-specific effective-bpw/throughput table. | llama.cpp at this revision; suffixes are recipe variants rather than universal bit assignments; numerical table is for `meta-llama/Llama-3.1-8B`. | [Options and importance matrix](https://github.com/ggml-org/llama.cpp/blob/3b53219361a61b53e7741c479b81b755ec6096b1/tools/quantize/README.md#L43-L62), [pinned table](https://github.com/ggml-org/llama.cpp/blob/3b53219361a61b53e7741c479b81b755ec6096b1/tools/quantize/README.md#L137-L170) |
| **llama.cpp tensor-type selection** | `3b53219361a61b53e7741c479b81b755ec6096b1` | `_M` is a model-file mixture recipe: tensor category, architecture, layer position, GQA/MoE properties, and fallbacks can select different encodings. | llama.cpp quantizer at this revision; not a universal attention/FFN bit assignment. | [Selection logic](https://github.com/ggml-org/llama.cpp/blob/3b53219361a61b53e7741c479b81b755ec6096b1/src/llama-quant.cpp#L529-L639), [base mapping](https://github.com/ggml-org/llama.cpp/blob/3b53219361a61b53e7741c479b81b755ec6096b1/src/llama-quant.cpp#L793-L834) |
| **GGUF specification and acronym** | GGML `af97976c7810cdabb1863172f31c432dab767de7`; acronym at llama.cpp revision above | GGUF is a binary model artifact containing metadata and tensors; it is not a runtime. The canonical expansion is **GGML Universal File**. | GGUF format. | [Specification](https://github.com/ggml-org/ggml/blob/af97976c7810cdabb1863172f31c432dab767de7/docs/gguf.md#L1-L50), [official acronym](https://github.com/ggml-org/llama.cpp/blob/3b53219361a61b53e7741c479b81b755ec6096b1/gguf-py/README.md#L1-L7) |
| **GGML block structures** | GGML `af97976c7810cdabb1863172f31c432dab767de7` | Defines stored fields and raw-block overhead for `Q8_0`, K-blocks, and `IQ4_XS`; raw block bpw is not the same as whole-artifact effective bpw. | Raw tensor blocks only—not headers, unquantized tensors, or mixture recipes. | [Constants](https://github.com/ggml-org/ggml/blob/af97976c7810cdabb1863172f31c432dab767de7/src/ggml-common.h#L85-L90), [`Q8_0`](https://github.com/ggml-org/ggml/blob/af97976c7810cdabb1863172f31c432dab767de7/src/ggml-common.h#L251-L256), [K-blocks](https://github.com/ggml-org/ggml/blob/af97976c7810cdabb1863172f31c432dab767de7/src/ggml-common.h#L290-L368), [`IQ4_XS`](https://github.com/ggml-org/ggml/blob/af97976c7810cdabb1863172f31c432dab767de7/src/ggml-common.h#L446-L460) |
| **MLX quantization API** | MLX `v0.32.0`, commit `7a1d4f5c12ac82f4b4d0a6e71538d89ca0605247` | Mode, group size, bit width, and quantized targets are separate choices. Affine mode returns packed weights, scales, and biases; MXFP4/group 32, MXFP8/group 32, and NVFP4/group 16 are distinct no-bias floating modes in the pinned API. Model quantization is weight-only by default. | MLX 0.32.0; not GGUF and not a claim about a particular converted artifact. | [API](https://ml-explore.github.io/mlx/build/html/python/_autosummary/mlx.core.quantize.html), [core implementation](https://github.com/ml-explore/mlx/blob/7a1d4f5c12ac82f4b4d0a6e71538d89ca0605247/python/src/ops.cpp#L4600-L4690), [model quantizer](https://github.com/ml-explore/mlx/blob/7a1d4f5c12ac82f4b4d0a6e71538d89ca0605247/python/mlx/nn/layers/quantized.py#L11-L67) |
| **oMLX oQ documentation** | `5a39ba3a9c28bd8125aa8502d710b89e874efb46` | oQ uses sensitivity-driven mixed precision. At this revision, oQ4 and oQ6 use affine/group-64 base precision with budgeted boosts, while **oQ8 is MXFP8/group 32**. | Current oQ/oQ+ output, not historical artifacts or every artifact oMLX can load. | [Pinned documentation](https://github.com/jundot/omlx/blob/5a39ba3a9c28bd8125aa8502d710b89e874efb46/docs/oQ_Quantization.md#L27-L43), [allocation logic description](https://github.com/jundot/omlx/blob/5a39ba3a9c28bd8125aa8502d710b89e874efb46/docs/oQ_Quantization.md#L71-L113) |
| **Public MLX affine 8-bit example** | Hugging Face `4255b21bd9a9d3fc807ef7abd80373f5e3a52a73` | Public config explicitly separates `mode: affine`, `bits: 8`, and `group_size: 64`, demonstrating that this is not GGUF `Q8_0` or current oQ8. | This public artifact only; it is not the private case-study identity. | [Pinned config](https://huggingface.co/mlx-community/gemma-4-e4b-it-8bit/blob/4255b21bd9a9d3fc807ef7abd80373f5e3a52a73/config.json), [model card](https://huggingface.co/mlx-community/gemma-4-e4b-it-8bit/blob/4255b21bd9a9d3fc807ef7abd80373f5e3a52a73/README.md) |
| **KV-cache mechanics** | Transformers `cd7456ea43677e7936b2429365eda59a09a51e51`; GQA paper, EMNLP 2023 | Cached self-attention appends and reuses key/value vectors; it does not cache attention scores or repeatedly rewrite old entries. GQA/MQA change the KV-head count; sliding-window and quantized caches change storage. | Conventional cached self-attention; recurrent, SSM, linear-attention, and hybrid state require different formulas. | [Cache explanation](https://github.com/huggingface/transformers/blob/cd7456ea43677e7936b2429365eda59a09a51e51/docs/source/en/cache_explanation.md#L24-L93), [cache strategies](https://github.com/huggingface/transformers/blob/cd7456ea43677e7936b2429365eda59a09a51e51/docs/source/en/kv_cache.md#L17-L37), [GQA](https://aclanthology.org/2023.emnlp-main.298/) |

### Pinned model-level effective-bpw example

Source: `meta-llama/Llama-3.1-8B`, llama.cpp commit `3b53219361a61b53e7741c479b81b755ec6096b1`, [README lines 141–170](https://github.com/ggml-org/llama.cpp/blob/3b53219361a61b53e7741c479b81b755ec6096b1/tools/quantize/README.md#L141-L170).

| File recipe | Effective bpw for this model |
|---|---:|
| `Q8_0` | 8.5008 |
| `Q6_K` | 6.5633 |
| `Q4_K_M` | 4.8944 |
| `IQ4_XS` | 4.4597 |

These values are model-level measurements for the pinned table, not universal constants. For comparison, the pinned structs imply raw-block costs of 8.5, 6.5625, 4.5, and 4.25 bpw respectively.

### High-trust quantization evaluations

| Study | Revision/venue | Exact claim supported | Scope | URL |
|---|---|---|---|---|
| **The case for 4-bit precision** | ICML 2023, PMLR 202; arXiv `2212.09720v2` | Block size, numeric type, model scale, and bit width jointly affect the total-bits/zero-shot-accuracy trade-off. | 16-bit inputs, 3–8-bit parameters, 19M–176B models in the studied families. | [PMLR](https://proceedings.mlr.press/v202/dettmers23a.html), [arXiv](https://arxiv.org/abs/2212.09720v2) |
| **Evaluating Quantized Large Language Models** | ICML 2024, PMLR 235; arXiv `2402.18158v2` | Weights, activations, and KV cache require separate evaluation across task types and long-context behavior. | Eleven model families, 125M–180B; not validation of one GGUF or MLX recipe. | [PMLR](https://proceedings.mlr.press/v235/li24bb.html), [arXiv](https://arxiv.org/abs/2402.18158v2) |
| **A Comprehensive Evaluation of Quantization Strategies for LLMs** | Findings of ACL 2024; DOI `10.18653/v1/2024.findings-acl.726`; arXiv `2402.16775v2` | Perplexity correlates with many but not all downstream results; memory savings do not guarantee speedups. | Tested instruction-tuned models and methods only. | [ACL](https://aclanthology.org/2024.findings-acl.726/), [arXiv](https://arxiv.org/abs/2402.16775v2) |
| **Quantization Hurts Reasoning?** | COLM 2025; arXiv `2504.04823v2` | Effects are model-, size-, bit-width-, target-, and task-dependent; extra reasoning can help some quantized models. | Public 1.5B–70B reasoning models; not agent-loop evidence. | [OpenReview](https://openreview.net/forum?id=BM192Ps5Nv), [arXiv](https://arxiv.org/abs/2504.04823v2) |
| **Unified llama.cpp quantization evaluation** | arXiv `2601.14277v1` preprint | Controlled single-model GGUF comparison using perplexity, downstream tasks, size, quantization time, and CPU throughput. | `Llama-3.1-8B-Instruct` under the study setup only. | [arXiv](https://arxiv.org/abs/2601.14277v1) |

<a id="explainers"></a>
## Explainers

These are secondary teaching aids, not primary evidence for implementation details, numerical tables, or compatibility:

- [3Blue1Brown — Transformers](https://www.youtube.com/watch?v=wjZofJX0v4M)
- [Sebastian Raschka — Recent Developments in LLM Architectures](https://magazine.sebastianraschka.com/p/recent-developments-in-llm-architectures)
- [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/)
- [Raschka — Coding the KV Cache](https://magazine.sebastianraschka.com/p/coding-the-kv-cache-in-llms)

<a id="community"></a>
## Community sources

Mutable practitioner evidence can help discover questions and hardware-specific reports, but cannot establish acronym expansions, block layouts, effective bpw, compatibility, or quality recommendations:

- [llama.cpp Discussions](https://github.com/ggml-org/llama.cpp/discussions)
- [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/)
- Hugging Face model-card discussions and comments
