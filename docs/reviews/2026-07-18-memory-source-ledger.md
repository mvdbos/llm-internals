# Memory lesson source ledger

| Claim | Source and scope |
|---|---|
| Artifact size differs from loaded and peak memory | Mechanism/accounting boundary; measure under a named engine and loading policy rather than generalizing from one runtime. |
| Retained state can grow with workload/context | Architecture-scoped mechanism; conventional cached attention is one example, not a universal cache formula. |
| Conventional KV cache is retained state | `reference/glossary.html#kv-cache`; explicitly limited to conventional cached self-attention. |
| Peak memory includes working allocations and overhead | `reference/glossary.html#runtime-memory`; measurement boundary and peak/steady-state label required. |

The new lesson makes no implementation-specific memory or compatibility claim. Existing glossary definitions and the canonical evidence ledger provide adjacent reference depth; integration may add a primary architecture/runtime source if an implementation table is introduced.
