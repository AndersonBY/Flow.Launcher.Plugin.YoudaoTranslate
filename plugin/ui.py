# -*- coding: utf-8 -*-
# @Author: Bi Ying
# @Date:   2022-08-02 20:03:15
# @Last Modified by:   Bi Ying
# @Last Modified time: 2022-08-03 01:02:09
import re
from typing import List

from flox import Flox

from youdaoai import Translation
from plugin.templates import ICON_PATH
from plugin.extensions import _
import locale


re_contain_english = re.compile(r"[a-zA-Z]+")
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


class Main(Flox):
    items = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.youdao_app_id = self.settings.get("youdao_app_id")
        self.youdao_app_secrect = self.settings.get("youdao_app_secrect")
        self.logger_level("info")

    @staticmethod
    def system_lang():
        lang = locale.getdefaultlocale()
        return lang[0][:2] if lang else "en"

    @staticmethod
    def valid_lang(lang: str) -> bool:
        return lang in LANGUAGES

    def translate(self, src: str, dest: str, query: str):
        try:
            ts = Translation(self.youdao_app_id, self.youdao_app_secrect)
            if src == "auto" and dest == "auto":
                if len(re_contain_english.findall(query)) > 0:
                    sources = ["en"]
                    dest = self.system_lang()
                else:
                    sources = [self.system_lang()]
                    dest = "en"
            elif src == "auto" and dest != "auto":
                sources = ["auto"]
            else:
                sources = [src]

            self.logger.info(f"{sources} -> {dest}: {query}")

            for src in sources:
                translation = ts.translate(query, src, dest)
                translation_text = translation["translation"][0]
                if "phonetic" in translation.get("basic", {}):
                    translation_text += f"[{translation['basic']['phonetic']}]"
                self.add_item(
                    title=translation_text,
                    subtitle="翻译结果",
                    icon=ICON_PATH,
                )
                if "basic" in translation:
                    for explain in translation["basic"].get("explains", []):
                        self.add_item(explain, "简明释义", ICON_PATH)
                if "web" in translation:
                    for web_explain in translation["web"]:
                        self.add_item(",".join(web_explain["value"]), f"网络释义: {web_explain['key']}", ICON_PATH)
        except Exception as error:
            self.add_item(_(str(error)), f"{src} → {dest}   {query}")
        return self.items

    def help_action(self):
        self.add_item("youdao translate", _("<hotkey> <from language> <to language> <text>"))
        return self.items

    def query(self, query_text: str = "") -> List[dict]:
        params = query_text.strip().lower().split(" ")
        if len(params) < 1 or len(params[0]) < 2:
            return self.help_action()

        self.logger.info(f"params: {params}")

        try:
            # no lang_code: <auto> -> <system language>
            if not self.valid_lang(params[0]):
                return self.translate("auto", "auto", query_text)
            # one lang_code: <auto> -> lang_code
            if not self.valid_lang(params[1]):
                return self.translate("auto", params[0], " ".join(params[1:]))
            # 2 lang_codes: lang1 -> lang2
            return self.translate(params[0], params[1], " ".join(params[2:]))
        except IndexError:
            return self.help_action()
