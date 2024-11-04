import discord
from disbot import base
import re

header = base.header

async def show_help(message):
    embed = discord.Embed(title="設定", description="設定を変更します。\n使い方: `."+header+" setting (コマンド)`")
    embed.add_field(name="show", value="設定の全体を表示します。")
    embed.add_field(name="help", value="このヘルプを表示します。")
    embed.add_field(name="vote", value="アンケート機能を使用するか設定します。")
    embed.add_field(name="newyear", value="新年の挨拶機能を使用するか設定します。")
    embed.add_field(name="nick", value="ニックネームを変更してから次に変更できるまでの時間")
    embed.add_field(name="forcenick", value="管理者が特別に与えることができる制限の時間")
    embed.add_field(name="admin", value="このbotの管理者ロールを設定します。")
    await message.channel.send(embed=embed)

async def show_conf(message):
    cmds = message.content.split(" ")
    roles = [i.id for i in message.author.roles]
    data = await base.load_conf(message)
    if len(cmds) > 2:
        if cmds[2] == "help":
            await show_help(message)
        elif cmds[2] == "show":
            await show_conf_all(message)
        elif cmds[2] == "newyear" or cmds[2] == "vote" or cmds[2] == "nick" or cmds[2] == "admin" or cmds[2] == "forcenick":
            admins = []
            if "admin" in data:
                admins = data["admin"]
            if (len(admins) == 0 or True in [i in roles for i in admins]) or message.author == message.guild.owner:
                if cmds[2] == "newyear":
                    await newyear(message)
                elif cmds[2] == "vote":
                    await vote(message)
                elif cmds[2] == "nick":
                    await nick(message)
                elif cmds[2] == "admin":
                    await admin(message)
                elif cmds[2] == "forcenick":
                    await forcenick(message)
                elif cmds[2] == "mention":
                    await mention(message)
            else:
                await message.channel.send(message.author.mention + "設定を変更する権限を持っていません。")
        else:
            await show_help(message)
    else:
        await show_help(message)

async def show_conf_all(message):
    data = await base.load_conf(message)
    print(data)
    embed = discord.Embed(title="設定表示", description="")
    if "vote" in data and "vote_time" in data and "vote_id" in data:
        if data["vote"]:
            embed.add_field(name="アンケート", value="オン")
            embed.add_field(name="アンケート時間", value=data["vote_time"])
            embed.add_field(name="アンケート・チャンネル", value="<#"+str(data["vote_id"])+">")
        else:
            embed.add_field(name="アンケート", value="オフ")
    else:
        embed.add_field(name="アンケート", value="オフ")
    if "newyear" in data and "newyear_id" in data:
        if data["newyear"]:
            embed.add_field(name="新年の挨拶", value="オン")
            embed.add_field(name="新年の挨拶・チャンネル", value="<#"+str(data["newyear_id"])+">")
        else:
            embed.add_field(name="新年の挨拶", value="オフ")
    else:
        embed.add_field(name="新年の挨拶", value="オフ")
    if "nick" in data:
        embed.add_field(name="ニックネーム", value=base.time_to_str_jp(data["nick"]))
    else:
        embed.add_field(name="ニックネーム", value="0s")
    if "forcenick" in data:
        embed.add_field(name="ニックネーム（管理者）", value=base.time_to_str_jp(data["forcenick"]))
    else:
        embed.add_field(name="ニックネーム（管理者）", value="0s")
    if "admin" in data:
        admin_str = ""
        for i in data["admin"]:
            admin_str += "<@&"+str(i)+">"
        embed.add_field(name="管理者", value=admin_str)
    else:
        embed.add_field(name="管理者", value="なし")
    if "mention" in data:
        if data["mention"]:
            embed.add_field(name="メンション制限", value="有効")
        else:
            embed.add_field(name="メンション制限", value="無効")
    else:
        embed.add_field(name="メンション制限", value="無効")
    await message.channel.send(embed=embed)

async def newyear_help(message):
    data = await base.load_conf(message)
    embed = discord.Embed(title="新年の挨拶", description="新年になった瞬間に指定したチャンネルで挨拶を送ります。\n設定方法: `."+header+" setting newyear (true/false) (チャンネル)`")
    if "newyear" in data and "newyear_id" and data:
        if data["newyear"]:
            embed.add_field(name="使用する", value="はい")
            embed.add_field(name="チャンネル", value="<#"+str(data["newyear_id"])+">")
        else:
            embed.add_field(name="使用する", value="いいえ")
    else:
        embed.add_field(name="使用する", value="いいえ")
    embed.add_field(name="(true/false)", value="使用するかどうか")
    embed.add_field(name="(チャンネル)", value="使用する場合、どこのチャンネルを使用するか")
    await message.channel.send(embed=embed)

async def newyear(message):
    cmds = message.content.split(" ")
    data = await base.load_conf(message)
    if len(cmds) <= 3:
        await newyear_help(message)
    elif len(cmds) == 4:
        if cmds[3].lower() == "true":
            await message.channel.send("エラー: 使用するチャンネルを指定してください。")
        elif cmds[3].lower() == "false":
            data["newyear"] = False
            data["newyear_id"] = 0
            embed = discord.Embed(title="設定完了", description="新年の挨拶")
            embed.add_field(name="使用する", value="いいえ")
            await message.channel.send(embed=embed)
        else:
            await newyear_help(message)
    elif len(cmds) == 5:
        if cmds[3].lower() == "true":
            if cmds[4][0:2] == "<#" and cmds[4][-1] == ">":
                data["newyear"] = True
                data["newyear_id"] = re.sub("\\D", "", cmds[4])
                embed = discord.Embed(title="設定完了", description="新年の挨拶")
                embed.add_field(name="使用する", value="はい")
                embed.add_field(name="チャンネル", value=cmds[4])
                await message.channel.send(embed=embed)
            else:
                await message.channel.send("エラー: 使用するチャンネルを指定してください。")
        elif cmds[3].lower() == "false":
            data["newyear"] = False
            data["newyear_id"] = 0
            embed = discord.Embed(title="設定完了", description="新年の挨拶")
            embed.add_field(name="使用する", value="いいえ")
            await message.channel.send(embed=embed)
        else:
            await newyear_help(message)
    else:
        await newyear_help(message)
    await base.save_conf(message, data)

async def vote_help(message):
    data = await base.load_conf(message)
    embed = discord.Embed(title="アンケート", description="アンケートを指定時間に指定したチャンネルで挨拶を送ります。\n設定方法: `."+header+" setting vote (true/false) (時間) (チャンネル)`")
    if "vote" in data and "vote_id" in data and "vote_time" in data:
        if data["vote"]:
            embed.add_field(name="使用する", value="はい")
            embed.add_field(name="時間", value=data["vote_time"])
            embed.add_field(name="チャンネル", value="<#"+str(data["vote_id"])+">")
        else:
            embed.add_field(name="使用する", value="いいえ")
    else:
        embed.add_field(name="使用する", value="いいえ")
    embed.add_field(name="(true/false)", value="使用するかどうか")
    embed.add_field(name="(時間)", value="どの時間帯に使用するか")
    embed.add_field(name="(チャンネル)", value="使用する場合、どこのチャンネルを使用するか")
    await message.channel.send(embed=embed)

async def vote(message):
    cmds = message.content.split(" ")
    data = await base.load_conf(message)
    print(cmds)
    if len(cmds) <= 3:
        print(0)
        await vote_help(message)
    elif len(cmds) == 4:
        if cmds[3].lower() == "true":
            await message.channel.send("エラー: 使用するチャンネルと時間を指定してください。")
        elif cmds[3].lower() == "false":
            data["vote"] = False
            data["vote_time"] = "00:00"
            data["vote_id"] = 0
            embed = discord.Embed(title="設定完了", description="アンケート")
            embed.add_field(name="使用する", value="いいえ")
            await message.channel.send(embed=embed)
        else:
            print(1)
            await vote_help(message)
    elif len(cmds) == 6:
        if cmds[3].lower() == "true":
            if cmds[4].find(":") != -1 and cmds[4].replace(":","").isnumeric():
                if cmds[5][0:2] == "<#" and cmds[5][-1] == ">":
                    data["vote"] = True
                    data["vote_time"] = cmds[4]
                    data["vote_id"] = re.sub("\\D", "", cmds[5])
                    embed = discord.Embed(title="設定完了", description="アンケート")
                    embed.add_field(name="使用する", value="はい")
                    embed.add_field(name="時間", value=cmds[4])
                    embed.add_field(name="チャンネル", value=cmds[5])
                    await message.channel.send(embed=embed)
                else:
                    embed.channel.send("エラー: 使用するチャンネルを指定してください。")
            else:
                await message.channel.send("エラー: 時間を指定してください。")
        elif cmds[3].lower() == "false":
            data["vote"] = False
            data["vote_time"] = "00:00"
            data["vote_id"] = 0
            embed = discord.Embed(title="設定完了", description="アンケート")
            embed.add_field(name="使用する", value="いいえ")
            await message.channel.send(embed=embed)
        else:
            print(2)
            await vote_help(message)
    else:
        print(3)
        await vote_help(message)
    await base.save_conf(message, data)

async def nick_help(message):
    data = await base.load_conf(message)
    embed = discord.Embed(title="アンケート", description="ニックネームを変更した後、次に変更できるまでの時間を設定します。\n設定方法: `."+header+" setting nick (時間)`")
    if "nick" in data:
        embed.add_field(name="時間", value=base.time_to_str(data["nick"]))
    else:
        embed.add_field(name="時間", value="0s")
    embed.add_field(name="(時間)", value="次に変更できるまでの時間 例: 1h30m")
    await message.channel.send(embed=embed)

async def nick(message):
    cmds = message.content.split(" ")
    data = await base.load_conf(message)
    print(cmds)
    if len(cmds) <= 3:
        await nick_help(message)
    elif len(cmds) > 3:
        if cmds[3] == "help":
            await nick_help(message)
        else:
            data["nick"] = base.str_to_time(cmds[3])
            embed = discord.Embed(title="設定完了", description="ニックネームを変更してから、次に変更できるまでの時間を変更しました。")
            embed.add_field(name="時間", value=base.time_to_str_jp(data["nick"]))
    else:
        await nick_help(message)
    await base.save_conf(message, data)

async def forcenick_help(message):
    data = await base.load_conf(message)
    embed = discord.Embed(title="アンケート", description="管理者が強制的にニックネームを変更した後、次にユーザーが変更できるまでの時間を設定します。\n設定方法: `."+header+" setting forcenick (時間)`")
    if "forcenick" in data:
        embed.add_field(name="時間", value=base.time_to_str(data["nick"]))
    else:
        embed.add_field(name="時間", value="0s")
    embed.add_field(name="(時間)", value="次に変更できるまでの時間 例: 1h30m")
    await message.channel.send(embed=embed)

async def forcenick(message):
    cmds = message.content.split(" ")
    data = await base.load_conf(message)
    print(cmds)
    if len(cmds) <= 3:
        print(0)
        await nick_help(message)
    elif len(cmds) > 3:
        if cmds[3] == "help":
            await forcenick_help(message)
        else:
            data["forcenick"] = base.str_to_time(cmds[3])
            embed = discord.Embed(title="設定完了", description="管理者が強制的にニックネームを変更してから、次にユーザーが変更できるまでの時間を変更しました。")
            embed.add_field(name="時間", value=base.time_to_str_jp(data["forcenick"]))
            await message.channel.send(embed=embed)
    else:
        await nick_help(message)
    await base.save_conf(message, data)

async def admin_help(message):
    data = await base.load_conf(message)
    admin_ids = []
    if "admin" in data:
        admin_id = data["admin"]
    embed = discord.Embed(title="このbotの管理者", description="このbotの設定を変更できる管理者ロールを指定します。\nこれを設定すると、このロールをもった人とサーバーのオーナーのみが設定を変更できるようになります。\n使い方: `."+header+" setting admin (ロール)`")
    embed.add_field(name="ロール", value="設定したいロール。(複数選択可)")
    await message.channel.send(embed=embed)

async def admin(message):
    data = await base.load_conf(message)
    cmds = message.content.split(" ")
    if len(cmds) == 2:
        await admin_help(message)
    else:
        admins, check = [], True
        print(cmds)
        for i in range(len(cmds) - 3):
            if cmds[i+3][0:3] == "<@&" and cmds[i+3][-1] == ">":
                admins.append(int(re.sub("\\D", "", cmds[i+3])))
            else:
                if cmds[i+2] != "":
                    check = False
                    break
        if check:
            data["admin"] = admins
            admin_str = ""
            for i in admins:
                admin_str += "<@&" + str(i) + ">"
            embed = discord.Embed(title="設定完了", description="管理者ロールの設定が完了しました。\n設定されたのは以下の通りです。")
            embed.add_field(name="管理者", value=admin_str)
            await message.channel.send(embed=embed)
        else:
            await message.channel.send("エラー: 関係のない文字が入っているようです。ロールのみを指定してください。")
    await base.save_conf(message, data)

async def mention_help(message):
    embed = discord.Embed(title="メンション制限", description="内容なしでメンションが行われた場合、メッセージを削除するかどうかを選べます。\n使い方: `."+header+" setting mention (true/false)`")
    embed.add_field(name="(true/false)", value="trueかfalseを入力してください。")
    await message.channel.send(embed=embed)

async def mention(message):
    cmds = message.content.split(" ")
    data = await base.load_conf(message)
    if len(cmds) <= 3:
        await mention_help(message)
    else:
        if cmds[3] == "help":
            await mention_help(message)
        elif cmds[3].lower() == "true" or cmds[3].lower() == "false":
            data["mention"] = cmds[3].lower() == "true"
            embed = discord.Embed(title="設定完了", description="内容なしでメンションが行われた場合、メッセージを削除するかどうかを設定しました。")
            if data["mention"]:
                embed.add_field(name="削除する", value="はい")
            else:
                embed.add_field(name="削除する", value="いいえ")
            await message.channel.send(embed=embed)
        else:
            await message.channel.send(message.author.mention+"trueかfalseを入力してください。")
    await base.save_conf(message, data)
