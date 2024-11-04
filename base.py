import discord
import pickle
import os
import re
from time import time
from datetime import datetime
import shutil

game_file_name = "/root/game_data.bin"
conf_file_name = "/root/conf_data.bin"

header = 'pn'
win_K, lose_K= 1, 0
default_rate = 1500
K = 64
lose_hosei = 2/3

def backup_all_data():
    year = datetime.now().year
    month = datetime.now().month
    day = datetime.now().day
    hour = datetime.now().hour
    minute = datetime.now().minute
    path = "/GoogleDrive/discord_backup/{0}/{1}/{2}/{3}/{4}/".format(year,month,day,hour,minute)
    os.makedirs(path)
    shutil.copy2(game_file_name, path)
    shutil.copy2(conf_file_name, path)
    print("バックアップ完了")

async def file_open(file, message, all=False):
    if os.path.exists(file):
        data = {}
        with open(file, "rb") as f:
            data = pickle.load(f)
            f.close()
        if message.guild.id in data and not all:
            return data[message.guild.id]
        elif all:
            return data
        else:
            return {}
    else:
        return {}

async def file_save(file, message, data):
    data_all = await file_open(file, message, all=True)
    data_all[message.guild.id] = data
    with open(file, "wb") as f:
        pickle.dump(data_all, f)
        f.close()
    return 0

async def save(embed, message):
    data = await file_open(game_file_name, message)
    if embed != {}:
        imposters = []
        crewmates = []
        members = {}
        if "members" in data:
            members = data["members"]
        win = embed.description.split("\n")[-1].split("won as ")[-1] == "Crewmate"
        if win:
            players = embed.description.split("\n")[-1].split(" won as")[0].split(",")
            for player in players:
                crewmates.append(re.sub("\\D", "", player))
            if len(embed.fields) > len(crewmates):
                for field in embed.fields:
                    i = field.value.find("<@")
                    player = re.sub("\\D", "", field.value[i:-1])
                    if not(player in crewmates): imposters.append(re.sub("\\D", "", player))
            else:
                print("エラー終了")
                return
        else:
            players = embed.description.split("\n")[-1].split(" won as")[0].split(",")
            for player in players:
                imposters.append(re.sub("\\D", "", player))
            if len(embed.fields) > len(imposters) * 2:
                for field in embed.fields:
                    i = field.value.find("<@")
                    player = re.sub("\\D", "", field.value[i:-1])
                    if not(player in imposters): crewmates.append(re.sub("\\D", "", player))
            else:
                print("エラー終了")
                return
        if len(crewmates) > len(imposters) and len(imposters) > 0:
            ave_crewmate, ave_imposter = 0, 0
            for crewmate in crewmates:
                if crewmate in members:
                    ave_crewmate += members[crewmate]
                else:
                    ave_crewmate += default_rate
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
                for imposter in imposters:
                    rate = default_rate
                    if imposter in members: rate = members[imposter]
                    members[imposter] = rate + K * lose_hosei * (lose_K - (1 / (1 + 10 ** (-(rate - ave_crewmate) / 400))))
            else:
                for imposter in imposters:
                    rate = default_rate
                    if imposter in members: rate = members[imposter]
                    members[imposter] = rate + K * (win_K - (1 / (1 + 10 ** (-(rate - ave_crewmate) / 400))))
                for crewmate in crewmates:
                    rate = default_rate
                    if crewmate in members: rate = members[crewmate]
                    members[crewmate] = rate + K * lose_hosei * (lose_K - (1 / (1 + 10 ** (-(rate - ave_imposter) / 400))))
            games = []
            if "games" in data:
                games = data["games"]
                game = {"id": games[-1]["id"]+1,"win": win, "imposter": imposters, "crewmate": crewmates, "date": time()}
            else:
                game = {"id": 1,"win": win, "imposter": imposters, "crewmate": crewmates, "date": time()}
            games.append(game)
            data["members"] = members
            data["games"] = games
            await file_save(game_file_name, message, data)
            crewmates_str, imposters_str = [], []
            members = message.guild.members
            for crewmate in crewmates:
                for member in members:
                    if re.sub("\\D", "", crewmate).replace(" ", "") != "":
                        if int(re.sub("\\D", "", crewmate)) == member.id:
                            crewmates_str.append(member.display_name)
            for imposter in imposters:
                for member in members:
                    if re.sub("\\D", "", imposter).replace(" ", "") != "":
                        if int(re.sub("\\D", "", imposter)) == member.id:
                            imposters_str.append(member.display_name)
            print(win, "Imposters", imposters_str, "Crewmates", crewmates_str)
            await message.channel.send(".pn check")
        else:
            await message.channel.send("エラー終了と判断されました。")
    return

async def cleanup(message):
    data = await file_open(game_file_name, message)
    if "members" in data:
        members = data["members"]
        for i in members.copy():
            if i.find("<") != -1 or i.find(">") != -1 or i.find("@") != -1:
                print(i)
                members[re.sub("\\D", "", i)] = members[i]
                members.pop(i)
            elif i.replace(" ","") == "":
                members.pop(i)
        data["members"] = members
        await file_save(game_file_name, message, data)
    if "games" in data:
        games = data["games"]
        for i in games:
            res_im = [int(re.sub("\\D", "", im)) > 9999999999999999999 for im in i["imposter"] if re.sub("\\D", "", im) != ""]
            res_cr = [int(re.sub("\\D", "", cr)) > 9999999999999999999 for cr in i["crewmate"] if re.sub("\\D", "", cr) != ""]
            if True in res_im or True in res_cr:
                games.remove(i)
        data["games"] = games
        await file_save(game_file_name, message, data)
    names = {}
    if "names" in data:
        names = data["names"]
    if message.author.id in names:
        data2 = await load_conf(message)
        if "nick" in data2:
            if data2["nick"] > 0:
                if message.author.display_name != names[message.author.id]:
                    try:
                        await message.author.edit(nick=names[message.author.id])
                        print("Display name has automatically changed.", message.author.display_name, names[message.author.id])
                    except:
                        pass
    else:
        names[message.author.id] = message.author.display_name
    data["names"] = names
    await file_save(game_file_name, message, data)
    if not("clean_done" in data):
        members = {}
        if "games" in data:
            games = data["games"]
            for game in games:
                ave_imposter, ave_crewmate = 0, 0
                for crewmate in game["crewmate"]:
                    if crewmate in members:
                        ave_crewmate += members[crewmate]
                    else:
                        ave_crewmate += default_rate
                for imposter in game["imposter"]:
                    if imposter in members:
                        ave_imposter += members[imposter]
                    else:
                        ave_imposter += default_rate
                ave_crewmate, ave_imposter = ave_crewmate/len(game["crewmate"]), ave_imposter/len(game["imposter"])
                print(ave_crewmate, ave_imposter)
                if game["win"]:
                    for crewmate in game["crewmate"]:
                        if not re.sub("\\D", "", crewmate) == "":
                            rate = default_rate
                            if re.sub("\\D", "", crewmate) in members: rate = members[re.sub("\\D", "", crewmate)]
                            members[re.sub("\\D", "", crewmate)] = rate + K * (win_K - (1 / (1 + 10 ** (-(rate - ave_imposter) / 400))))
                    for imposter in game["imposter"]:
                        if not re.sub("\\D", "", imposter) == "":
                            rate = default_rate
                            if re.sub("\\D", "", imposter) in members: rate = members[re.sub("\\D", "", imposter)]
                            members[re.sub("\\D", "", imposter)] = rate + K * lose_hosei * (lose_K - (1 / (1 + 10 ** (-(rate - ave_crewmate) / 400))))
                else:
                    for crewmate in game["crewmate"]:
                        if not re.sub("\\D", "", crewmate) == "":
                            rate = default_rate
                            if crewmate in members: rate = members[re.sub("\\D", "", crewmate)]
                            members[re.sub("\\D", "", crewmate)] = rate + K * lose_hosei * (lose_K - (1 / (1 + 10 ** (-(rate - ave_imposter) / 400))))
                    for imposter in game["imposter"]:
                        if not re.sub("\\D", "", imposter) == "":
                            rate = default_rate
                            if re.sub("\\D", "", imposter) in members: rate = members[re.sub("\\D", "", imposter)]
                            members[re.sub("\\D", "", imposter)] = rate + K * (win_K - (1 / (1 + 10 ** (-(rate - ave_crewmate) / 400))))
        print(members)
        data["members"] = members
        data["clean_done"] = True
        print("Clean Up Done.")
        await file_save(game_file_name, message, data)
    data = await file_open(conf_file_name, message)
    if data == {}:
        data = {
            "newyear": False,
            "newyear_id": 0,
            "vote": False,
            "vote_time": "00:00",
            "vote_id": 0
        }
        await file_save(conf_file_name, message, data)

async def load_conf(message):
    return await file_open(conf_file_name, message)

async def save_conf(message, data):
    return await file_save(conf_file_name, message, data)

def time_to_str(t):
    tmp = t
    strt = ""
    if tmp == 0:
        strt = "0s"
    else:
        if tmp >= 60*60*24*365:
            strt += str(int(tmp / (60*60*24*365)))+"y"
            tmp = tmp % (60*60*24*365)
        if tmp >= 60*60*24*30:
            strt += str(int(tmp / (60*60*24*30)))+"M"
            tmp = tmp % (60*60*24*30)
        if tmp >= 60*60*24*7:
            strt += str(int(tmp / (60*60*24*7)))+"w"
            tmp = tmp % (60*60*24*7)
        if tmp >= 60*60*24:
            strt += str(int(tmp / (60*60*24)))+"d"
            tmp = tmp % (60*60*24)
        if tmp >= 60*60:
            strt += str(int(tmp / (60*60)))+"h"
            tmp = tmp % (60*60)
        if tmp >= 60:
            strt += str(int(tmp / 60))+"m"
            tmp = tmp % 60
        if tmp > 0:
            strt += str(tmp)+"s"
    return strt

def time_to_str_jp(t):
    tmp = t
    strt = ""
    if tmp = 0:
        strt = "0s"
    else:
        if tmp >= 60*60*24*365:
            strt += str(int(tmp / (60*60*24*365)))+"年"
            tmp = tmp % (60*60*24*365)
        elif tmp >= 60*60*24*30:
            strt += str(int(tmp / (60*60*24*30)))+"ヶ月"
            tmp = tmp % (60*60*24*30)
        elif tmp >= 60*60*24*7:
            strt += str(int(tmp / (60*60*24*7)))+"週間"
            tmp = tmp % (60*60*24*7)
        elif tmp >= 60*60*24:
            strt += str(int(tmp / (60*60*24)))+"日"
            tmp = tmp % (60*60*24)
        elif tmp >= 60*60:
            strt += str(int(tmp / (60*60)))+"時間"
            tmp = tmp % (60*60)
        elif tmp >= 60:
            strt += str(int(tmp / 60))+"分"
            tmp = tmp % 60
        elif tmp > 0:
            strt += str(tmp)+"秒"
    return strt

def str_to_time(strt):
    t = 0
    if strt.find("y") != -1:
        t += int(strt.split("y")[0]) * (60*60*24*365)
        strt = strt.replace(strt.split("y")[0]+"y", "")
    if strt.find("M") != -1:
        t += int(strt.split("M")[0]) * (60*60*24*30)
        strt = strt.replace(strt.split("M")[0]+"M", "")
    if strt.find("w") != -1:
        t += int(strt.split("w")[0]) * (60*60*24*7)
        strt = strt.replace(strt.split("w")[0]+"M", "")
    if strt.find("d") != -1:
        t += int(strt.split("d")[0]) * (60*60*24)
        strt = strt.replace(strt.split("d")[0]+"d", "")
    if strt.find("h") != -1:
        t += int(strt.split("h")[0]) * (60*60)
        strt = strt.replace(strt.split("h")[0]+"h", "")
    if strt.find("m") != -1:
        t += int(strt.split("m")[0]) * (60)
        strt = strt.replace(strt.split("m")[0]+"m", "")
    if strt.find("s") != -1:
        t += int(strt.split("s")[0])
        strt = strt.replace(strt.split("s")[0]+"s", "")
    return t

def bubble_sort(keys, values, i, remain):
    if remain == 1:
        return keys, values
    elif i == remain - 1:
        return bubble_sort(keys, values, 0, remain - 1)
    else:
        if values[i] < values[i+1]:
            keys[i], keys[i+1] = keys[i+1], keys[i]
            values[i], values[i+1] = values[i+1], values[i]
        return bubble_sort(keys, values, i+1, remain)
