import discord
from disbot import base

role=804272949527183381

async def lock_start(message):
    members = message.guild.members
    roles = discord.utils.get(message.guild.roles, name="Mute")
    for member in members:
        await member.add_roles(roles)

async def lock_stop(message):
    members = message.guild.members
    roles = discord.utils.get(message.guild.roles, name="Mute")
    for member in members:
        await member.remove_roles(roles)

async def lockdown(message):
    cmds = message.content.split(" ")
    if message.author == message.guild.owner:
        if len(cmds) > 2:
            if cmds[2] == "start":
                await lock_start(message)
            elif cmds[2] == "stop":
                await lock_stop(message)
