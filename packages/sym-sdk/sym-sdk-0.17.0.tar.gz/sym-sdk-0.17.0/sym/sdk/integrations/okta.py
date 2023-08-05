"""Helpers for interacting with the Okta API within the Sym SDK."""


from typing import List

from sym.sdk.exceptions import OktaError  # noqa
from sym.sdk.user import User


def is_user_in_group(user: User, *, group_id: str) -> bool:
    """Checks if the provided user is a member of the Okta group specified.

    The Okta group's ID must be given, and the method will check that the group exists and is
    accessible. An exception will be thrown if not.

    Args:
        user: The user to check group membership of.
        group_id: The ID of the Okta group.

    Returns:
        True if the user is a member of the specified Okta group, False otherwise.
    """


def users_in_group(*, group_id: str) -> List[User]:
    """Get all users from the specified Okta group.

    The Okta group's ID must be given, and the method will check that the group exists and is
    accessible. An exception will be thrown if not.

    Args:
        group_id: The ID of the Okta group.
    """
