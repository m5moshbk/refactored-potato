"""Atomic in-memory metadata index with generation-aware pagination."""

from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Tuple, Union

from .models import DriveItem, FOLDER_MIME_TYPE
from .policy import Operation, PolicyEngine


class StalePageTokenError(ValueError):
    """Raised when a page token refers to an older index generation."""


@dataclass(frozen=True)
class IndexResult:
    items_indexed: int
    duplicate_updates: int
    unique_items: int


@dataclass(frozen=True)
class IndexPage:
    items: Tuple[DriveItem, ...]
    next_page_token: Optional[str]
    generation: int


class MetadataIndexer:
    def __init__(self, policy: Optional[PolicyEngine] = None) -> None:
        self.policy = policy or PolicyEngine()
        self._items: Dict[str, DriveItem] = {}
        self._generation = 0

    @property
    def generation(self) -> int:
        return self._generation

    def index_one(self, item: Union[DriveItem, dict]) -> DriveItem:
        self.policy.authorize(Operation.INDEX_IN_MEMORY)
        normalized = self._coerce(item)
        self._items[normalized.file_id] = normalized
        self._generation += 1
        return normalized

    def index_many(self, items: Iterable[Union[DriveItem, dict]], strict: bool = True) -> IndexResult:
        self.policy.authorize(Operation.INDEX_IN_MEMORY)
        if not isinstance(strict, bool):
            raise TypeError("strict must be a boolean")

        staged = dict(self._items)
        indexed = 0
        duplicate_updates = 0

        for raw in items:
            try:
                item = self._coerce(raw)
            except (TypeError, ValueError):
                if strict:
                    raise
                continue
            if item.file_id in staged:
                duplicate_updates += 1
            staged[item.file_id] = item
            indexed += 1

        if indexed:
            self._items = staged
            self._generation += 1

        return IndexResult(
            items_indexed=indexed,
            duplicate_updates=duplicate_updates,
            unique_items=len(self._items),
        )

    @staticmethod
    def _coerce(item: Union[DriveItem, dict]) -> DriveItem:
        if isinstance(item, DriveItem):
            return item
        if isinstance(item, dict):
            return DriveItem.from_dict(item)
        raise TypeError("items must be DriveItem instances or dictionaries")

    def get_item(self, file_id: str) -> Optional[DriveItem]:
        self.policy.authorize(Operation.READ_MOCK_METADATA)
        return self._items.get(file_id)

    def contains(self, file_id: str) -> bool:
        self.policy.authorize(Operation.READ_MOCK_METADATA)
        return file_id in self._items

    def all_items(self) -> Tuple[DriveItem, ...]:
        self.policy.authorize(Operation.READ_MOCK_METADATA)
        return tuple(self._items[key] for key in sorted(self._items))

    def count(self) -> int:
        self.policy.authorize(Operation.READ_MOCK_METADATA)
        return len(self._items)

    def snapshot(self) -> Dict[str, DriveItem]:
        self.policy.authorize(Operation.READ_MOCK_METADATA)
        return dict(self._items)

    def page(self, page_size: int = 100, page_token: Optional[str] = None) -> IndexPage:
        self.policy.authorize(Operation.READ_MOCK_METADATA)
        if (
            not isinstance(page_size, int)
            or isinstance(page_size, bool)
            or page_size < 1
            or page_size > 1000
        ):
            raise ValueError("page_size must be an integer from 1 to 1000")

        if page_token is None:
            token_generation = self._generation
            offset = 0
        else:
            if not isinstance(page_token, str):
                raise ValueError("page_token must be a string or None")
            parts = page_token.split(":")
            if len(parts) != 2 or not all(part.isascii() and part.isdecimal() for part in parts):
                raise ValueError("page_token must use generation:offset decimal format")
            token_generation, offset = int(parts[0]), int(parts[1])
            if token_generation != self._generation:
                raise StalePageTokenError("page token belongs to a stale index generation")

        ordered = self.all_items()
        selected = ordered[offset:offset + page_size]
        next_offset = offset + len(selected)
        next_token = None
        if next_offset < len(ordered):
            next_token = str(self._generation) + ":" + str(next_offset)
        return IndexPage(tuple(selected), next_token, self._generation)

    def validate_hierarchy(self) -> None:
        """Validate parent references and detect cycles after all pages are indexed."""
        self.policy.authorize(Operation.READ_MOCK_METADATA)

        for item in self._items.values():
            for parent_id in item.parents:
                if parent_id == item.file_id:
                    raise ValueError("item cannot be its own parent: " + item.file_id)
                parent = self._items.get(parent_id)
                if parent is None:
                    raise ValueError("missing parent: " + parent_id)
                if not parent.is_folder or parent.mime_type != FOLDER_MIME_TYPE:
                    raise ValueError("parent must be a folder: " + parent_id)

        # Iterative DFS over the single-parent relation; multiple parents are also checked.
        state: Dict[str, int] = {}
        for start in self._items:
            if state.get(start) == 2:
                continue
            stack = [(start, False)]
            while stack:
                node_id, exiting = stack.pop()
                if exiting:
                    state[node_id] = 2
                    continue
                current = state.get(node_id, 0)
                if current == 1:
                    raise ValueError("parent cycle detected at: " + node_id)
                if current == 2:
                    continue
                state[node_id] = 1
                stack.append((node_id, True))
                node = self._items[node_id]
                for parent_id in node.parents:
                    if state.get(parent_id) == 1:
                        raise ValueError("parent cycle detected at: " + parent_id)
                    if state.get(parent_id) != 2:
                        stack.append((parent_id, False))


# Compatibility alias for callers using the shorter historical name.
Indexer = MetadataIndexer
