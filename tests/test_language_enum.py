from etsy_python.v3.enums.Language import Language


class TestLanguage:
    def test_supported_language_codes_match_iso_639_1(self):
        # Every member's value is its ISO 639-1 two-letter code and matches
        # its name in lowercase. This catches accidental rename/value drift.
        for member in Language:
            assert member.value == member.name.lower()
            assert len(member.value) == 2

    def test_expected_languages_are_present(self):
        expected = {"en", "de", "es", "fr", "it", "ja", "nl", "pl", "pt", "ru"}
        assert {m.value for m in Language} == expected
