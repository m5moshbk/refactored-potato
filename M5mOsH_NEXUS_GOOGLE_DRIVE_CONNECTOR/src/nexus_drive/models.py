"""Validated, immutable metadata models. No Google SDK dependency."""

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Tuple

FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"


@dataclass(frozen=True)
class DriveItem:
    file_id: str
    name: str
    mime_type: str
    parents: Tuple[str, ...] = ()
    size_bytes: Optional[int] = None
    modified_time: Optional[str] = None

    def __post_init__(self) -> None:
        if not isinstance(self.file_id, str) or not self.file_id.strip():
            raise ValueError("file_id must be a non-empty string")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("name must be a non-empty string")
        if not isinstance(self.mime_type, str) or not self.mime_type.strip():
            raise ValueError("mime_type must be a non-empty string")
        if not isinstance(self.parents, tuple):
            raise TypeError("parents must be a tuple of strings")
        if any(not isinstance(parent, str) or not parent.strip() for parent in self.parents):
            raise ValueError("each parent id must be a non-empty string")
        if len(set(self.parents)) != len(self.parents):
            raise ValueError("parents must not contain duplicates")
        if self.size_bytes is not None:
            if (
                not isinstance(self.size_bytes, int)
                or isinstance(self.size_bytes, bool)
                or self.size_bytes < 0
            ):
                raise ValueError("size_bytes must be a non-negative integer or None")
        if self.modified_time is not None and not isinstance(self.modified_time, str):
            raise TypeError("modified_time must be a string or None")

    @property
    def is_folder(self) -> bool:
        return self.mime_type == FOLDER_MIME_TYPE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_id": self.file_id,
            "name": self.name,
            "mime_type": self.mime_type,
            "parents": list(self.parents),
            "size_bytes": self.size_bytes,
            "modified_time": self.modified_time,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "DriveItem":
        if not isinstance(data, Mapping):
            raise TypeError("DriveItem data must be a mapping")
        allowed = {
            "file_id", "name", "mime_type", "parents",
            "size_bytes", "modified_time",
        }
        unexpected = set(data) - allowed
        if unexpected:
            raise ValueError("unexpected DriveItem fields: " + ", ".join(sorted(unexpected)))
        parents = data.get("parents", ())
        if isinstance(parents, list):
            parents = tuple(parents)
        elif isinstance(parents, tuple):
            parents = parents
        else:
            raise TypeError("parents must be a list or tuple")
        return cls(
            file_id=data.get("file_id"),
            name=data.get("name"),
            mime_type=data.get("mime_type"),
            parents=parents,
            size_bytes=data.get("size_bytes"),
            modified_time=data.get("modified_time"),
        )
