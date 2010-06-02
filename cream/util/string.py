def slugify(s):
    """
    Returns a slug-ready version of ``s``.
    (Lowercases all letters, replaces non-alphanumeric letters with hyphens,
    replaces all whitespace with underscores)
    """
    import re
    return re.sub('[^a-z0-9]', '-', re.sub('\s', '_', s.lower()))

def crop_string(s, maxlen, appendix='...'):
    """
    Crop string ``s`` after ``maxlen`` chars and append ``appendix``.
    """
    if len(s) > maxlen:
        return s[:maxlen] + appendix
    else:
        return s
