from typing import Callable, TypeVar


ItemT = TypeVar('ItemT')


def find_item(items: list[ItemT], does_item_match: Callable[[ItemT], bool]):
    found_items = [item for item in items if does_item_match(item)]

    if len(found_items) == 0:
        return None

    return found_items[0]
