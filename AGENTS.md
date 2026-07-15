# AGENTS.md — LLM Internals Course

## Glossary-linking rule

Every technical term that has an entry in `reference/glossary.html` MUST be linked to its glossary anchor on **first occurrence per page** using `class="glossary-link"`.

### How to do it

```html
<p>Each <a href="../reference/glossary.html#W" class="glossary-link">weight</a> is stored as a number.</p>
```

Glossary anchors are single-letter IDs matching the first letter of the term: `#T` for Tensor, `#W` for Weight, `#K` for K-quant / KV Cache, etc. Check `reference/glossary.html` for the exact anchor.

### Visual treatment

Glossary links use a subtle dotted underline (defined in `assets/style.css`). They inherit the body text color so they don't compete with regular hyperlinks.

### After finishing a lesson

Add a "Terms in this lesson" footer at the bottom, before the closing `</body>`, using the `.terms-footer` class:

```html
<div class="terms-footer">
  <p><strong>📖 Terms in this lesson:</strong>
    <a href="../reference/glossary.html#T">Tensor</a> ·
    <a href="../reference/glossary.html#W">Weight</a> ·
    ...
  </p>
</div>
```

This footer doubles as a self-audit: every term you linked inline should appear here. If a term is in the footer but not linked inline, you missed a first occurrence.

### What NOT to link

- Don't link the same term twice on one page (first occurrence only)
- Don't link terms inside quiz questions or answer buttons (breaks the quiz UX)
- Don't link terms that aren't in the glossary
- Don't use `class="glossary-link"` for external links (those are regular `<a>` tags)

### Adding new glossary entries

When you add a new term to `reference/glossary.html`, give it an `id` attribute matching its first letter. If that letter is already taken, append a number: `#A1`, `#A2`, etc. Then update all lessons that use the new term.
