import discord
from disbot import base, check, custom, game, config, nick, lockdown

async def show_help(message):
    embed = discord.Embed(title="Among US 自動ポイント計算 v.1.7.3", description="Made by takpika\nUpdate: 2021/3/13\nAutoMuteUs botが出力した結果を元にポイントを自動計算します。\n※動作検証が十分にできないため、うまく動作しない可能性があります。")
    embed.add_field(name="check", value="現在のレート状況を確認します。")
    embed.add_field(name="add", value="新しいゲームを手動追加します。")
    embed.add_field(name="help", value="このヘルプを表示します。")
    embed.add_field(name="game", value="ゲーム関連のデータを表示・削除できます。")
    embed.add_field(name="setting", value="このbotの設定ができます。")
    embed.add_field(name="nick", value="ニックネームの変更ができます。")
    await message.channel.send(embed=embed)

async def command(message):
    await message.delete()
    data = await base.load_conf(message)
    print(message.guild.members)
    cmds = message.content.split(" ")
    if len(cmds) > 1:
        if cmds[1] == "check":
            await check.show_check(message)
        elif cmds[1] == "help":
            await show_help(message)
        elif cmds[1] == "add":
            await custom.add_custom(message)
        elif cmds[1] == "game":
            await game.show_games(message)
        elif cmds[1] == "setting":
            await config.show_conf(message)
        elif cmds[1] == "nick":
            if "nick" in data:
                if data["nick"] > 0:
                        await nick.show_nick(message)
                else:
                    await message.channel.send(message.author.mention+"現在ニックネーム機能は無効化されています。通常のニックネーム変更機能を使用してください。")
            else:
                await message.channel.send(message.author.mention+"現在ニックネーム機能は無効化されています。通常のニックネーム変更機能を使用してください。")
        elif cmds[1] == "lockdown":
            await lockdown.lockdown(message)
        elif "働け" in cmds[1] or "はたらけ" in cmds[1] or "hatarake" in cmds[1].lower():
            await message.channel.send("¯\_(ツ)_/¯")
        else:
            await message.channel.send(message.author.mention+" `"+cmds[1]+"` 未知のコマンドです。")
    else:
        await show_help(message)
    base.backup_all_data()
