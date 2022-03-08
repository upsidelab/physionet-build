from typing import Iterator, Tuple, Optional, TypeVar, Callable

from user.models import User


T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


def user_has_cloud_identity(user: User) -> bool:
    return hasattr(user, "cloud_identity")


def user_has_billing_setup(user: User) -> bool:
    if not user_has_cloud_identity(user):
        return False
    return hasattr(user.cloud_identity, "billing_setup")


def user_workspace_setup_done(user: User) -> bool:
    if not user_has_cloud_identity(user):
        return False
    return user.cloud_identity.is_workspace_done


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
