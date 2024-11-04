import discord
from datetime import date, timedelta, datetime

async def show_ask_help(message):
    embed = discord.Embed(title="アンケート自動ツール", description="アンケートを自動で送信します。\n使い方: `.ask (コマンド)`\n※コマンドなしの場合は今日のアンケートを表示します。")
    embed.add_field(name="today", value="今日のアンケートを表示します。")
    embed.add_field(name="tomorrow", value="明日のアンケートを表示します。")
    embed.add_field(name="help", value="このヘルプを表示します。")
    await message.channel.send(embed=embed)


async def ask_command(message):
    await message.delete()
    year, month, day = "2020", "12", "31"
    cmds = message.content.split(" ")
    if len(cmds) > 1:
        if cmds[1] == "today":
            year, month, day = str(date.today().year), str(date.today().month), str(date.today().day)
            await message.channel.send("---"+year+"年"+month+"月"+day+"日---")
            for i in range(12):
                await message.channel.send(str(i*2)+":00-"+str((i+1)*2)+":00")
        elif cmds[1] == "tomorrow":
            year, month, day = str((date.today()+timedelta(days=1)).year), str((date.today()+timedelta(days=1)).month), str((date.today()+timedelta(days=1)).day)
            await message.channel.send("---"+year+"年"+month+"月"+day+"日---")
            for i in range(12):
                await message.channel.send(str(i*2)+":00-"+str((i+1)*2)+":00")
        elif cmds[1] == "help":
            await show_ask_help(message)
        else:
            await message.channel.send("`"+cmds[1]+"` 未知のコマンドです。")
    else:
        year, month, day = str(date.today().year), str(date.today().month), str(date.today().day)
        await message.channel.send("---"+year+"/"+month+"/"+day+"---")
        for i in range(12):
            await message.channel.send(str(i*2)+":00-"+str((i+1)*2)+":00")
