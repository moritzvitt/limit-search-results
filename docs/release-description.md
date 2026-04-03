# Limit Search Results

Limit the number of results shown in Anki with a simple search modifier.

Use `limit:x` in a search query to keep only the `x` matching cards or notes that are closest in queue position.

Examples:

- `deck:Default limit:20`
- `tag:marked limit:5`
- `is:new limit:50`

The add-on removes `limit:x`, runs the remaining query normally, then ranks matching cards by queue state and due position before trimming the result list. For note results, it ranks notes by their earliest matching card.

It works in the Browser and also applies to add-ons or tools that call Anki collection search methods such as `find_notes()` and `find_cards()` with a query containing `limit:x`.
