import discord
import pickle
import os
import re
from disbot import base
from time import time

file_name = "/root/game_data.bin"

header = base.header
win_K, lose_K= base.win_K, base.lose_K
default_rate = base.default_rate
K = base.K
lose_hosei = base.lose_hosei

async def add_custom(message):
    cmds = message.content.split(" ")
    members = re.findall('"([^"]*)"', message.content)
    print(members)
    if len(members) == 2:
        crewmates = members[0].split(" ")
        imposters = members[1].split(" ")
        if len(crewmates) <= len(imposters):
            await message.channel.send("エラー: クルーメイトの人数がインポスターの人数以下です。")
        elif len(imposters) == 0:
            await message.channel.send("エラー: インポスターがいません。")
        elif len(crewmates) == 0:
            await message.channel.send("エラー: クルーメイトがいません。")
        else:
            im, cr, win, win_err = False, False, False, False
            for i in range(len(crewmates)):
                if crewmates[i][0] == "<" and crewmates[i][-1] == ">":
                    crewmates[i] = re.sub("\\D", "", crewmates[i])
                else:
                    await message.channel.send("エラー: クルーメイト内に関係のない文字が入っています。")
                    cr = True
                    break
            for i in range(len(imposters)):
                if imposters[i][0] == "<" and imposters[i][-1] == ">":
                    imposters[i] = re.sub("\\D", "", imposters[i])
                else:
                    await message.channel.send("エラー: インポスター内に関係のない文字が入っています。")
                    im = True
                    break
            if cmds[-1].lower() == "i":
                win = False
            elif cmds[-1].lower() == "c":
                win = True
            else:
                await message.channel.send("エラー: 勝敗結果に関係のない文字が入っています。")
                win_err = True
            if not (im or cr or win_err):
                data = await base.file_open(file_name, message)
                members = {}
                if "members" in data:
                    members = data["members"]
                crewmates_str, imposters_str = "", ""
                ave_crewmate, ave_imposter = 0, 0
                for crewmate in crewmates:
                    if crewmate in members:
                        ave_crewmate += members[crewmate]
                    else:
                        ave_crewmate += 1500
                for imposter in imposters:
                    if imposter in members:
                        ave_imposter += members[imposter]
                    else:
                        ave_imposter += default_rate
                ave_crewmate, ave_imposter = ave_crewmate/len(crewmates), ave_imposter/len(imposters)
                if win:
                    for crewmate in crewmates:
                        rate = default_rate
                        if crewmate in members: rate = members[crewmate]
                        members[crewmate] = rate + K * (win_K - (1 / (1 + 10 ** (-(rate - ave_imposter) / 400))))
                        crewmates_str += "<@" + crewmate + ">, "
                    for imposter in imposters:
                        rate = default_rate
                        if imposter in members: rate = members[imposter]
                        members[imposter] = rate + K * lose_hosei * (lose_K - (1 / (1 + 10 ** (-(rate - ave_crewmate) / 400))))
                        imposters_str += "<@" + imposter + ">, "
                    embed = discord.Embed(title="カスタムゲーム", description="ゲーム結果を保存しました\n勝者: クルーメイト")
                else:
                    for imposter in imposters:
                        rate = default_rate
                        if imposter in members: rate = members[imposter]
                        members[imposter] = rate + K * (win_K - (1 / (1 + 10 ** (-(rate - ave_crewmate) / 400))))
                        imposters_str += "<@" + imposter + ">, "
                    for crewmate in crewmates:
                        rate = default_rate
                        if crewmate in members: rate = members[crewmate]
                        members[crewmate] = rate + K * lose_hosei * (lose_K - (1 / (1 + 10 ** (-(rate - ave_imposter) / 400))))
                        crewmates_str += "<@"+ crewmate + ">, "
                    embed = discord.Embed(title="カスタムゲーム", description="ゲーム結果を保存しました\n勝者: インポスター")
                embed.add_field(name="クルーメイト", value=crewmates_str)
                embed.add_field(name="インポスター", value=imposters_str)
                await message.channel.send(embed=embed)
                games = []
                if "games" in data:
                    games = data["games"]
                    game = {"id": games[-1]["id"]+1,"win": win, "imposter": imposters, "crewmate": crewmates, "date": time()}
                else:
                    game = {"id": 1,"win": win, "imposter": imposters, "crewmate": crewmates, "date": time()}
                games.append(game)
                data["members"] = members
                data["games"] = games
                data_all = await base.file_open(file_name, message, all=True)
                data_all[message.guild.id] = data
                with open(file_name, "wb") as f:
                    pickle.dump(data_all, f)
                    f.close()
    else:
        await add_custom_help(message)

async def add_custom_help(message):
    embed = discord.Embed(title="カスタムゲーム", description="ゲームを手動入力できます。\n使い方 `."+header+" add (クルーメイト) （インポスター） （i/c）`")
    embed.add_field(name="クルーメイト", value="クルーメイトをメンションして全員を`\"`で囲んでください")
    embed.add_field(name="インポスター", value="インポスターををメンションして全員を`\"`で囲んでください")
    embed.add_field(name="i/c", value="どちらが勝利したか入力してください。iはインポスター、cはクルーメイト")
    await message.channel.send(embed=embed)
