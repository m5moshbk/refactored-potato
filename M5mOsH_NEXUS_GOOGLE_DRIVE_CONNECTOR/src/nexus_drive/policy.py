"""Application-level allow-list for MOCK operations only."""

from enum import Enum


class Operation(str, Enum):
    READ_MOCK_METADATA = "read_mock_metadata"
    INDEX_IN_MEMORY = "index_in_memory"
    GOOGLE_API_READ = "google_api_read"
    GOOGLE_API_WRITE = "google_api_write"
    DOWNLOAD_FILE = "download_file"
    UPLOAD_FILE = "upload_file"
    MOVE_FILE = "move_file"
    DELETE_FILE = "delete_file"


class PolicyDeniedError(PermissionError):
    """Raised when an operation is outside the configured policy."""


class PolicyEngine:
    def __init__(self, mode: str = "mock", read_only: bool = True) -> None:
        if mode != "mock":
            raise ValueError("this prototype supports MOCK mode only")
        if read_only is not True:
            raise ValueError("this prototype requires read_only=True")
        self.mode = mode
        self.read_only = read_only
        self._allowed = {
            Operation.READ_MOCK_METADATA,
            Operation.INDEX_IN_MEMORY,
        }

    def authorize(self, operation: Operation) -> None:
        if not isinstance(operation, Operation):
            raise TypeError("operation must be an Operation value")
        if operation not in self._allowed:
            raise PolicyDeniedError("operation denied by MOCK-only policy: " + operation.value)
