# Youdao Translate (Flow.Launcher.Plugin.YoudaoTranslate)

Translate plugin that translates between any languages supported by youdao for [Flow Launcher](https://github.com/Flow-Launcher/Flow.Launcher).

![Translate](https://i.imgur.com/QiX5Q1o.gif)

#### About


Plugin uses [youdaoai](https://github.com/AndersonBY/python-youdao-ai) to translate between any supported languages.


### Requirements

Python 3.6 or later installed on your system, with python.exe in your PATH variable and this path updated in the Flow Launcher settings (this is a general requirement to use Python plugins with Flow). As of v1.8, Flow Launcher should take care of the installation of Python for you if it is not on your system.


### Installing

#### Package Manager

Use the `pm install` command from within Flow itself.

#### Manual

Add the Flow.Launcher.Plugin.YoudaoTranslate directory to %APPDATA%\Roaming\FlowLauncher\Plugins\ and restart Flow.

#### Python Package Requirements

There is no requirement to install the packages as they will be packed with the release. 

If you still want to manually pip install them:

The `requirements.txt` file in this repo outlines which packages are needed. This can be found online here on Github, as well as in the local plugin directory once installed (%APPDATA%\Roaming\FlowLauncher\Plugins\YoudaoTranslate-X.X.X\ where X.X.X is the currently installed version)

The easiest way to manually install these packages is to use the following command in a Windows Command Prompt or Powershell Prompt

`pip install -r requirements.txt -t ./lib`

Remember you need to be in the local directory containing the requirements text file.

### Usage

| Keyword                                                          | Description                                 |
| ---------------------------------------------------------------- | ------------------------------------------- |
| `yd {from language} {to language} {words to be translated}` | Translate `words to be translated` from `from language` to `to language` language. Example of usage is `yd en cs hello world` |

Alternatively:
- if you do no supply any language code, your input language will be auto-detected between English and your computer system default language , e.g. `yd 你好`.
- if you just supply one language code, this will be used as the 'to language' and your input will be auto-detected as the 'from language', e.g. `yd ru 你好`

**Full list of supported language codes:**

https://ai.youdao.com/DOCSIRMA/html/%E8%87%AA%E7%84%B6%E8%AF%AD%E8%A8%80%E7%BF%BB%E8%AF%91/API%E6%96%87%E6%A1%A3/%E6%96%87%E6%9C%AC%E7%BF%BB%E8%AF%91%E6%9C%8D%E5%8A%A1/%E6%96%87%E6%9C%AC%E7%BF%BB%E8%AF%91%E6%9C%8D%E5%8A%A1-API%E6%96%87%E6%A1%A3.html

### Problems, errors and feature requests

Open an issue in this repo.
