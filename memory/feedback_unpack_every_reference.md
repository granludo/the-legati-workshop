---
name: unpack-every-reference
description: Never cite a bare identifier (issue, PR, commit, version, decision code, relative path) without saying in the same sentence what it is and which repo it lives in. Starter memory from the original workshop; keep, edit or delete.
metadata:
  type: feedback
---

On first mention, an identifier comes with its identity: not "#456" but "#456, the export-to-PDF pull request"; not "migration 26" but "migration 26, the one that adds the tags table"; not "D5" but "D5, the decision to drop the appendix". Paths are given relative to a named repository root, and when two repositories are in play, say which.

**Why:** a bare number is cheap for the legatus that just read the tracker and expensive for the human who did not. It forces them to stop and look it up, or to guess. The reader should never need a second document open to parse a sentence.

**How to apply:** in chat above all. In a tracker whose table already defines its codes, the shorthand can stand after the first use.
