import nonebot.plugin
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, Arg
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.log import logger

default_start = list(nonebot.get_driver().config.command_start)[0]
helper = on_command("help", priority=1, aliases={"帮助"})
# Matcher level info registering, still active in-use
helper.__help_name__ = 'help'
helper.__help_info__ = f'''{default_start}help  # 获取本插件帮助
{default_start}help list  # 展示已加载插件列表
{default_start}help <plugin_name>  # 调取目标插件帮助信息'''


@helper.handle()
async def handle_first_receive(event: Event, matcher: Matcher, args: Message = CommandArg()):
    at = MessageSegment.at(event.get_user_id())
    if args:
        matcher.set_arg("content", args)
    else:
        await matcher.finish(Message(at + f'''欢迎使用Nonebot2 Help Menu
支持使用的前缀：{" ".join(list(nonebot.get_driver().config.command_start))}
{default_start}help  # 获取本插件帮助
{default_start}help list  # 展示已加载插件列表
{default_start}help <plugin_name>  # 调取目标插件帮助信息
'''))


@helper.got("content")
async def get_result(event: Event, content: Message = Arg()):
    at = MessageSegment.at(event.get_user_id())
    args = content.extract_plain_text().split()
    logger.warning(args)
    if str(args[0]).lower() == "list":
        plugin_set = nonebot.plugin.get_loaded_plugins()
        plugin_names = []
        for plugin in plugin_set:
            # plugin.name, then metadata name or legacy help name
            name = f'{plugin.name} | '
            try:
                name += plugin.metadata.name if plugin.metadata.name \
                    else plugin.module.__getattribute__("__help_plugin_name__")
            except:
                name = plugin.name
            # version is optional and legacy
            try:
                version = plugin.module.__getattribute__("__help_version__")
            except:
                version = ""
            plugin_names.append(f'{name} {version}')
        plugin_names.sort()
        newline_char = '\n'
        result = f'已加载插件：\n{newline_char.join(plugin_names)}'
    else:
        try:
            plugin = nonebot.plugin.get_plugin(args[0])
        except AttributeError:
            result = f'{args[0]}插件不存在或未加载，请确认输入的是插件模块名（插件列表的第一部分名称）'
        else:
            results = []
            # if metadata set, use the general usage in metadata instead of legacy __usage__
            if plugin.metadata and plugin.metadata.name and plugin.metadata.usage:
                results.extend([f'{plugin.metadata.name}: {plugin.metadata.description}', plugin.metadata.usage])
            else:
                # legacy __usage__ or __doc__
                try:
                    results.extend([plugin.module.__getattribute__("__help_plugin_name__"),
                                    plugin.module.__getattribute__("__usage__")])
                except:
                    try:
                        results.extend([plugin.name, plugin.module.__doc__])
                    except AttributeError:
                        pass
            # Matcher level help, still legacy since nb2 has no Matcher metadata
            matchers = plugin.matcher
            infos = {}
            index = 1
            for matcher in matchers:
                try:
                    name = matcher.__help_name__
                except AttributeError:
                    name = None
                try:
                    help_info = matcher.__help_info__
                except AttributeError:
                    help_info = matcher.__doc__
                if name and help_info:
                    infos[f'{index}. {name}'] = help_info
                    index += 1
            if index > 1:
                results.extend(["", "序号. 命令名: 命令用途"])
                results.extend(
                    [f'{key}: {value}' for key, value in infos.items()
                     if key and value]
                )
            result = '\n'.join(results)
    await helper.finish(Message().append(at).append(
        MessageSegment.text(result)))
