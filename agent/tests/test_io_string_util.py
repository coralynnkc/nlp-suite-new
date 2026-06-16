from src.io.IO_string_util import process_comma_separated_string_list


def test_comma_string_input():
    s, lst = process_comma_separated_string_list("alpha, beta ,gamma")
    assert lst == ["alpha", "beta", "gamma"]
    assert s == "alpha, beta, gamma"


def test_list_input():
    s, lst = process_comma_separated_string_list(["alpha", " beta ", "gamma"])
    assert lst == ["alpha", "beta", "gamma"]
    assert s == "alpha, beta, gamma"


def test_case_insensitive_lowercases():
    s, lst = process_comma_separated_string_list("Alpha, BETA", case_sensitive=False)
    assert lst == ["alpha", "beta"]
    assert s == "alpha, beta"


def test_case_insensitive_on_list_input():
    # upstream crashed here (called .lower() on the list); must handle lists too
    _, lst = process_comma_separated_string_list(["Alpha", "BETA"], case_sensitive=False)
    assert lst == ["alpha", "beta"]


def test_strips_blank_and_whitespace_entries():
    s, lst = process_comma_separated_string_list("alpha, , ,beta,")
    assert lst == ["alpha", "beta"]
    assert s == "alpha, beta"
