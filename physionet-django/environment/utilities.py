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


def left_join_iterators(
    key_left: Callable[[T], V],
    left: Iterator[T],
    key_right: Callable[[U], V],
    right: Iterator[U],
) -> Iterator[Tuple[T, Optional[U]]]:
    right_dict = {key_right(element): element for element in right}
    return [(element, right_dict.get(key_left(element))) for element in left]


def right_join_iterators(
    key_left: Callable[[T], V],
    left: Iterator[T],
    key_right: Callable[[U], V],
    right: Iterator[U],
) -> Iterator[Tuple[Optional[T], U]]:
    left_dict = {key_left(element): element for element in left}
    return [(left_dict.get(key_right(element)), element) for element in right]


def full_outer_join_iterators(
    key_left: Callable[[T], V],
    left: Iterator[T],
    key_right: Callable[[U], V],
    right: Iterator[U],
) -> Iterator[Tuple[Optional[T], Optional[U]]]:
    left_joined = left_join_iterators(key_left, left, key_right, right)
    right_joined = right_join_iterators(key_left, left, key_right, right)
    left_outer_joined = [
        (left_el, right_el) for left_el, right_el in left_joined if right_el is None
    ]

    return [*left_outer_joined, *right_joined]
