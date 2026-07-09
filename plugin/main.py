# -*- coding: utf-8 -*-
# @Author: Bi Ying
# @Date:   2022-08-02 20:03:15
# @Last Modified by:   Bi Ying
# @Last Modified time: 2023-10-13 15:13:12
import re
import json
import locale
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from plugin.flox import Flox
from plugin.templates import ICON_PATH
from plugin.extensions import _


re_contain_latin = re.compile(r"[a-zA-Z]+")
LANGUAGES = [
    "zh",
    "zh-chs",
    "zh-cht",
    "en",
    "ja",
    "ko",
    "fr",
    "es",
    "pt",
    "it",
    "ru",
    "vi",
    "de",
    "ar",
    "id",
    "af",
    "bs",
    "bg",
    "yue",
    "ca",
    "hr",
    "cs",
    "da",
    "nl",
    "et",
    "fj",
    "fi",
    "el",
    "ht",
    "he",
    "hi",
    "mww",
    "hu",
    "sw",
    "tlh",
    "lv",
    "lt",
    "ms",
    "mt",
    "no",
    "fa",
    "pl",
    "otq",
    "ro",
    "sr-Cyrl",
    "sr-Latn",
    "sk",
    "sl",
    "sv",
    "ty",
    "th",
    "to",
    "tr",
    "uk",
    "ur",
    "cy",
    "yua",
    "sq",
    "am",
    "hy",
    "az",
    "bn",
    "eu",
    "be",
    "ceb",
    "co",
    "eo",
    "tl",
    "fy",
    "gl",
    "ka",
    "gu",
    "ha",
    "haw",
    "is",
    "ig",
    "ga",
    "jw",
    "kn",
    "kk",
    "km",
    "ku",
    "ky",
    "lo",
    "la",
    "lb",
    "mk",
    "mg",
    "ml",
    "mi",
    "mr",
    "mn",
    "my",
    "ne",
    "ny",
    "ps",
    "pa",
    "sm",
    "gd",
    "st",
    "sn",
    "sd",
    "si",
    "so",
    "su",
    "tg",
    "ta",
    "te",
    "uz",
    "xh",
    "yi",
    "yo",
    "zu",
]
LANGUAGE_ALIASES = {language.lower(): language for language in LANGUAGES}
AUTO_SOURCE = "auto"
CACHE_TTL_SECONDS = 7 * 24 * 60 * 60
CACHE_MAX_ITEMS = 128
REQUEST_TIMEOUT_SECONDS = 4
MIN_AUTO_QUERY_LENGTH = 2
MAX_BASIC_RESULTS = 5
MAX_WEB_RESULTS = 5

YOUDAO_ERROR_MESSAGES = {
    "101": "缺少必填参数或 App ID 无效",
    "102": "不支持的语言类型",
    "103": "翻译文本过长",
    "108": "App ID 无效或服务未开通",
    "202": "签名校验失败，请检查 App Secret",
    "301": "辞典查询失败",
    "401": "账户已经欠费或可用额度不足",
    "411": "访问频率受限，请稍后重试",
}


class YoudaoTranslate(Flox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger_level("info")
        self._translator = None
        self._cache = None

    @staticmethod
    def system_lang():
        lang, _ = locale.getlocale()
        if not lang:
            return "zh"
        lang = lang.replace("-", "_").split("_")[0].lower()
        return lang if YoudaoTranslate.valid_lang(lang) else "zh"

    @staticmethod
    def normalize_lang(lang: str) -> Optional[str]:
        return LANGUAGE_ALIASES.get(lang.lower())

    @staticmethod
    def valid_lang(lang: str) -> bool:
        return YoudaoTranslate.normalize_lang(lang) is not None

    @staticmethod
    def contains_cjk(text: str) -> bool:
        return any(
            "\u3400" <= char <= "\u9fff"
            or "\uf900" <= char <= "\ufaff"
            or "\u3040" <= char <= "\u30ff"
            or "\uac00" <= char <= "\ud7af"
            for char in text
        )

    @staticmethod
    def cache_key(src: str, dest: str, query: str) -> str:
        return json.dumps([src, dest, query], ensure_ascii=False, separators=(",", ":"))

    @property
    def credentials(self) -> Tuple[Optional[str], Optional[str]]:
        return self.settings.get("youdao_app_id"), self.settings.get("youdao_app_secrect")

    @property
    def translator(self):
        if self._translator is None:
            import httpx
            from youdaoai import YoudaoAI
            from youdaoai.client import YoudaoError

            class TimedYoudaoAI(YoudaoAI):
                def __init__(self, app_key: str, app_secret: str, timeout: int = REQUEST_TIMEOUT_SECONDS):
                    super().__init__(app_key, app_secret)
                    self.timeout = timeout

                def _do_request(self, api_path: str, data: dict):
                    headers = {"Content-Type": "application/x-www-form-urlencoded"}
                    response = httpx.post(self.base_url + api_path, data=data, headers=headers, timeout=self.timeout)
                    if int(response.json().get("errorCode", 0)) != 0:
                        raise YoudaoError(response.json())
                    return response

                def translate_raw(self, text: str, from_: str, to_: str) -> Dict[str, Any]:
                    data: Dict[str, Any] = {"q": text, "from": from_, "to": to_}
                    response = self._do_request("api", self._update_payload(data))
                    return response.json()

            app_id, app_secret = self.credentials
            if app_id is None or app_secret is None:
                raise ValueError("请先配置有道 App ID 和 App Secret")
            self._translator = TimedYoudaoAI(app_id, app_secret)
        return self._translator

    @property
    def cache_path(self) -> Path:
        return Path(self.settings_path).parent / "TranslationCache.json"

    @property
    def cache(self) -> Dict[str, Dict[str, Any]]:
        if self._cache is not None:
            return self._cache

        try:
            with open(self.cache_path, "r", encoding="utf-8") as file:
                cache = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            cache = {}

        self._cache = cache if isinstance(cache, dict) else {}
        return self._cache

    def save_cache(self):
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            items = sorted(self.cache.items(), key=lambda item: item[1].get("time", 0), reverse=True)
            self._cache = dict(items[:CACHE_MAX_ITEMS])
            temp_path = self.cache_path.with_suffix(self.cache_path.suffix + f".{os.getpid()}.tmp")
            with open(temp_path, "w", encoding="utf-8") as file:
                json.dump(self._cache, file, ensure_ascii=False, separators=(",", ":"))
            os.replace(temp_path, self.cache_path)
        except OSError as error:
            self.logger.warning("Unable to save translation cache: %s", error)

    def get_cached_translation(self, src: str, dest: str, query: str) -> Optional[Dict[str, Any]]:
        item = self.cache.get(self.cache_key(src, dest, query))
        if not item:
            return None
        if time.time() - item.get("time", 0) > CACHE_TTL_SECONDS:
            return None
        data = item.get("data")
        return data if isinstance(data, dict) else None

    def cache_translation(self, src: str, dest: str, query: str, data: Dict[str, Any]):
        self.cache[self.cache_key(src, dest, query)] = {"time": time.time(), "data": data}
        self.save_cache()

    def add_copy_item(self, title: str, subtitle: str, query: str, score: int):
        self.add_item(
            title=title,
            subtitle=subtitle,
            icon=ICON_PATH,
            method="Flow.Launcher.CopyToClipboard",
            parameters=[title, False, True],
            context=title,
            score=score,
            auto_complete_text=f"{self.user_keyword} {query}".strip(),
        )

    def add_notice(self, title: str, subtitle: str = "", open_settings: bool = False):
        method = "Flow.Launcher.OpenPluginSettingsWindow" if open_settings else None
        parameters = [self.id] if open_settings else []
        self.add_item(title=title, subtitle=subtitle, icon=ICON_PATH, method=method, parameters=parameters)

    def translation_error_message(self, translation: Dict[str, Any]) -> Optional[str]:
        error_code = str(translation.get("errorCode") or translation.get("error_code") or "0")
        if error_code == "0":
            return None
        return YOUDAO_ERROR_MESSAGES.get(error_code, f"有道返回错误码 {error_code}")

    @staticmethod
    def normalize_translation(translation: Any) -> Dict[str, Any]:
        if isinstance(translation, dict):
            return translation

        if hasattr(translation, "model_dump"):
            return translation.model_dump(by_alias=True, exclude_none=True)

        return {}

    def translate_once(self, src: str, dest: str, query: str) -> Dict[str, Any]:
        cached = self.get_cached_translation(src, dest, query)
        if cached is not None:
            self.logger.info("cache hit: %s -> %s: %s", src, dest, query)
            return cached

        translation = self.normalize_translation(self.translator.translate_raw(query, src, dest))
        if self.translation_error_message(translation) is None:
            self.cache_translation(src, dest, query, translation)
        return translation

    def resolve_auto_languages(self, src: str, dest: str, query: str) -> Tuple[List[str], str]:
        system_lang = self.system_lang()
        if src == AUTO_SOURCE and dest == AUTO_SOURCE:
            if self.contains_cjk(query):
                return [AUTO_SOURCE], "en"
            if re_contain_latin.search(query):
                return ["en"], system_lang if system_lang != "en" else "zh"
            return [AUTO_SOURCE], "en"
        if src == AUTO_SOURCE:
            return [AUTO_SOURCE], dest
        return [src], dest

    def translate(self, src: str, dest: str, query: str):
        sources, dest = self.resolve_auto_languages(src, dest, query)
        self.logger.info("%s -> %s: %s", sources, dest, query)

        try:
            for src in sources:
                translation = self.translate_once(src, dest, query)
                error_message = self.translation_error_message(translation)
                if error_message:
                    return self.add_notice(error_message, f"{src} -> {dest}   {query}", open_settings=True)

                translation_text = translation.get("translation", [""])[0]
                if not translation_text:
                    return self.add_notice("没有返回翻译结果", f"{src} -> {dest}   {query}")

                if "phonetic" in translation.get("basic", {}):
                    translation_text += f"[{translation['basic']['phonetic']}]"

                self.add_copy_item(
                    title=translation_text,
                    subtitle="翻译结果 - Enter 复制",
                    query=query,
                    score=100,
                )

                if "basic" in translation:
                    for explain in translation["basic"].get("explains", [])[:MAX_BASIC_RESULTS]:
                        self.add_copy_item(explain, "简明释义 - Enter 复制", query, score=80)
                if "web" in translation:
                    for web_explain in translation["web"][:MAX_WEB_RESULTS]:
                        title = ", ".join(web_explain.get("value", []))
                        subtitle = f"网络释义: {web_explain.get('key', '')} - Enter 复制"
                        self.add_copy_item(title, subtitle, query, score=60)
        except Exception as error:
            module = error.__class__.__module__
            if module.startswith("requests") and error.__class__.__name__ == "Timeout":
                self.add_notice("翻译请求超时", "请稍后重试，或检查网络/代理设置")
            elif module.startswith("requests"):
                self.add_notice("翻译请求失败", str(error))
            elif module.startswith("httpx") and error.__class__.__name__ == "TimeoutException":
                self.add_notice("翻译请求超时", "请稍后重试，或检查网络/代理设置")
            elif module.startswith("httpx"):
                self.add_notice("翻译请求失败", str(error))
            elif error.__class__.__name__ == "YoudaoError":
                response = getattr(error, "error_response", None)
                error_code = str(getattr(response, "error_code", ""))
                message = YOUDAO_ERROR_MESSAGES.get(error_code, f"有道返回错误码 {error_code}")
                self.add_notice(message, f"{', '.join(sources)} -> {dest}   {query}", open_settings=True)
            else:
                self.add_notice(_(str(error)), f"{', '.join(sources)} -> {dest}   {query}")

    def help_action(self):
        self.add_item("yd hello", "自动英译中；也可用 yd en zh hello", ICON_PATH, auto_complete_text="yd hello")
        self.add_item("yd zh en 你好", _("指定源语言和目标语言"), ICON_PATH, auto_complete_text="yd zh en 你好")
        return self._results

    def context_menu(self, data):
        if data:
            self.add_copy_item(data, "复制", data, score=100)

    def query(self, query: str = "") -> List[dict]:
        query_text = query.strip()
        params = query_text.split()
        if not params or len(query_text) < MIN_AUTO_QUERY_LENGTH:
            return self.help_action()

        app_id, app_secret = self.credentials
        if not app_id or not app_secret:
            return self.add_notice("请先配置有道 App ID 和 App Secret", "Enter 打开插件设置", open_settings=True)

        self.logger.info("params: %s", params)

        first_lang = self.normalize_lang(params[0])
        if not first_lang:
            return self.translate(AUTO_SOURCE, AUTO_SOURCE, query_text)

        if len(params) == 1:
            return self.help_action()

        second_lang = self.normalize_lang(params[1])
        if not second_lang:
            text = query_text[len(params[0]):].strip()
            if len(text) < MIN_AUTO_QUERY_LENGTH:
                return self.help_action()
            return self.translate(AUTO_SOURCE, first_lang, text)

        text = query_text[len(params[0]) + len(params[1]) + 1:].strip()
        if len(text) < MIN_AUTO_QUERY_LENGTH:
            return self.help_action()
        return self.translate(first_lang, second_lang, text)
