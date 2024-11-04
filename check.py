import discord
import re
from disbot import base

file_name = "/root/game_data.bin"

header = base.header
default_rate = base.default_rate

async def show_check_help(message):
    embed = discord.Embed(title="レートボード", description="使い方 `."+header+" check (コマンド)`\n利用可能コマンドの説明")
    embed.add_field(name="なし", value="全員のレートを表示します。")
    embed.add_field(name="me", value="あなたの点数を表示します。")
    embed.add_field(name="メンション", value="メンションされた人の点数を表示します。")
    embed.add_field(name="help", value="このヘルプを表示します。")
    await message.channel.send(embed=embed)

async def show_check(message):
    data = await base.file_open(file_name, message)
    print("Guild ID:",message.guild.id)
    if data != {}:
        data_members = {}
        if "members" in data:
            data_members = data["members"]
        if len(message.content.split(" ")) == 2:
            embed = discord.Embed(title="レートボード", description="現在のレート状況を確認してみましょう！\n※ここに表示されてない人は全員初期値の"+str(default_rate)+"です。")
            print(data_members)
            keys, values = base.bubble_sort(list(data_members.keys()), list(data_members.values()), 0, len(data_members))
            print(keys, values)
            for i in keys:
                id = int(re.sub("\\D", "", i))
                '''
                member = message.guild.get_member(id)
                try:
                    embed.add_field(name=member.display_name, value=str(data_members[i])+"pt")
                except:
                    pass
                '''
                emoji = ""
                if int(data_members[i]) == int(values[0]):
                    emoji += ":crown:"
                if int(data_members[i]) >= 3000:
                    emoji += ":small_orange_diamond:"
                elif int(data_members[i]) >= 5000:
                    emoji += ":small_blue_diamond:"
                elif int(data_members[i]) >= 8000:
                    emoji += ":large_blue_diamond:"
                elif int(data_members[i]) >= 10000:
                    emoji += ":diamond_shape_with_a_dot_inside:"
                embed.add_field(name=str(int(data_members[i])), value=emoji+"<@"+str(id)+">")
            await message.channel.send(embed=embed)
        elif message.content.split(" ")[2] == "help":
            await show_check_help(message)
        elif message.content.split(" ")[2] == "me":
            id = re.sub("\\D", "", message.author.mention)
            if id in data_members:
                emoji = ""
                if int(data_members[i]) == int(max(list(data_members.values()))):
                    emoji += ":crown:"
                if int(data_members[i]) >= 3000:
                    emoji += ":small_orange_diamond:"
                elif int(data_members[i]) >= 5000:
                    emoji += ":small_blue_diamond:"
                elif int(data_members[i]) >= 8000:
                    emoji += ":large_blue_diamond:"
                elif int(data_members[i]) >= 10000:
                    emoji += ":diamond_shape_with_a_dot_inside:"
                reply = emoji + message.author.mention + " あなたのレートは" +str(int(data_members[id]))+"です。"
            else:
                reply = message.author.mention + " あなたのレートは"+str(int(default_rate))+"です。"
            await message.channel.send(reply)
        elif message.content.split(" ")[2][0] == "<" and message.content.split(" ")[2][-1] == ">":
            id = re.sub("\\D", "", message.content.split(" ")[2])
            if id in data_members:
                emoji = ""
                if int(data_members[id]) == int(max(list(data_members.values()))):
                    emoji += ":crown:"
                if int(data_members[id]) >= 3000:
                    emoji += ":small_orange_diamond:"
                elif int(data_members[id]) >= 5000:
                    emoji += ":small_blue_diamond:"
                elif int(data_members[id]) >= 8000:
                    emoji += ":large_blue_diamond:"
                elif int(data_members[id]) >= 10000:
                    emoji += ":diamond_shape_with_a_dot_inside:"
                reply = emoji + message.content.split(" ")[2] + "さんのレートは" +str(int(data_members[id]))+"です。"
            else:
                reply = message.content.split(" ")[2] + "さんのレートは"+str(int(default_rate))+"です。"
            await message.channel.send(reply)
        else:
            await show_check_help(message)
    else:
        await message.channel.send("現在データがありません…。AutoMuteUsを使ってプレイすることで、確認できるようになります。")
