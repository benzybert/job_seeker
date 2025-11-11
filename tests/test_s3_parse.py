import pytest
from job_agent_shared.s3 import S3Url


def test_parse_s3_url():
    url = "s3://resumes/backend.pdf"
    s3 = S3Url.parse(url)
    assert s3.bucket == "resumes"
    assert s3.key == "backend.pdf"


def test_parse_invalid():
    with pytest.raises(ValueError):
        S3Url.parse("http://resumes/backend.pdf")


