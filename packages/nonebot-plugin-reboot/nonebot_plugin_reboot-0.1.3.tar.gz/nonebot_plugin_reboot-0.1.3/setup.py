# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_reboot']

package_data = \
{'': ['*']}

install_requires = \
['nonebot2>=2.0.0-beta.2,<3.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-reboot',
    'version': '0.1.3',
    'description': 'Reboot your bot by using command',
    'long_description': '# Nonebot-plugin-reboot \n用命令重启 bot \n\n[![asciicast](https://asciinema.org/a/z10hzQ7Pgx4s9TVwj0nAv2TsV.svg)](https://asciinema.org/a/z10hzQ7Pgx4s9TVwj0nAv2TsV)\n\n## :warning:注意事项\n**不支持** `nb-cli`，即 `nb run` 启动方式。\n需要在 bot 目录下使用 `python bot.py` 启动。\n\n重启时直接对子进程使用 `process.terminate()`，如果你的其他插件启动了子进程，请确保它们能在设定的等待时间内正确关闭子进程，否则子进程会变成孤立进程。  \n:warning: Windows 下因系统 API 的限制进程会直接被杀死， **没有** 等待时间。\n\n<hr>  \n\n插件依赖于 `multiprocessing` `spawn` 生成子进程方式工作，支持由 `nb-cli` 生成的 bot.py，或任何显式加载了 `bot.py` 并在加载插件后调用 `nonebot.run` 的启动方式。  \n\n不支持 `nb run` 启动，因为 `nb run` 使用 `importlib` 在函数内加载 `bot.py`，multiprocessing 生成子进程时不会运行 `bot.py`，即 nonebot 初始化和加载插件的过程，导致启动失败。  \n\n得益于使用 `spawn` 方式启动，每次重启都相当于重新加载了所有代码。只有这个插件本身或者 `bot.py` 有更新时才需要彻底关闭 bot 重启。\n\n\n## 安装\n通过 nb-cli 安装:  \n`nb plugin install nonebot-plugin-reboot`  \n通过 pip 安装:  \n`pip install nonebot-plugin-reboot`  \n\n\n## 使用\n**超级用户**向机器人**私聊**发送**命令** `重启`, `reboot` 或 `restart`  \n> :warning: 注意命令的 `COMMAND_START`.  \n> 例如 /重启 、 /reboot 、 /restart\n\n\n## 配置项 \n`reboot_load_command`: `bool` \n- 加载内置的 `onebot v11` 重启命令 \n- 可以通过命令 `重启` `reboot` `restart` 触发重启 \n- 默认值: `True` \n\n`reboot_grace_time_limit`: `int`\n- 收到重启命令后等待进程退出的最长时间，超时会强制杀进程\n- 在 Windows 下没有等待时间，会直接杀进程\n- ~~真寻从ctrl+c到彻底退出居然要六秒~~\n- 默认值: `20`\n\n## `bot.py`\n因为使用了 `spawn` 方式启动子进程，默认的 bot.py 会加载两次插件。  \n\n推荐的写法是将 插件加载部分 和 nonebot启动部分 分开，以避免插件在主进程和子进程都加载一遍\n\n~~真寻启动居然要20秒~~\n\n```python\n#\n# 上面省略\n#\n\nif __name__ == "__mp_main__": # 仅在子进程运行的代码\n    # Please DO NOT modify this file unless you know what you are doing!\n    # As an alternative, you should use command `nb` or modify `pyproject.toml` to load plugins\n    # 加载插件\n    nonebot.load_from_toml("pyproject.toml")\n    nonebot.load_plugins("src/plugins")\n    nonebot.load_plugin("nonebot_plugin_xxxxxx")\n    # ...\n\nif __name__ == "__main__": # 仅在主进程运行的代码\n    # nonebot.logger.warning("Always use `nb run` to start the bot instead of manually running!")\n    # 运行 nonebot\n    nonebot.load_plugin("nonebot_plugin_reboot") # 加载重启插件\n    nonebot.run(app="__mp_main__:app")\n```\n\n\n## API\n```python\nrequire("nonebot_plugin_reboot")\nfrom nonebot_plugin_reboot import Reloader\nReloader.reload(delay=5) # 可选参数 5秒后触发重启\n```\n\n\n## 依赖 \n`nonebot2 >= 2.0.0beta.2`  \n\n启用 `reboot_load_command` 时需要以下依赖  \n`nonebot-adapter-onebot`',
    'author': '18870',
    'author_email': 'a20110123@163.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/18870/nonebot-plugin-reboot',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
