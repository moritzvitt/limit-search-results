# Limit Search Results

This Anki add-on adds a custom search modifier: `limit:x`.

When you include `limit:x` in a search query, Anki will use only the first `x` matching cards or notes from the current results.

Examples:

- `deck:Spanish limit:10`
- `tag:important is:new limit:25`
- `note:Basic limit:5`

## How It Works

- `limit:x` is removed before the normal Anki search runs.
- The remaining query is searched as usual.
- The add-on trims the final result list to the first `x` items.
- This works with both card and note results in the Browser.
- It also applies to other add-ons or tools that call Anki collection search methods such as `find_notes()` or `find_cards()` with a query containing `limit:x`.

If you search with only `limit:x`, the add-on applies the limit to all matching results.

## Files

- Main logic: [`addon.py`](./addon.py)
- Add-on entry point: [`__init__.py`](./__init__.py)
- Manifest: [`manifest.json`](./manifest.json)
- Config notes: [`config.md`](./config.md)
- Release text: [`docs/release-description.md`](./docs/release-description.md)

## Packaging

To package manually:

```bash
zip -r limit-search-results.ankiaddon . -x './.git/*' './.vscode/*' './__pycache__/*' './.DS_Store'
```
