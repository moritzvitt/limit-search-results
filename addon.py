from __future__ import annotations

import re

from anki.collection import Collection
from aqt import gui_hooks
from aqt.browser import SearchContext

LIMIT_RE = re.compile(r"(^|\s)limit:(\d+)\b", re.IGNORECASE)
LIMIT_METADATA_KEY = "limit_search_results.limit"
_ORIGINAL_FIND_NOTES = Collection.find_notes
_ORIGINAL_FIND_CARDS = Collection.find_cards


def _extract_limit(search: str) -> tuple[str, int | None]:
    match = LIMIT_RE.search(search)
    if not match:
        return search, None

    limit = int(match.group(2))
    cleaned_search = LIMIT_RE.sub(" ", search).strip()
    cleaned_search = re.sub(r"\s{2,}", " ", cleaned_search)
    return cleaned_search or "*", limit


def _prepare_limit_search(context: SearchContext) -> None:
    if context.ids is not None:
        return

    search, limit = _extract_limit(context.search or "")
    if limit is None:
        return

    context.search = search
    context.addon_metadata[LIMIT_METADATA_KEY] = limit


def _apply_limit_to_results(context: SearchContext) -> None:
    limit = context.addon_metadata.get(LIMIT_METADATA_KEY)
    if limit is None or context.ids is None:
        return

    context.ids = list(context.ids)[:limit]


def _find_notes_with_limit(self: Collection, query: str, *args, **kwargs):
    cleaned_query, limit = _extract_limit(query or "")
    note_ids = _ORIGINAL_FIND_NOTES(self, cleaned_query, *args, **kwargs)
    if limit is None:
        return note_ids
    return list(note_ids)[:limit]


def _find_cards_with_limit(self: Collection, query: str, *args, **kwargs):
    cleaned_query, limit = _extract_limit(query or "")
    card_ids = _ORIGINAL_FIND_CARDS(self, cleaned_query, *args, **kwargs)
    if limit is None:
        return card_ids
    return list(card_ids)[:limit]


def _patch_collection_search() -> None:
    Collection.find_notes = _find_notes_with_limit
    Collection.find_cards = _find_cards_with_limit


def register() -> None:
    _patch_collection_search()
    gui_hooks.browser_will_search.append(_prepare_limit_search)
    gui_hooks.browser_did_search.append(_apply_limit_to_results)
