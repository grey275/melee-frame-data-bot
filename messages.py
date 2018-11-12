import yaml

import discord

from config import Config


def _fetchRawMsgs(message_file):
    with open(message_file, 'r') as f:
        msg_dict = yaml.load(f.read())
    return msg_dict


_RAW_MSGS = _fetchRawMsgs(Config.message_file)


def _makeEmbedOBJ(fields={}, **embed_info):
    embed = discord.Embed(**embed_info)
    for field in fields:
        embed.add_field(**field)
    return embed


def build(key, **info):
    raw_msg = _RAW_MSGS[key]
    output = list()
    if isinstance(raw_msg, str):
        output.append({"content": raw_msg.format(**info)})
    else:
        output.append({"embed": _makeEmbedOBJ(**raw_msg)})
    return output


HELP = build("Help", contributor_list=Config.contributor_list)
NO_COMMAND = build("NoCommand")
INFO = build("Info")
