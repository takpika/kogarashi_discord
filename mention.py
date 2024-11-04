import discord
import json
import os

id = 783630664544682015

path = "/root/ban_words.json"
ban_words = []
if os.path.exists(path):
    with open(path, "r") as f:
        data = json.load(f)
        f.close()
    ban_words = data["words"]

async def mention(message):
    if message.guild.id == id:
        tmp = message.content.lower()
        tmp = tmp.replace(" ", "")
        tmp = tmp.replace("@everyone", "")
        tmp = tmp.replace("@here", "")
        for i in message.mentions:
            tmp = tmp.replace(i.mention, "")
        if len(tmp) == 0:
            print("Delete")
            await message.delete()
        else:
            tmp = message.content.replace(" ", "").replace("　", "")
            if True in [word in tmp for word in ban_words]:
                await message.delete()
                await message.channel.send("指定された禁止ワードを含んでいたため、メッセージを削除しました。")
