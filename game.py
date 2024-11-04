import discord
import re
from disbot import base
from datetime import datetime, timedelta
import math

file_name = "/root/game_data.bin"

header = 'pn'

async def show_games_detail(game, i, message):
    imposters_str, crewmates_str = "", ""
    for imposter in game["imposter"]:
        if re.sub("\\D", "", imposter) != "":
            imposters_str += "<@"+re.sub("\\D", "", imposter)+"> "
    for crewmate in game["crewmate"]:
        if re.sub("\\D", "", crewmate) != "":
            crewmates_str += "<@"+re.sub("\\D", "", crewmate)+"> "
    if game["win"]:
        win = "クルーメイト"
    else:
        win = "インポスター"
    if "date" in game:
        game_time = datetime.fromtimestamp(game["date"])
        embed = discord.Embed(title="No. "+str(game["id"]), description=game_time.strftime("%Y/%m/%d %H:%M:%S")+"\n勝者: "+win)
    else:
        embed = discord.Embed(title="No. "+str(game["id"]), description="時刻データなし\n勝者: "+win)
    embed.add_field(name="クルーメイト", value=crewmates_str)
    embed.add_field(name="インポスター", value=imposters_str)
    await message.channel.send(embed=embed)

async def show_games(message):
    data = await base.file_open(file_name, message)
    games = []
    cmds = message.content.split(" ")
    if "games" in data:
        games = data["games"]
    if len(games) <= 0:
        await message.channel.send("ゲームデータが登録されていません…")
    else:
        count = len(games)
        if len(cmds) > 2:
            if cmds[2].isnumeric():
                i = int(cmds[2])
                games.reverse()
                if (count % 5 == 0 and i <= count / 5) or (count % 5 != 0 and i <= count / 5 + 1) and i > 0:
                    await message.channel.send(str(int(math.ceil(count / 5)))+"ページ中"+str(i)+"ページ目")
                    for x in range((i-1)*5,i*5-1):
                        if x+1 <= count:
                            await show_games_detail(games[x], x, message)
                else:
                    await message.channel.send(str(i)+"ページ目は存在しません。"+str(int(math.ceil(count / 5)))+"ページまであります。")
            elif cmds[2] == "remove":
                if len(cmds) <= 3:
                    embed = discord.Embed(title="ゲームデータ削除", description="保存されているゲームデータを削除することができます。\n使い方: `."+header+" game remove (ID)`")
                    embed.add_field(name="ID", value="ゲームに付けられたID番号です。`."+header+" game (ページ番号)`でIDを確認してください。No.??の数字がIDです。")
                    await message.channel.send(embed=embed)
                elif cmds[3].isnumeric():
                    res = [i["id"] == int(cmds[3]) for i in games]
                    if True in res:
                        for i in range(len(games)):
                            if games[i]["id"] == int(cmds[3]):
                                print("Delete:",games[i])
                                games.pop(i)
                                break
                        await message.channel.send("指定されたゲームの削除が完了しました。")
                        data["games"] = games
                        await base.file_save(file_name, message, data)
                    else:
                        await message.channel.send("そのIDのゲームは存在しません。")
                else:
                    embed = discord.Embed(title="ゲームデータ削除", description="保存されているゲームデータを削除することができます。\n使い方: `."+header+" game remove (ID)`")
                    embed.add_field(name="ID", value="ゲームに付けられたID番号です。`."+header+" game (ページ番号)`でIDを確認してください。No.??の数字がIDです。")
                    await message.channel.send(embed=embed)
            else:
                embed = discord.Embed(title="ゲームデータ関連", description="ゲームデータを途中のバージョンから保存するようになりました。\nここではゲームデータを確認・削除ができます。\n※AutoMuteUsを使用すると自動で保存されます。\n※ゲームデータの手動追加は`."+header+" add`\n使い方: `."+header+" game (コマンド)`")
                embed.add_field(name="なし", value="上から5つを古い順に表示します。")
                embed.add_field(name="ページ数", value="何ページ目を表示するか指定できます。1ページ最大5ゲームまで表示されます。")
                embed.add_field(name="remove (ID)", value="指定したIDのゲームを削除します。")
                embed.add_field(name="help", value="このヘルプを表示します。")
                await message.channel.send(embed=embed)
        else:
            games.reverse()
            if count >= 5:
                for i in range(5):
                    await show_games_detail(games[i], i, message)
            else:
                for i in range(len(games)):
                    await show_games_detail(games[i], i, message)
