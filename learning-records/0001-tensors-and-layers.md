# Learning Record 0001: Tensors & Layers

**Date:** 2026-07-13
**Lesson:** [0001-tensors-and-layers.html](../lessons/0001-tensors-and-layers.html)
**Status:** superseded by the 2026 course audit

This generalized record preserves the conceptual corrections from the original lesson without personal learning-profile or setup details. It is not current evidence; the revised lesson and pinned sources are authoritative.

## Corrections carried forward

- Parameters include embeddings and other learned tensors, but observed behavior also depends on architecture, tokenizer, context, decoding, and tools.
- An embedding → repeated Transformer blocks → output projection is one architecture pattern, not a universal description of every LLM.
- Parameter allocation and quantization sensitivity vary by architecture; no fixed FFN percentage or universal sensitivity hierarchy is assumed.
- The bytes-per-parameter shortcut is only a first estimate. Complete accounting includes encoding metadata, mixed or unquantized tensors, loaded representation, retained state, workspaces, and runtime overhead.

## Durable concepts

- A tensor has a shape, dtype, and values; changing value representation does not imply that every tensor shape or runtime state remains unchanged.
- Learned parameters, transient activations, retained runtime state, and artifact bytes are different accounting categories.
- Text reaches model layers through tokenization and embeddings; later blocks create contextual representations; logits and decoding produce the next token.
- Architecture-specific fields are required before applying a memory formula.
