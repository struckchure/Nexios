

from __future__ import annotations

import functools
from collections import defaultdict
from typing import Any, Callable, cast

PRE_DUMP = "pre_dump"
POST_DUMP = "post_dump"
PRE_LOAD = "pre_load"
POST_LOAD = "post_load"
VALIDATES = "validates"
VALIDATES_SCHEMA = "validates_schema"


class Hook:
    __hook__: dict[str, list[tuple[bool, Any]]] | None = None


def validates(field_name: str) -> Callable[..., Any]:
    """Register a field validator.

    :param str field_name: Name of the field that the method validates.
    """
    return set_hook(None, VALIDATES, field_name=field_name)


def validates_schema(
    fn: Callable[..., Any] | None = None,
    pass_many: bool = False,
    pass_original: bool = False,
    skip_on_field_errors: bool = True,
) -> Callable[..., Any]:
    
    return set_hook(
        fn,
        VALIDATES_SCHEMA,
        many=pass_many,
        pass_original=pass_original,
        skip_on_field_errors=skip_on_field_errors,
    )


def pre_dump(
    fn: Callable[..., Any] | None = None, pass_many: bool = False
) -> Callable[..., Any]:
  
    return set_hook(fn, PRE_DUMP, many=pass_many)


def post_dump(
    fn: Callable[..., Any] | None = None,
    pass_many: bool = False,
    pass_original: bool = False,
) -> Callable[..., Any]:
    
    return set_hook(fn, POST_DUMP, many=pass_many, pass_original=pass_original)


def pre_load(
    fn: Callable[..., Any] | None = None, pass_many: bool = False
) -> Callable[..., Any]:
    
    return set_hook(fn, PRE_LOAD, many=pass_many)


def post_load(
    fn: Callable[..., Any] | None = None,
    pass_many: bool = False,
    pass_original: bool = False,
) -> Callable[..., Any]:
    
    return set_hook(fn, POST_LOAD, many=pass_many, pass_original=pass_original)


def set_hook(
    fn: Callable[..., Any] | None, tag: str, many: bool = False, **kwargs: Any
) -> Callable[..., Any]:
    
    # Allow using this as either a decorator or a decorator factory.
    if fn is None:
        return functools.partial(set_hook, tag=tag, many=many, **kwargs)

    function = cast(Hook, fn)
    try:
        hook_config = function.__hook__
    except AttributeError:
        function.__hook__ = hook_config = defaultdict(list)
    
    if hook_config is not None:
        hook_config[tag].append((many, kwargs))

    return fn
