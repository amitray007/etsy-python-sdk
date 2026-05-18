from etsy_python.v3.exceptions.BaseAPIException import BaseAPIException
from etsy_python.v3.exceptions.RequestException import RequestException
from etsy_python.v3.resources.Response import Response


class TestBaseAPIExceptionStr:
    def test_formats_all_fields(self):
        exc = BaseAPIException(
            code=400, error="bad_request", error_description="missing field", type="ERROR"
        )
        s = str(exc)
        assert "code = 400" in s
        assert "error = bad_request" in s
        assert "error_description = missing field" in s
        assert "type = ERROR" in s

    def test_handles_none_defaults(self):
        exc = BaseAPIException(code=500)
        s = str(exc)
        assert "code = 500" in s
        assert "error = None" in s
        assert "type = ERROR" in s


class TestRequestExceptionStr:
    def test_prefixes_etsy_marker(self):
        exc = RequestException(code=429, error="rate_limit_exceeded", rate_limits={"X-Limit-Per-Day": 5000})
        s = str(exc)
        assert s.startswith("[EtsyRequestException]")
        assert "code = 429" in s
        assert "error = rate_limit_exceeded" in s


class TestResponseStr:
    def test_includes_code_and_message(self):
        resp = Response(200, "ok")
        s = str(resp)
        assert s == "[EtsyResponse] [code = 200] [message = ok]"
