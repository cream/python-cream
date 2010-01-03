def slugify(s):
    """
    Returns a slug-ready version of ``s``.
    (Lowercases all letters, replaces non-alphanumeric letters with hyphens,
    replaces all whitespace with underscores)
    """
    import re
    return re.sub('[^a-z0-9]', '-', re.sub('\s', '_', s.lower()))
