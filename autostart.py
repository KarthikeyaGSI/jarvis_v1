"""
Auto-Start Module - Starts agent on system boot
Cross-platform: Windows, Linux, macOS
"""
import os
import sys
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class AutostartManager:
    """Manages automatic startup configuration"""

    def __init__(self):
        self.system = sys.platform
        self.app_path = Path(__file__).parent.parent / "main.py"
        self.python_exe = sys.executable

    def enable(self) -> bool:
        """Enable autostart on system boot"""
        try:
            if self.system == "win32":
                return self._enable_windows()
            elif self.system == "linux":
                return self._enable_linux()
            elif self.system == "darwin":
                return self._enable_macos()
            else:
                logger.error(f"Unsupported platform: {self.system}")
                return False
        except Exception as e:
            logger.error(f"Failed to enable autostart: {e}")
            return False

    def disable(self) -> bool:
        """Disable autostart"""
        try:
            if self.system == "win32":
                return self._disable_windows()
            elif self.system == "linux":
                return self._disable_linux()
            elif self.system == "darwin":
                return self._disable_macos()
            return False
        except Exception as e:
            logger.error(f"Failed to disable autostart: {e}")
            return False

    def is_enabled(self) -> bool:
        """Check if autostart is enabled"""
        if self.system == "win32":
            return self._is_enabled_windows()
        elif self.system == "linux":
            return self._is_enabled_linux()
        return False

    def _enable_windows(self) -> bool:
        """Enable autostart on Windows via registry"""
        import winreg

        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        command = f'"{self.python_exe}" "{self.app_path}" --mode service'

        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, "Marketingkolabs", 0, winreg.REG_SZ, command)
            winreg.CloseKey(key)
            logger.info("Autostart enabled for Windows")
            return True
        except Exception as e:
            logger.error(f"Windows autostart failed: {e}")
            return False

    def _disable_windows(self) -> bool:
        """Disable autostart on Windows"""
        import winreg

        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\Microsoft\Windows\CurrentVersion\Run",
                                0, winreg.KEY_WRITE)
            winreg.DeleteValue(key, "Marketingkolabs")
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return True  # Already disabled
        except Exception as e:
            logger.error(f"Windows autostart disable failed: {e}")
            return False

    def _is_enabled_windows(self) -> bool:
        """Check Windows autostart status"""
        import winreg

        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\Microsoft\Windows\CurrentVersion\Run",
                                0, winreg.KEY_READ)
            winreg.QueryValueEx(key, "Marketingkolabs")
            return True
        except FileNotFoundError:
            return False

    def _enable_linux(self) -> bool:
        """Enable autostart on Linux via .desktop file"""
        autostart_dir = Path.home() / ".config" / "autostart"
        autostart_dir.mkdir(parents=True, exist_ok=True)

        desktop_content = f"""[Desktop Entry]
Type=Application
Name=Marketingkolabs
Exec={self.python_exe} {self.app_path} --mode service
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
"""
        desktop_file = autostart_dir / "marketingkolabs.desktop"
        with open(desktop_file, 'w') as f:
            f.write(desktop_content)

        logger.info("Autostart enabled for Linux")
        return True

    def _disable_linux(self) -> bool:
        """Disable autostart on Linux"""
        desktop_file = Path.home() / ".config" / "autostart" / "marketingkolabs.desktop"
        if desktop_file.exists():
            desktop_file.unlink()
        return True

    def _is_enabled_linux(self) -> bool:
        """Check Linux autostart status"""
        desktop_file = Path.home() / ".config" / "autostart" / "marketingkolabs.desktop"
        return desktop_file.exists()

    def _enable_macos(self) -> bool:
        """Enable autostart on macOS via LaunchAgent"""
        launch_agents = Path.home() / "Library" / "LaunchAgents"
        launch_agents.mkdir(parents=True, exist_ok=True)

        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.marketingkolabs.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>{self.python_exe}</string>
        <string>{self.app_path}</string>
        <string>--mode</string>
        <string>service</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""
        plist_file = launch_agents / "com.marketingkolabs.agent.plist"
        with open(plist_file, 'w') as f:
            f.write(plist_content)

        logger.info("Autostart enabled for macOS")
        return True

    def _disable_macos(self) -> bool:
        """Disable autostart on macOS"""
        plist_file = Path.home() / "Library" / "LaunchAgents" / "com.marketingkolabs.agent.plist"
        if plist_file.exists():
            plist_file.unlink()
        return True
