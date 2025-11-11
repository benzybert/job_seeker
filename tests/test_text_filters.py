from job_agent_shared.text import combine_text, match_filters


def test_combine_and_match():
    text = combine_text(["Backend Engineer", "Tel Aviv", "Python APIs"])
    assert match_filters(text, include_any=["python"], include_all=["tel aviv"], exclude_any=["manager"])
    assert not match_filters(text, include_any=["java"], include_all=[], exclude_any=[])


