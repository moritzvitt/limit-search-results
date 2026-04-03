# Limit Search Results

This Anki add-on adds a custom search modifier: `limit:x`.

When you include `limit:x` in a search query, Anki keeps only the `x` matching cards or notes that are closest in queue position.

Examples:

- `deck:Spanish limit:10`
- `tag:important is:new limit:25`
- `note:Basic limit:5`

## How It Works

- `limit:x` is removed before the normal Anki search runs.
- The remaining query is searched as usual.
- Matching cards are ranked by queue state and due position so the add-on prefers cards you are likely to see sooner.
- Matching notes are ranked by the earliest matching card attached to each note.
- This works with both card and note results in the Browser.
- It also applies to other add-ons or tools that call Anki collection search methods such as `find_notes()` or `find_cards()` with a query containing `limit:x`.

If you search with only `limit:x`, the add-on applies the limit to all matching results.

## Why This Is Useful

- Review the next few matching cards instead of a long unordered result list.
- Keep note searches focused on notes whose matching cards are due sooner.
- Reuse the same `limit:x` query in Browser searches and collection API calls.

## Files

- Main logic: [`addon.py`](./addon.py)
- Add-on entry point: [`__init__.py`](./__init__.py)
- Manifest: [`manifest.json`](./manifest.json)
- Config notes: [`config.md`](./config.md)
- Release text: [`docs/release-description.md`](./docs/release-description.md)

## Packaging

To package manually:

```bash
zip -r limit-search-results.ankiaddon \
  __init__.py \
  addon.py \
  manifest.json \
  config.json \
  config.md \
  LICENSE
```
