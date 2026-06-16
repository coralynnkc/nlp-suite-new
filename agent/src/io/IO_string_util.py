import logging

logger = logging.getLogger(__name__)


def process_comma_separated_string_list(keywords, case_sensitive=True):
    """Normalize a comma-separated keyword list into a cleaned string and list.

    Accepts either a comma-separated string or an iterable of strings. Trims
    whitespace, drops empties, and lower-cases when ``case_sensitive`` is False.
    Returns ``(cleaned_str, cleaned_list)`` where the string is the cleaned
    items rejoined with ", ".
    """
    if isinstance(keywords, str):
        keywords_list = keywords.split(",")
    else:
        keywords_list = list(keywords)

    if not case_sensitive:
        keywords_list = [k.lower() for k in keywords_list]

    cleaned = [k.strip() for k in keywords_list if k.strip()]
    return ", ".join(cleaned), cleaned
