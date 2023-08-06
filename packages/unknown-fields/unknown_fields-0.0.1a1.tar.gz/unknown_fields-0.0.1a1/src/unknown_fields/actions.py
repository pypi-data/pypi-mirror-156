import warnings


def ignore_unknown_fields(cls_, fields, args, kwargs):
    """
    Simply ignore unknown fields
    """
    # Map args to fields first
    kargs = {}
    for i in range(min(len(fields), len(args))):
        kargs[fields[i]] = args[i]
    kargs.update({x: kwargs[x] for x in kwargs if x in fields})
    return [], kargs


def warn_and_ignore(cls_, fields, args, kwargs):
    """
    Warn and then ignore unknown fields
    """
    if len(args) > len(fields):
        warnings.warn("Too many positional arguments")
    else:
        for x in kwargs.keys():
            if x not in fields:
                warnings.warn(f"Unknown keyword argument {x}")
    return ignore_unknown_fields(cls_, fields, args, kwargs)


def catch(cls_, fields, args, kwargs):
    setattr(
        cls_, "unknown_arguments",
        (args[len(fields):], {x: kwargs[x] for x in kwargs.keys() if x not in fields})
            )
    return ignore_unknown_fields(cls_, fields, args, kwargs)

