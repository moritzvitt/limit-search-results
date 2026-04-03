# Architecture Overview

The add-on adds a `limit:x` modifier to Anki search queries.

## Flow

1. A shared parser looks for `limit:x` in the query text.
2. If present, the add-on removes it from the actual search query and keeps the numeric limit.
3. The Browser hooks still store the parsed value in `context.addon_metadata` so Browser result lists can be trimmed normally.
4. The add-on also patches collection search methods so `find_notes()` and `find_cards()` respect `limit:x` outside the Browser hook lifecycle.
5. Matching cards are re-ranked by queue state and due position before the limit is applied.
6. Matching notes are ranked by the earliest matching card attached to each note.

## Notes

- The add-on preserves Anki's normal search filtering, but changes result ordering when `limit:x` is present so it can prefer cards closer in queue position.
- It works for both card and note Browser modes.
- It also works for other add-ons that pass `limit:x` into collection search methods.
- The add-on has no user configuration at the moment.
