from services.ingestor.app.pipelines.normalize import normalize_greenhouse, normalize_lever


def test_normalize_greenhouse_min():
    raw = [{"id": 1, "absolute_url": "https://example/jobs/1", "title": "Backend", "location": {"name": "Tel Aviv"}}]
    jobs = normalize_greenhouse("wix", raw)
    assert jobs and jobs[0].source == "greenhouse"
    assert jobs[0].source_id == "1"


def test_normalize_lever_min():
    raw = [{"_id": "abc", "hostedUrl": "https://example/jobs/abc", "text": "Data Engineer", "categories": {"location": "Herzliya"}}]
    jobs = normalize_lever("monday", raw)
    assert jobs and jobs[0].source == "lever"
    assert jobs[0].source_id == "abc"


