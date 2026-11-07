import pytest

from nexus_drive.models import DriveItem, FOLDER_MIME_TYPE


def test_folder_detection_and_round_trip():
    item = DriveItem("folder-1", "Root", FOLDER_MIME_TYPE)
    assert item.is_folder is True
    assert DriveItem.from_dict(item.to_dict()) == item


@pytest.mark.parametrize("field,value", [
    ("file_id", ""),
    ("name", " "),
    ("mime_type", ""),
])
def test_required_strings_rejected(field, value):
    values = {
        "file_id": "id",
        "name": "name",
        "mime_type": "text/plain",
    }
    values[field] = value
    with pytest.raises(ValueError):
        DriveItem(**values)


@pytest.mark.parametrize("size", [-1, True, 1.5, "12"])
def test_invalid_sizes_rejected(size):
    with pytest.raises(ValueError):
        DriveItem("f1", "file", "text/plain", size_bytes=size)


def test_parents_must_be_tuple_and_unique():
    with pytest.raises(TypeError):
        DriveItem("f1", "file", "text/plain", parents=["p1"])
    with pytest.raises(ValueError):
        DriveItem("f1", "file", "text/plain", parents=("p1", "p1"))


def test_unknown_fields_rejected():
    with pytest.raises(ValueError):
        DriveItem.from_dict({
            "file_id": "f1", "name": "x", "mime_type": "text/plain",
            "unexpected": "value",
        })
