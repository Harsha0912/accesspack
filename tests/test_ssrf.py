import pytest
from app.fetch import BlockedURLError, InvalidURLError, check_url_allowed

@pytest.mark.parametrize("url", [
    "http://localhost/",
    "http://localhost:8080/foo",
    "https://LOCALHOST/path",
    "http://127.0.0.1/",
    "http://127.0.0.1:9/",
    "http://[::1]/",
])
def test_rejects_localhost(url):
    with pytest.raises((BlockedURLError, InvalidURLError)):
        check_url_allowed(url)

@pytest.mark.parametrize("url", [
    "http://169.254.169.254/",
    "http://169.254.169.254/latest/meta-data/",
    "https://169.254.169.254/latest/meta-data",
])
def test_rejects_metadata_ip(url):
    with pytest.raises(BlockedURLError):
        check_url_allowed(url)

def test_rejects_file_and_data():
    with pytest.raises(BlockedURLError):
        check_url_allowed("file:///etc/passwd")
    with pytest.raises(BlockedURLError):
        check_url_allowed("data:text/html,hi")

def test_allows_example():
    assert check_url_allowed("https://example.com/").startswith("https://example.com")
