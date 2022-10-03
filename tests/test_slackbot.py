from biologic import slackbot
from biologic.config import slack_channel_url, slack_user_id

dummy_message = 'unit testing slackbot'

def test_prepare_message():
    message = slackbot._prepare_message(message=dummy_message)

    assert isinstance(message, dict)
    assert 'text' in message.keys()


def test_prepend_user_id():
    message = slackbot._prepend_user_id(
        user_id=slack_user_id,
        message=dummy_message
    )

    assert isinstance(message, str)


def test_post():
    slackbot.post(
        message=dummy_message,
        user_id=slack_user_id,
        url=slack_channel_url
    )    

