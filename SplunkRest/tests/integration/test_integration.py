from splunklib import client


def test_splunk__no_messages(splunk_service: client.Service):
    """ensure that splunk does not show warnings (might be caused by a configuration problem)"""
    messages = list(splunk_service.messages)
    assert not messages, "\n".join(f"{message.name}:{message.value}" for message in messages)
