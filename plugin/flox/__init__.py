# -*- coding: utf-8 -*-
# @Author: Bi Ying
# @Date:   2023-10-13 00:50:31
# @Last Modified by:   Bi Ying
# @Last Modified time: 2023-10-13 15:56:48
import traceback
import os
import json
import time
import webbrowser
from datetime import date
import logging
import logging.handlers
from collections.abc import Callable
from pathlib import Path
from typing import Any
from functools import cached_property

from .launcher import Launcher
from .browser import Browser
from .settings import Settings

PLUGIN_MANIFEST = "plugin.json"
FLOW_LAUNCHER_DIR_NAME = "FlowLauncher"
SCOOP_FLOW_LAUNCHER_DIR_NAME = "flow-launcher"
WOX_DIR_NAME = "Wox"
FLOW_API = "Flow.Launcher"
WOX_API = "Wox"
APP_DIR = None
USER_DIR = None
LOCALAPPDATA = Path(os.getenv("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
APPDATA = Path(os.getenv("APPDATA") or Path.home() / "AppData" / "Roaming")
FILE_PATH = os.path.dirname(os.path.abspath(__file__))
CURRENT_WORKING_DIR = Path().cwd()
LAUNCHER_NOT_FOUND_MSG = (
    "Unable to locate Launcher directory\n"
    f"Current working directory: {CURRENT_WORKING_DIR}\n"
    f"FILE_PATH: {FILE_PATH}\n"
)


launcher_dir = None
path = Path(__file__)
if SCOOP_FLOW_LAUNCHER_DIR_NAME.lower() in str(path).lower():
    launcher_name = SCOOP_FLOW_LAUNCHER_DIR_NAME
    API = FLOW_API
elif FLOW_LAUNCHER_DIR_NAME.lower() in str(path).lower():
    launcher_name = FLOW_LAUNCHER_DIR_NAME
    API = FLOW_API
elif WOX_DIR_NAME.lower() in str(path).lower():
    launcher_name = WOX_DIR_NAME
    API = WOX_API
else:
    launcher_name = FLOW_LAUNCHER_DIR_NAME
    API = FLOW_API

while APP_DIR is None or USER_DIR is None:
    if len(path.parts) == 1:
        break
    if path.joinpath("Settings").exists():
        USER_DIR = path
        if USER_DIR.name == "UserData":
            APP_DIR = USER_DIR.parent
        elif str(path).startswith(str(APPDATA)):
            APP_DIR = LOCALAPPDATA.joinpath(launcher_name)
        else:
            APP_DIR = LOCALAPPDATA.joinpath(launcher_name)
        break

    path = path.parent

USER_DIR = USER_DIR or APPDATA / "FlowLauncher"
APP_DIR = APP_DIR or LOCALAPPDATA / "FlowLauncher"
PLUGIN_DIR = Path(__file__).parent.parent.parent

APP_ICONS = APP_DIR.joinpath("Images")
ICON_APP = APP_DIR.joinpath("app.png")
ICON_APP_ERROR = APP_DIR.joinpath(APP_ICONS, "app_error.png")
ICON_BROWSER = APP_DIR.joinpath(APP_ICONS, "browser.png")
ICON_CALCULATOR = APP_DIR.joinpath(APP_ICONS, "calculator.png")
ICON_CANCEL = APP_DIR.joinpath(APP_ICONS, "cancel.png")
ICON_CLOSE = APP_DIR.joinpath(APP_ICONS, "close.png")
ICON_CMD = APP_DIR.joinpath(APP_ICONS, "cmd.png")
ICON_COLOR = APP_DIR.joinpath("color.png")
ICON_CONTROL_PANEL = APP_DIR.joinpath("ControlPanel.png")
ICON_COPY = APP_DIR.joinpath("copy.png")
ICON_DELETE_FILE_FOLDER = APP_DIR.joinpath("deletefilefolder.png")
ICON_DISABLE = APP_DIR.joinpath("disable.png")
ICON_DOWN = APP_DIR.joinpath("down.png")
ICON_EXE = APP_DIR.joinpath("exe.png")
ICON_FILE = APP_DIR.joinpath("file.png")
ICON_FIND = APP_DIR.joinpath("find.png")
ICON_FOLDER = APP_DIR.joinpath("folder.png")
ICON_HISTORY = APP_DIR.joinpath("history.png")
ICON_IMAGE = APP_DIR.joinpath("image.png")
ICON_LOCK = APP_DIR.joinpath("lock.png")
ICON_LOGOFF = APP_DIR.joinpath("logoff.png")
ICON_OK = APP_DIR.joinpath("ok.png")
ICON_OPEN = APP_DIR.joinpath("open.png")
ICON_PICTURES = APP_DIR.joinpath("pictures.png")
ICON_PLUGIN = APP_DIR.joinpath("plugin.png")
ICON_PROGRAM = APP_DIR.joinpath("program.png")
ICON_RECYCLEBIN = APP_DIR.joinpath("recyclebin.png")
ICON_RESTART = APP_DIR.joinpath("restart.png")
ICON_SEARCH = APP_DIR.joinpath("search.png")
ICON_SETTINGS = APP_DIR.joinpath("settings.png")
ICON_SHELL = APP_DIR.joinpath("shell.png")
ICON_SHUTDOWN = APP_DIR.joinpath("shutdown.png")
ICON_SLEEP = APP_DIR.joinpath("sleep.png")
ICON_UP = APP_DIR.joinpath("up.png")
ICON_UPDATE = APP_DIR.joinpath("update.png")
ICON_URL = APP_DIR.joinpath("url.png")
ICON_USER = APP_DIR.joinpath("user.png")
ICON_WARNING = APP_DIR.joinpath("warning.png")
ICON_WEB_SEARCH = APP_DIR.joinpath("web_search.png")
ICON_WORK = APP_DIR.joinpath("work.png")


class Flox(Launcher):
    def __init_subclass__(cls, api=API, app_dir=APP_DIR, user_dir=USER_DIR):
        cls.appdir = APP_DIR
        cls.user_dir = USER_DIR
        cls.api = api
        cls.font_family = "/Resources/#Segoe Fluent Icons"
        cls.issue_item_title = "Report Issue"
        cls.issue_item_subtitle = "Report this issue to the developer"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._debug = False
        self._start = time.time()
        self._results = []
        self._settings = None

    @cached_property
    def browser(self):
        return Browser(self.app_settings)

    def exception(self, exception):
        self.exception_item(exception)
        self.issue_item(exception)

    def _query(self, query):
        self.args = query.lower()

        self.query(query)

    def _context_menu(self, data):
        self.context_menu(data)

    def exception_item(self, exception):
        self.add_item(
            title=exception.__class__.__name__,
            subtitle=str(exception),
            icon=ICON_APP_ERROR,
            method=self.change_query,
            dont_hide=True,
        )

    def issue_item(self, e):
        trace = "".join(traceback.format_exception(type(e), value=e, tb=e.__traceback__)).replace("\n", "%0A")
        self.add_item(
            title=self.issue_item_title,
            subtitle=self.issue_item_subtitle,
            icon=ICON_BROWSER,
            method=self.create_github_issue,
            parameters=[e.__class__.__name__, trace],
        )

    def create_github_issue(self, title, trace, log=None):
        url = self.manifest["Website"]
        if "github" in url.lower():
            issue_body = f"Please+type+any+relevant+information+here%0A%0A%0A%0A%0A%0A%3Cdetails open%3E%3Csummary%3ETrace+Log%3C%2Fsummary%3E%0A%3Cp%3E%0A%0A%60%60%60%0A{trace}%0A%60%60%60%0A%3C%2Fp%3E%0A%3C%2Fdetails%3E"
            url = f"{url}/issues/new?title={title}&body={issue_body}"
        webbrowser.open(url)

    def add_item(
        self,
        title: str,
        subtitle: str = "",
        icon: str | os.PathLike[str] | None = None,
        method: str | Callable[..., Any] | None = None,
        parameters: list[Any] | None = None,
        context: Any = None,
        glyph: str | None = None,
        score: int = 0,
        **kwargs,
    ):
        icon = icon or self.icon
        if not Path(icon).is_absolute():
            icon = str(Path(self.plugindir, icon))
        item = {
            "Title": str(title),
            "SubTitle": str(subtitle),
            "IcoPath": str(icon),
            "ContextData": context,
            "Score": score,
            "JsonRPCAction": {},
        }
        auto_complete_text = kwargs.pop("auto_complete_text", None)

        item["AutoCompleteText"] = auto_complete_text or f"{self.user_keyword} {title}".replace("* ", "")
        if method:
            item["JsonRPCAction"]["method"] = getattr(method, "__name__", method)
            item["JsonRPCAction"]["parameters"] = parameters or []
            item["JsonRPCAction"]["dontHideAfterAction"] = kwargs.pop("dont_hide", False)
        if glyph:
            item["Glyph"] = {}
            item["Glyph"]["Glyph"] = glyph
            font_family = kwargs.pop("font_family", self.font_family)
            if font_family.startswith("#"):
                font_family = str(Path(self.plugindir).joinpath(font_family))
            item["Glyph"]["FontFamily"] = font_family
        for kw in kwargs:
            item[kw] = kwargs[kw]
        self._results.append(item)
        return self._results[-1]

    @cached_property
    def plugindir(self):
        potential_paths = [
            Path.cwd(),
            Path(__file__).resolve().parent,
            PLUGIN_DIR,
        ]

        for potential_path in potential_paths:
            path = Path(potential_path).resolve()
            while True:
                if path.joinpath(PLUGIN_MANIFEST).exists():
                    return str(path)
                if path.parent == path:
                    break

                path = path.parent

        return str(PLUGIN_DIR)

    @cached_property
    def manifest(self):
        with open(os.path.join(self.plugindir, PLUGIN_MANIFEST), "r", encoding="utf-8") as f:
            return json.load(f)

    @cached_property
    def id(self):
        return self.manifest["ID"]

    @cached_property
    def icon(self):
        return self.manifest["IcoPath"]

    @cached_property
    def action_keyword(self):
        action_keywords = self.manifest.get("ActionKeywords")
        if action_keywords:
            return action_keywords[0]
        return self.manifest["ActionKeyword"]

    @cached_property
    def version(self):
        return self.manifest["Version"]

    @cached_property
    def appdata(self):
        return str(self.user_dir)

    @property
    def app_settings(self):
        settings_file = os.path.join(self.appdata, "Settings", "Settings.json")
        try:
            with open(settings_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @property
    def query_search_precision(self):
        return self.app_settings.get("QuerySearchPrecision", "Regular")

    @cached_property
    def user_keywords(self):
        plugin_settings = self.app_settings.get("PluginSettings", {}).get("Plugins", {}).get(self.id, {})
        keywords = plugin_settings.get("ActionKeywords") or plugin_settings.get("UserKeywords")
        if keywords:
            return keywords
        return self.manifest.get("ActionKeywords") or [self.action_keyword]

    @cached_property
    def user_keyword(self):
        return self.user_keywords[0]

    def appicon(self, icon):
        return os.path.join(str(self.appdir), "images", icon + ".png")

    @property
    def applog(self):
        today = date.today().strftime("%Y-%m-%d")
        file = f"{today}.txt"
        return os.path.join(self.appdata, "Logs", self.appversion, file)

    @cached_property
    def appversion(self):
        return os.path.basename(str(self.appdir)).replace("app-", "")

    @cached_property
    def logfile(self):
        file = "plugin.log"
        return os.path.join(self.plugindir, file)

    @cached_property
    def logger(self):
        logger = logging.getLogger(self.id)
        formatter = logging.Formatter("%(asctime)s %(levelname)s (%(filename)s): %(message)s", datefmt="%H:%M:%S")
        for handler in logger.handlers:
            if getattr(handler, "baseFilename", None) == self.logfile:
                break
        else:
            logfile = logging.handlers.RotatingFileHandler(
                self.logfile,
                maxBytes=1024 * 2024,
                backupCount=1,
                encoding="utf-8",
            )
            logfile.setFormatter(formatter)
            logger.addHandler(logfile)
        logger.setLevel(logging.WARNING)
        logger.propagate = False
        return logger

    def logger_level(self, level):
        if level == "info":
            self.logger.setLevel(logging.INFO)
        elif level == "debug":
            self.logger.setLevel(logging.DEBUG)
        elif level == "warning":
            self.logger.setLevel(logging.WARNING)
        elif level == "error":
            self.logger.setLevel(logging.ERROR)
        elif level == "critical":
            self.logger.setLevel(logging.CRITICAL)

    @cached_property
    def name(self):
        return self.manifest["Name"]

    @cached_property
    def author(self):
        return self.manifest["Author"]

    @cached_property
    def settings_path(self):
        dirname = self.name
        setting_file = "Settings.json"
        return os.path.join(self.appdata, "Settings", "Plugins", dirname, setting_file)

    @cached_property
    def settings(self):
        if self._settings is not None:
            return self._settings
        os.makedirs(os.path.dirname(self.settings_path), exist_ok=True)
        return Settings(self.settings_path)

    def browser_open(self, url):
        self.browser.open(url)

    @cached_property
    def python_dir(self):
        plugin_settings = self.app_settings.get("PluginSettings", {})
        return plugin_settings.get("PythonExecutablePath") or plugin_settings.get("PythonDirectory")

    def log(self):
        return self.logger
