"""
tests/test_entities.py
======================
Entity extractor and command parser tests (Phase 7 & 11).
"""
import pytest
from nlp.entity_extractor import EntityExtractor
from nlp.command_parser import CommandParser, ParsedCommand


class TestEntityExtractor:
    """Tests for EntityExtractor rule-based slot extraction."""

    @pytest.fixture
    def extractor(self) -> EntityExtractor:
        return EntityExtractor()

    def test_open_app_entity(self, extractor: EntityExtractor) -> None:
        res = extractor.extract("open chrome", "OPEN_APP")
        assert res.get("app_name") == "chrome"

        res = extractor.extract("launch visual studio code", "OPEN_APP")
        assert res.get("app_name") == "visual studio code"

    def test_close_app_entity(self, extractor: EntityExtractor) -> None:
        res = extractor.extract("close chrome", "CLOSE_APP")
        assert res.get("app_name") == "chrome"

    def test_web_search_entity(self, extractor: EntityExtractor) -> None:
        res = extractor.extract("search google for python tutorials", "WEB_SEARCH")
        assert res.get("query") == "python tutorials"

        res = extractor.extract("search for machine learning", "WEB_SEARCH")
        assert res.get("query") == "machine learning"

    def test_youtube_search_entity(self, extractor: EntityExtractor) -> None:
        res = extractor.extract("search youtube for lofi music", "YOUTUBE_SEARCH")
        assert res.get("query") == "lofi music"

    def test_open_website_entity(self, extractor: EntityExtractor) -> None:
        res = extractor.extract("open github.com", "OPEN_WEBSITE")
        assert res.get("url") == "github.com"

        res = extractor.extract("go to youtube.com", "OPEN_WEBSITE")
        assert res.get("url") == "youtube.com"

    def test_create_folder_entity(self, extractor: EntityExtractor) -> None:
        res = extractor.extract("create a folder called AI Projects", "CREATE_FOLDER")
        assert res.get("folder_name") == "AI Projects"

    def test_create_file_entity(self, extractor: EntityExtractor) -> None:
        res = extractor.extract("create a file called notes.txt", "CREATE_FILE")
        assert res.get("file_name") == "notes.txt"

    def test_find_file_entity(self, extractor: EntityExtractor) -> None:
        res = extractor.extract("find file report.pdf", "FIND_FILE")
        assert res.get("file_name") == "report.pdf"

    def test_rename_file_entity(self, extractor: EntityExtractor) -> None:
        res = extractor.extract("rename report.txt to final_report.txt", "RENAME_FILE")
        assert res.get("old_name") == "report.txt"
        assert res.get("new_name") == "final_report.txt"

    def test_delete_file_entity(self, extractor: EntityExtractor) -> None:
        res = extractor.extract("delete file budget.xlsx", "DELETE_FILE")
        assert res.get("file_name") == "budget.xlsx"

    def test_remember_entity(self, extractor: EntityExtractor) -> None:
        res = extractor.extract("remember that my project folder is on Desktop", "REMEMBER")
        assert res.get("key") == "my project folder"
        assert res.get("value") == "on Desktop"

    def test_recall_entity(self, extractor: EntityExtractor) -> None:
        res = extractor.extract("what is my project folder?", "RECALL")
        assert res.get("key") == "my project folder"

    def test_no_entity_intents(self, extractor: EntityExtractor) -> None:
        res = extractor.extract("take a screenshot", "SCREENSHOT")
        assert res == {}

        res = extractor.extract("what time is it", "TIME")
        assert res == {}


class TestCommandParser:
    """Integration tests for CommandParser pipeline."""

    @pytest.fixture
    def parser(self) -> CommandParser:
        return CommandParser()

    def test_command_parser_parse(self, parser: CommandParser) -> None:
        cmd = parser.parse("open chrome")
        assert isinstance(cmd, ParsedCommand)
        assert cmd.intent == "OPEN_APP"
        assert cmd.entities.get("app_name") == "chrome"

    def test_command_parser_time(self, parser: CommandParser) -> None:
        cmd = parser.parse("what time is it")
        assert cmd.intent == "TIME"
        assert cmd.confidence > 0.0
