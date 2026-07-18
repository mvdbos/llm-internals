# Lesson 2 practical scope map

## Learner win

| Requirement | Scope decision |
|---|---|
| Practical decision | Understand the memory/approximation trade-off before comparing quantized candidates. |
| Minimum theory | Fewer numeric levels, shared scale and offset, one encode → store → reconstruct example, block metadata, and the distinction between local reconstruction error and workload quality. |
| Learner action | Explain why nominal four-bit storage is approximate and why a label alone cannot guarantee acceptable workload quality. |

## Boundary

Keep the practical explanation in Lesson 2. Move mapping-family catalogues, duplicate symmetric/affine parameterization formulas, and the full evaluation taxonomy to optional reference material. Preserve only a concise link to the reference after the lesson’s single concrete affine round trip.

## Requirement-to-evidence ledger

| Requirement | Target | Verification | Status |
|---|---|---|---|
| Fewer-bits intuition before formulas | Opening table and paragraph | Read opening order | complete |
| Floating-point caveat | Opening table caption/text | Search for `unevenly spaced` | complete |
| Neutral conceptual labels | Opening table | No production-format labels in instructional spine | complete |
| One affine encode/store/reconstruct example | Worked example | One complete round trip remains | complete |
| Block metadata and effective storage | Block section | Storage calculation and explanation remain | complete |
| Local error is not workload quality | Error section and quiz | Scoped caveat and quiz question | complete |
| One group-size trade-off | Why blocks section | No repeated explanation later | complete |
| Product-neutral instructional spine | Lesson body | Only authorized boundary callout points forward | complete |
| Three required quiz concepts | Quiz | Metadata, workload quality, group-size questions | complete |
| Practical handoff | Closing takeaway | Points to runtime memory lesson | complete |

## Final check

The revised lesson has six learner-facing sections (including quiz and takeaway) and an estimated reading time of nine minutes. `python3 scripts/audit_course.py --allow-planned-lessons`, `node --check assets/quiz.js`, and `git diff --check` passed on 2026-07-18.

## Reference handoff for the format reference

`reference/quantization-formats.html` should preserve sourced optional depth on mapping-family categories, symmetric and affine parameterizations, and implementation-specific variants. Lesson 2 should not require a learner to memorize those categories to make its first practical decision.
