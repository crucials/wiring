import discord

from typing import Union


PartialMessageableChannel = Union[discord.TextChannel, discord.VoiceChannel,
                                  discord.StageChannel, discord.Thread,
                                  discord.DMChannel, discord.PartialMessageable,
                                  discord.CategoryChannel, discord.ForumChannel]
MessageableChannel = Union[PartialMessageableChannel, discord.GroupChannel]
