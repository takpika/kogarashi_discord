import discord
from disbot import base
import re
from time import time
from datetime import datetime

header = base.header


async def show_nick(message):
    cmds = message.content.split(" ")
    if len(cmds) > 2:
        if cmds[2] == "help":
            await show_nick_help(message)
        elif cmds[2] == "rename":
            await force_change_nick(message)
        else:
            await change_nick(message)
    else:
        await show_nick_help(message)

async def show_nick_help(message):
    embed = discord.Embed(title="ニックネーム", description="ニックネームを変更できます。\n使い方: `."+header+" nick 使用したいニックネーム`")
    embed.add_field(name="ニックネーム", value="あなたが使用したいニックネームを入力してください。")
    embed.add_field(name="rename", value="ユーザーの名前を変更させることができます（管理者のみ）")
    await message.channel.send(embed=embed)
    data = await base.load_conf(message)
    limit_time, members = 0, {}
    if "nick" in data and "members" in data:
        limit_time = data["nick"]
        members = data["members"]
    if message.author.id in members:
        if members[message.author.id] > int(time()):
            remain = members[message.author.id] - int(time())
            await message.channel.send(message.author.mention + "あなたが次にニックネームを変更できるまであと"+base.time_to_str_jp(remain)+"です。")


async def change_nick(message):
    data = await base.load_conf(message)
    data2 = await base.file_open(base.game_file_name, message)
    limit_time = 0
    if "nick" in data:
        limit_time = data["nick"]
    new_name = message.content.replace("."+header+" nick ", "")
    members = {}
    names = {}
    if "members" in data:
        members = data["members"]
    if "names" in data2:
        names = data2["names"]
    if message.author.id in members:
        if members[message.author.id] > int(time()):
            remain = members[message.author.id] - int(time())
            await message.channel.send(message.author.mention + "まだニックネームを変更できません。次ニックネーム変更できるまであと"+base.time_to_str_jp(remain)+"です。")
        else:
            members[message.author.id] = int(time()) + limit_time
            names[message.author.id] = new_name
            await message.author.edit(nick=new_name)
            await message.channel.send(message.author.mention + "ニックネームを`"+new_name+"`に変更しました。次に変更できるまであと"+base.time_to_str_jp(limit_time)+"です。")
    else:
        members[message.author.id] = int(time()) + limit_time
        names[message.author.id] = new_name
        await message.author.edit(nick=new_name)
        await message.channel.send(message.author.mention + "ニックネームを`"+new_name+"`に変更しました。次に変更できるまであと"+base.time_to_str_jp(limit_time)+"です。")
    data["members"] = members
    data2["names"] = names
    await base.save_conf(message, data)
    await base.file_save(base.game_file_name, message, data2)

async def help_force_change_nick(message):
    embed = discord.Embed(title="強制ニックネーム変更（管理者限定）", description="他ユーザーの名前を変更させることができます。\n使い方: `."+header+" nick rename @メンション 制限 新しいニックネーム`")
    embed.add_field(name="制限", value="時間制限をかけるかどうかを選択してください。(true/false)")
    embed.add_field(name="ニックネーム", value="新しいニックネームを入力してください。")
    await message.channel.send(embed=embed)

async def force_change_nick(message):
    data = await base.load_conf(message)
    data2 = await base.file_open(base.game_file_name, message)
    roles = [i.id for i in message.author.roles]
    limit_time = 0
    if "forcenick" in data:
        limit_time = data["forcenick"]
    admins = []
    members = {}
    names = {}
    if "members" in data:
        members = data["members"]
    if "names" in data2:
        names = data2["names"]
    if "admin" in data:
        admins = data["admin"]
    if (len(admins) == 0 or True in [i in roles for i in admins]) or message.author == message.guild.owner:
        cmds = message.content.split(" ")
        if len(cmds) < 5:
            help_force_change_nick(message)
        else:
            if cmds[3][0] == "<" and cmds[3][-1]:
                user_id = int(re.sub("\\D", "", cmds[3]))
                if cmds[4].lower() == "true" or cmds[4].lower() == "false":
                    punishment = cmds[4].lower() == "true"
                    new_name = message.content.replace("."+header+" nick rename "+cmds[3]+" "+cmds[4]+" ", "")
                    print(user_id,punishment,new_name)
                    user = message.guild.get_member(user_id)
                    print(user, user_id, type(user_id))
                    names[user_id] = new_name
                    await message.channel.send("<@!"+str(user_id)+">あなたのニックネームが`"+new_name+"`に変更されました。")
                    if punishment:
                        members[user_id] = int(time()) + limit_time
                        await message.channel.send("次に変更できるまで、あと"+base.time_to_str_jp(limit_time)+"です。")
                else:
                    await message.channel.send("エラー: trueかfalseで入力してください。")
            else:
                await message.channel.send("エラー: ユーザーを選択してください。")
        data["members"] = members
        data2["names"] = names
        await base.save_conf(message, data)
        await base.file_save(base.game_file_name, message, data2)
    else:
        await message.channel.send(message.author.mention + "このコマンドを実行する権限がありません。")
