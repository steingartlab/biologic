import requests

HEADERS = {'Content-type': 'application/json'}


def _prepare_message(message: str) -> dict:
    """Messages must be dictionaries.
    
    Args:
        message (str): The message to be sent to channel.

    Returns:
        dict: Formatted text ready to be sent to channel.
    """
    return {'text': message}


def _prepend_user_id(user_id: str, message: str) -> str:
    """Formats message appropriately to tag user.
    
    Args:
        message (str): The message to be sent to channel.
        user_id (str): User ID for tagging user in message.
            Refer to Notion manual on how to find.
    """
    return f'<@{user_id}>: {message}'


def post(message: str, url: str, user_id: str = None) -> None:
    """Sends message to slack channel.

    Requires incoming webhooks enabled for the channel IDd
    by the url. 
    
    Args:
        message (str): The message to be sent to channel.
        url (str): Unique channel URL as generated when
            the webhook was enabled. Be careful not to
            share this externally.
        user_id (str): User ID for tagging user in message.
            Refer to Notion manual on how to find.
    """

    if user_id is not None:
        message = _prepend_user_id(
            user_id=user_id,
            message=message
        )

    outgoing_message = _prepare_message(message=message)
    response = requests.post(
        url=url,
        headers=HEADERS,
        json=outgoing_message
    )