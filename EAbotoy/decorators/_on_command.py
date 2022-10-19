from typing import List, Union, Dict

from ..model import WeChatMsg
from ..collection import MsgTypes


def on_command(commands: Union[Dict[str, str], List[str], str]):
    """匹配命令内容"""

    def deco(func):
        async def inner(ctx: WeChatMsg):
            if not ctx.MsgType == MsgTypes.TextMsg:
                return None
            content = ctx.Content
            if isinstance(commands, str):
                if not content.startswith(commands):
                    return
                arg = content[len(commands):].strip()
                command = commands
            elif isinstance(commands, List):
                pre = content.split(" ")[0]
                if pre not in commands:
                    return None

                command = commands[commands.index(pre)]
                arg = content[len(command):].strip()
            elif isinstance(commands, Dict):
                pre = content.split(" ")[0]
                command = commands.get(pre)
                if command is None:
                    return None
                arg = content[len(command):].strip()
            else:
                return None

            return func(ctx, arg, command)

        return inner

    return deco
