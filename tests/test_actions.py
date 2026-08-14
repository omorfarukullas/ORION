"""
tests/test_actions.py
=====================
Action function unit tests using mocks.
"""
from unittest.mock import MagicMock, patch
from actions import applications, browser, media, screenshots, system


class TestApplicationActions:
    @patch("actions.applications.subprocess.Popen")
    def test_open_application_success(self, mock_popen):
        res = applications.open_application("chrome")
        self_assert_in = "Opening" in res
        assert self_assert_in
        mock_popen.assert_called_once()

    def test_open_application_not_found(self):
        res = applications.open_application("nonexistent_app_12345")
        assert "could not find" in res.lower()


class TestBrowserActions:
    @patch("actions.browser.webbrowser.open")
    def test_web_search(self, mock_open):
        res = browser.web_search("python tutorials")
        assert "Searching Google" in res
        mock_open.assert_called_once()
        assert "google.com/search?q=python" in mock_open.call_args[0][0]

    @patch("actions.browser.webbrowser.open")
    def test_youtube_search(self, mock_open):
        res = browser.youtube_search("lofi hip hop")
        assert "Searching YouTube" in res
        mock_open.assert_called_once()
        assert "youtube.com/results?search_query=lofi" in mock_open.call_args[0][0]

    @patch("actions.browser.webbrowser.open")
    def test_open_url(self, mock_open):
        res = browser.open_url("github.com")
        assert "Opening https://github.com" in res
        mock_open.assert_called_once_with("https://github.com")


class TestScreenshotActions:
    @patch("actions.screenshots.pyautogui.screenshot")
    def test_take_screenshot(self, mock_screenshot, tmp_path):
        mock_img = MagicMock()
        mock_screenshot.return_value = mock_img

        res = screenshots.take_screenshot(save_dir=tmp_path)
        assert "Screenshot saved as" in res
        mock_screenshot.assert_called_once()
        mock_img.save.assert_called_once()


class TestSystemActions:
    @patch("actions.system.psutil.cpu_percent", return_value=25.0)
    def test_get_cpu_usage(self, mock_cpu):
        res = system.get_cpu_usage()
        assert "25 percent" in res

    @patch("actions.system.psutil.virtual_memory")
    def test_get_ram_usage(self, mock_vm):
        mock_mem = MagicMock()
        mock_mem.used = 8 * (1024**3)
        mock_mem.total = 16 * (1024**3)
        mock_vm.return_value = mock_mem

        res = system.get_ram_usage()
        assert "8.0 GB of 16.0 GB RAM" in res

    @patch("actions.system.psutil.sensors_battery")
    def test_get_battery_status(self, mock_battery):
        mock_bat = MagicMock()
        mock_bat.percent = 85
        mock_bat.power_plugged = True
        mock_battery.return_value = mock_bat

        res = system.get_battery_status()
        assert "85 percent, charging" in res


class TestMediaActions:
    @patch("actions.media.pyautogui.press")
    def test_media_controls(self, mock_press):
        media.play_pause()
        mock_press.assert_called_with("playpause")

        media.volume_up(steps=2)
        assert mock_press.call_count == 3  # 1 playpause + 2 volumeup

        media.mute()
        mock_press.assert_called_with("volumemute")
