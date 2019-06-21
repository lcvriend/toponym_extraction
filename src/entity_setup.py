def create_patterns(label, patterns):
    """
    Create patterns to pass to the EntityRuler.

    Arguments
    =========
    :param label: `str`
        Name of the entity label.
    :param patterns: `list` of `dicts`
        Iterable of patterns (usually exact phrase matches as `str`).

    Returns
    =======
    :create_patterns: `list` of `dicts`
    """

    return ({'label': label, 'pattern': p} for p in patterns)
