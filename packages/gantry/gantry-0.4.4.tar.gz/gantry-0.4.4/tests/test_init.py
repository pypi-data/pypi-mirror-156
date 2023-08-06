import mock
import pytest

import gantry
from gantry.exceptions import ClientNotInitialized


@pytest.mark.parametrize(
    "method",
    [
        "ping",
        "instrument",
        "log_feedback_event",
        "log_feedback",
        "log_record",
        "log_records",
        "log_prediction_event",
        "log_predictions",
    ],
)
def test_uninit_client(method):
    with mock.patch("gantry._CLIENT", None):
        with pytest.raises(ClientNotInitialized):
            getattr(gantry, method)()
