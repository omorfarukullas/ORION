"""
tests/test_actions.py
=====================
Action function unit tests using mocks.
"""
from unittest.mock import MagicMock, patch
from pathlib import Path
from actions import applications, browser, files, media, screenshots, system


class TestApplicationActions:
    @patch("actions.applications.subprocess.Popen")
    def test_open_application_success(self, mock_popen):
        res = applications.open_application("chrome")
        assert "Opening" in res
        mock_popen.assert_called_once()

    def test_open_application_not_found(self):
        res = applications.open_application("nonexistent_app_12345")
        assert "could not find" in res.lower()

    @patch("actions.applications.psutil.process_iter")
    def test_close_application(self, mock_process_iter):
        mock_proc = MagicMock()
        mock_proc.info = {"pid": 1234, "name": "chrome.exe"}
        mock_process_iter.return_value = [mock_proc]

        res = applications.close_application("chrome")
        assert "Closed Chrome" in res
        mock_proc.terminate.assert_called_once()

    @patch("actions.applications.psutil.process_iter")
    def test_list_running_apps(self, mock_process_iter):
        mock_proc1 = MagicMock()
        mock_proc1.info = {"name": "chrome.exe"}
        mock_proc2 = MagicMock()
        mock_proc2.info = {"name": "python.exe"}
        mock_process_iter.return_value = [mock_proc1, mock_proc2]

        apps = applications.list_running_apps()
        assert "chrome.exe" in apps
        assert "python.exe" in apps


class TestFileActions:
    def test_create_folder(self, tmp_path: Path):
        res = files.create_folder("test_dir", parent=tmp_path)
        assert "Created folder test_dir" in res
        assert (tmp_path / "test_dir").is_dir()

    def test_create_file(self, tmp_path: Path):
        res = files.create_file("test_file.txt", parent=tmp_path)
        assert "Created file test_file.txt" in res
        assert (tmp_path / "test_file.txt").is_file()

    def test_find_file(self, tmp_path: Path):
        test_file = tmp_path / "sample.txt"
        test_file.touch()

        res = files.find_file("sample.txt", search_root=tmp_path)
        assert "Found sample.txt" in res

        res_not_found = files.find_file("missing.txt", search_root=tmp_path)
        assert "Could not find" in res_not_found

    def test_rename_file(self, tmp_path: Path):
        old_file = tmp_path / "old.txt"
        old_file.touch()

        res = files.rename_file("old.txt", "new.txt", parent=tmp_path)
        assert "Renamed old.txt to new.txt" in res
        assert (tmp_path / "new.txt").exists()
        assert not (tmp_path / "old.txt").exists()

    def test_delete_file(self, tmp_path: Path):
        to_delete = tmp_path / "delete_me.txt"
        to_delete.touch()

        res = files.delete_file("delete_me.txt", parent=tmp_path)
        assert "Deleted delete_me.txt" in res
        assert not to_delete.exists()


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

    @patch("actions.system.subprocess.run")
    def test_shutdown(self, mock_run):
        res = system.shutdown()
        assert "shutdown in 5 seconds" in res
        mock_run.assert_called_once_with(["shutdown", "/s", "/t", "5"], check=True)

    @patch("actions.system.subprocess.run")
    def test_restart(self, mock_run):
        res = system.restart()
        assert "restart in 5 seconds" in res
        mock_run.assert_called_once_with(["shutdown", "/r", "/t", "5"], check=True)


class TestMediaActions:
    @patch("actions.media.pyautogui.press")
    def test_media_controls(self, mock_press):
        media.play_pause()
        mock_press.assert_called_with("playpause")

        media.volume_up(steps=2)
        assert mock_press.call_count == 3  # 1 playpause + 2 volumeup

        media.mute()
        mock_press.assert_called_with("volumemute")
