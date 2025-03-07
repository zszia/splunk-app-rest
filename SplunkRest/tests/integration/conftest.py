import os

import pytest
from splunklib import client


@pytest.fixture(scope="session")
def splunk_service():
    return client.connect(
        username="admin",
        password=os.environ["SPLUNK_PASSWORD"],
    )
