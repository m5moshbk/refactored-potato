import pytest

from nexus_drive.policy import Operation, PolicyDeniedError, PolicyEngine


def test_mock_metadata_and_memory_indexing_are_allowed():
    policy = PolicyEngine()
    policy.authorize(Operation.READ_MOCK_METADATA)
    policy.authorize(Operation.INDEX_IN_MEMORY)


@pytest.mark.parametrize("operation", [
    Operation.GOOGLE_API_READ,
    Operation.GOOGLE_API_WRITE,
    Operation.DOWNLOAD_FILE,
    Operation.UPLOAD_FILE,
    Operation.MOVE_FILE,
    Operation.DELETE_FILE,
])
def test_external_and_mutating_operations_are_denied(operation):
    with pytest.raises(PolicyDeniedError):
        PolicyEngine().authorize(operation)


def test_live_mode_is_not_supported():
    with pytest.raises(ValueError):
        PolicyEngine(mode="live")


def test_disabling_read_only_is_not_supported():
    with pytest.raises(ValueError):
        PolicyEngine(read_only=False)


def test_unknown_operation_type_is_rejected():
    with pytest.raises(TypeError):
        PolicyEngine().authorize("read_mock_metadata")
