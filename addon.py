from __future__ import annotations

import re

from anki.collection import Collection
from aqt import gui_hooks, mw
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


def _ids_sql(ids: list[int]) -> str:
    if not ids:
        return "(0)"
    return "(" + ",".join(str(int(item_id)) for item_id in ids) + ")"


def _card_priority_key(queue: int, due: int, original_index: int) -> tuple[int, int, int]:
    if queue in (1, 3, 4):
        queue_rank = 0
    elif queue == 2:
        queue_rank = 1
    elif queue == 0:
        queue_rank = 2
    elif queue in (-2, -3):
        queue_rank = 8
    elif queue == -1:
        queue_rank = 9
    else:
        queue_rank = 7
    return (queue_rank, due, original_index)


def _sort_card_ids_by_queue_position(col: Collection, card_ids: list[int]) -> list[int]:
    if len(card_ids) <= 1:
        return list(card_ids)

    rows = col.db.all(
        f"select id, queue, due from cards where id in {_ids_sql(card_ids)}"
    )
    original_positions = {card_id: index for index, card_id in enumerate(card_ids)}
    ranked = []
    for card_id, queue, due in rows:
        ranked.append(
            (
                _card_priority_key(
                    int(queue),
                    int(due),
                    original_positions.get(int(card_id), len(card_ids)),
                ),
                int(card_id),
            )
        )
    ranked.sort(key=lambda item: item[0])
    ranked_ids = [card_id for _, card_id in ranked]

    if len(ranked_ids) == len(card_ids):
        return ranked_ids

    ranked_set = set(ranked_ids)
    ranked_ids.extend(card_id for card_id in card_ids if card_id not in ranked_set)
    return ranked_ids


def _sort_note_ids_by_matching_card_queue_position(
    col: Collection, note_ids: list[int], cleaned_query: str
) -> list[int]:
    if len(note_ids) <= 1:
        return list(note_ids)

    matching_card_ids = list(_ORIGINAL_FIND_CARDS(col, cleaned_query))
    if not matching_card_ids:
        return list(note_ids)

    rows = col.db.all(
        f"select id, nid, queue, due from cards where id in {_ids_sql(matching_card_ids)}"
    )
    card_positions = {card_id: index for index, card_id in enumerate(matching_card_ids)}
    ranked_cards = []
    for card_id, note_id, queue, due in rows:
        ranked_cards.append(
            (
                _card_priority_key(
                    int(queue),
                    int(due),
                    card_positions.get(int(card_id), len(matching_card_ids)),
                ),
                int(note_id),
            )
        )
    ranked_cards.sort(key=lambda item: item[0])

    allowed_note_ids = set(int(note_id) for note_id in note_ids)
    ordered_note_ids: list[int] = []
    seen_note_ids: set[int] = set()
    for _, note_id in ranked_cards:
        if note_id not in allowed_note_ids or note_id in seen_note_ids:
            continue
        seen_note_ids.add(note_id)
        ordered_note_ids.append(note_id)

    if len(ordered_note_ids) == len(note_ids):
        return ordered_note_ids

    ordered_note_ids.extend(
        int(note_id) for note_id in note_ids if int(note_id) not in seen_note_ids
    )
    return ordered_note_ids


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

    ids = list(context.ids)
    if mw is not None and mw.col is not None and ids:
        card_match_count = mw.col.db.scalar(
            f"select count() from cards where id in {_ids_sql(ids)}"
        )
        if int(card_match_count or 0) == len(ids):
            ids = _sort_card_ids_by_queue_position(mw.col, ids)
        else:
            ids = _sort_note_ids_by_matching_card_queue_position(mw.col, ids, context.search or "*")

    context.ids = ids[:limit]


def _find_notes_with_limit(self: Collection, query: str, *args, **kwargs):
    cleaned_query, limit = _extract_limit(query or "")
    note_ids = _ORIGINAL_FIND_NOTES(self, cleaned_query, *args, **kwargs)
    if limit is None:
        return note_ids
    sorted_note_ids = _sort_note_ids_by_matching_card_queue_position(
        self, list(note_ids), cleaned_query
    )
    return sorted_note_ids[:limit]


def _find_cards_with_limit(self: Collection, query: str, *args, **kwargs):
    cleaned_query, limit = _extract_limit(query or "")
    card_ids = _ORIGINAL_FIND_CARDS(self, cleaned_query, *args, **kwargs)
    if limit is None:
        return card_ids
    sorted_card_ids = _sort_card_ids_by_queue_position(self, list(card_ids))
    return sorted_card_ids[:limit]


def _patch_collection_search() -> None:
    Collection.find_notes = _find_notes_with_limit
    Collection.find_cards = _find_cards_with_limit


def register() -> None:
    _patch_collection_search()
    gui_hooks.browser_will_search.append(_prepare_limit_search)
    gui_hooks.browser_did_search.append(_apply_limit_to_results)
