import random
from typing import Iterator, Tuple, Optional, TypeVar, Callable
from string import ascii_uppercase

from user.models import User


T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


def gcp_user_id_for_user(user: User, random_suffix_length: int = 3) -> str:
    max_username_length = User._meta.get_field("username").max_length
    max_truncated_username_length = max_username_length - random_suffix_length - 1
    username = user.username
    truncated_username = (
        username[:max_truncated_username_length]
        if len(username) > max_truncated_username_length
        else username
    )
    random_suffix = "".join(random.choices(ascii_uppercase, k=random_suffix_length))
    return f"{truncated_username}-{random_suffix}"


def user_has_cloud_identity(user: User) -> bool:
    return hasattr(user, "cloud_identity")


def user_has_billing_setup(user: User) -> bool:
    if not user_has_cloud_identity(user):
        return False
    return hasattr(user.cloud_identity, "billing_setup")


def inner_join_iterators(
    key_left: Callable[[T], V],
    left: Iterator[T],
    key_right: Callable[[U], V],
    right: Iterator[U],
) -> Iterator[Tuple[T, U]]:
    right_dict = {key_right(element): element for element in right}
    return [
        (element, right_dict[key_left(element)])
        for element in left
        if key_left(element) in right_dict
    ]


def left_join_iterators(
    key_left: Callable[[T], V],
    left: Iterator[T],
    key_right: Callable[[U], V],
    right: Iterator[U],
) -> Iterator[Tuple[T, Optional[U]]]:
    right_dict = {key_right(element): element for element in right}
    return [(element, right_dict.get(key_left(element))) for element in left]
