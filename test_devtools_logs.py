from unittest.mock import patch

from devtools_logs import event, ship_build, ship_diagnostic, ship_release


def test_event_keeps_workflow_context():
    item = event("devtools-job", "info", "build completed", kind="build", build_id="b-7")
    assert item.service == "devtools-job"
    assert item.attributes == {"kind": "build", "build_id": "b-7"}
    assert item.level == "info"


def test_ship_functions_use_entries_field():
    with patch("devtools_logs.infrai.logs.ingest", return_value={}) as ingest:
        ship_build("b-7", "abc")
        ship_release("r-2", "staging")
        ship_diagnostic("lock", True)

    assert ingest.call_count == 3
    for call in ingest.call_args_list:
        assert list(call.kwargs) == ["entries"]
        assert len(call.kwargs["entries"]) == 1
        assert call.kwargs["entries"][0]["service"] == "devtools-job"
