import enum
from inspect import signature
from typing import Union

from unknown_fields.actions import ignore_unknown_fields, warn_and_ignore, catch


class Action(enum.Enum):
    Ignore = ignore_unknown_fields
    WarnThenIgnore = warn_and_ignore
    Catch = catch


def unknown_fields(cls=None, action: Union[callable, Action] = Action.Ignore):
    """
    Wrapper for dataclasses to take action on unknown __init__ arguments

    :param cls: Class this applies to
    :param action: Action to take during init to handle the fields
    """

    def new_init(cls_, *args, **kwargs):
        args, kwargs = cls_.__unknown_field_action(cls_.__fields, args, kwargs)
        cls_.__org_init(*args, **kwargs)

    def wrapped(cls_, *args, **kwargs):
        cls_.__unknown_field_action = action.value if isinstance(action, Action) else action
        cls_.__fields = list(signature(cls_.__init__).parameters.keys())[1:]
        cls_.__org_init = cls_.__init__
        cls_.__init__ = new_init
        return cls_

    if cls is None:
        return wrapped
    else:
        return wrapped(cls)
