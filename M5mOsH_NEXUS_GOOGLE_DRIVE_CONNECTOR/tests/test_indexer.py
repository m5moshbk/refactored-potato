import pytest

from nexus_drive.indexer import MetadataIndexer, StalePageTokenError
from nexus_drive.models import DriveItem, FOLDER_MIME_TYPE
from nexus_drive.policy import Operation, PolicyDeniedError, PolicyEngine


def file(file_id, name=None, parents=()):
    return DriveItem(
        file_id=file_id,
        name=name or file_id,
        mime_type="text/plain",
        parents=tuple(parents),
    )


def folder(file_id, parents=()):
    return DriveItem(
        file_id=file_id,
        name=file_id,
        mime_type=FOLDER_MIME_TYPE,
        parents=tuple(parents),
    )


def test_index_one_and_basic_reads():
    index = MetadataIndexer()
    saved = index.index_one(file("f1"))
    assert saved.file_id == "f1"
    assert index.get_item("f1") == saved
    assert index.contains("f1")
    assert index.count() == 1
    assert index.snapshot() == {"f1": saved}


def test_strict_batch_is_atomic_on_invalid_item():
    index = MetadataIndexer()
    index.index_one(file("existing"))
    before = index.snapshot()
    generation = index.generation

    with pytest.raises(ValueError):
        index.index_many([file("new"), {"file_id": "", "name": "bad", "mime_type": "x"}])

    assert index.snapshot() == before
    assert index.generation == generation


def test_non_strict_batch_skips_invalid_items():
    index = MetadataIndexer()
    result = index.index_many([
        file("a"),
        {"file_id": "", "name": "bad", "mime_type": "x"},
        file("b"),
    ], strict=False)
    assert result.items_indexed == 2
    assert result.unique_items == 2


def test_duplicate_ids_update_existing_item():
    index = MetadataIndexer()
    result = index.index_many([file("same", "old"), file("same", "new")])
    assert result.items_indexed == 2
    assert result.duplicate_updates == 1
    assert index.get_item("same").name == "new"


def test_generator_failure_does_not_commit_staged_items():
    index = MetadataIndexer()
    index.index_one(file("stable"))
    before = index.snapshot()

    def broken():
        yield file("not-committed")
        raise RuntimeError("generator failed")

    with pytest.raises(RuntimeError):
        index.index_many(broken())
    assert index.snapshot() == before


def test_policy_denies_index_operation():
    class DenyIndexPolicy(PolicyEngine):
        def authorize(self, operation):
            if operation == Operation.INDEX_IN_MEMORY:
                raise PolicyDeniedError("denied")
            return super().authorize(operation)

    index = MetadataIndexer(policy=DenyIndexPolicy())
    with pytest.raises(PolicyDeniedError):
        index.index_one(file("x"))


def test_pages_are_sorted_and_generation_aware():
    index = MetadataIndexer()
    index.index_many([file("c"), file("a"), file("b")])
    first = index.page(page_size=2)
    assert [item.file_id for item in first.items] == ["a", "b"]
    assert first.next_page_token == str(index.generation) + ":2"

    second = index.page(page_size=2, page_token=first.next_page_token)
    assert [item.file_id for item in second.items] == ["c"]
    assert second.next_page_token is None


def test_old_page_token_rejected_after_mutation():
    index = MetadataIndexer()
    index.index_many([file("a"), file("b")])
    first = index.page(page_size=1)
    index.index_one(file("c"))
    with pytest.raises(StalePageTokenError):
        index.page(page_size=1, page_token=first.next_page_token)


@pytest.mark.parametrize("page_size", [0, -1, 1001, True, 1.5])
def test_invalid_page_size_rejected(page_size):
    with pytest.raises(ValueError):
        MetadataIndexer().page(page_size=page_size)


@pytest.mark.parametrize("token", [1, True, "", "-1", "x:0", "1:-2", "١:0", "1:٢", "1:2:3"])
def test_invalid_page_tokens_rejected(token):
    with pytest.raises(ValueError):
        MetadataIndexer().page(page_token=token)


def test_hierarchy_accepts_valid_parent_chain():
    index = MetadataIndexer()
    index.index_many([
        folder("root"),
        folder("child", parents=("root",)),
        file("leaf", parents=("child",)),
    ])
    index.validate_hierarchy()


def test_hierarchy_rejects_missing_or_non_folder_parent():
    index = MetadataIndexer()
    index.index_one(file("orphan", parents=("missing",)))
    with pytest.raises(ValueError, match="missing parent"):
        index.validate_hierarchy()

    index = MetadataIndexer()
    index.index_many([file("parent"), file("child", parents=("parent",))])
    with pytest.raises(ValueError, match="parent must be a folder"):
        index.validate_hierarchy()


@pytest.mark.parametrize("items", [
    [folder("a", parents=("a",))],
    [folder("a", parents=("b",)), folder("b", parents=("a",))],
    [folder("a", parents=("b",)), folder("b", parents=("c",)), folder("c", parents=("a",))],
])
def test_hierarchy_rejects_self_parent_and_cycles(items):
    index = MetadataIndexer()
    index.index_many(items)
    with pytest.raises(ValueError):
        index.validate_hierarchy()


def test_parent_can_arrive_in_later_batch():
    index = MetadataIndexer()
    index.index_one(file("child", parents=("parent",)))
    with pytest.raises(ValueError, match="missing parent"):
        index.validate_hierarchy()
    index.index_one(folder("parent"))
    index.validate_hierarchy()
