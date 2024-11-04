from disbot import base
import re
import json

header = base.header

async def help(message):
    embed = discord.Embed(title="アイテム購入", description="貯めたポイントを使ってアイテムを購入して、ゲームを有利に進めよう！\n使い方`."+header+" shop {コマンド}`\n\nコマンド一覧")
    embed.add_field(name="list", value="取り扱っているアイテムのリストを表示します。\n`list ページ数`で指定したページを表示します。")
    embed.add_field(name="buy", value="アイテムを購入します。\n使い方: `buy {ID}`")
    embed.add_field(name="help", value="このヘルプを表示します。")
    message.channel.send(embed=embed)

async def shop(message):
    cmds = message.content.split(" ")
    if cmds[2] == "list":
        await list_items(message)
    elif cmds[2] == "buy":
        await buy_item(message)
    else:
        await help(message)

async def list_items(message):

async def buy_item(message):
