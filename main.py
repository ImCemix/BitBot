import discord
import aiofiles
from discord.ext import commands
import os


intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix="#", intents=intents)
client.remove_command("help")

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="#help"))
    print("Online. . .")
    client.reaction_roles = []

    for file in ["reaction_roles.txt"]:
        async with aiofiles.open(file, mode="a") as temp:
            pass

    async with aiofiles.open("reaction_roles.txt", mode="r") as file:
        lines = await file.readlines()
        for line in lines:
            data = line.split(" ")
            client.reaction_roles.append((int(data[0]), int(data[1]), data[2].strip("\n")))

@client.event
async def on_raw_reaction_add(payload):
    for role_id, msg_id, emoji in client.reaction_roles:
        if msg_id == payload.message_id and emoji == str(payload.emoji.name.encode("utf-8")):
            await payload.member.add_roles(client.get_guild(payload.guild_id).get_role(role_id))

@client.event
async def on_raw_reaction_remove(payload):
    for role_id, msg_id, emoji in client.reaction_roles:
        if msg_id == payload.message_id and emoji == str(payload.emoji.name.encode("utf-8")):
            guild = client.get_guild(payload.guild_id)
            await guild.get_member(payload.user_id).remove_roles(guild.get_role(role_id))

@client.command()
@commands.has_permissions(administrator=True)
async def set_reaction(ctx, role: discord.Role = None, msg: discord.Message = None, emoji=None):
    if role != None and msg != None and emoji != None:
        await msg.add_reaction(emoji)
        client.reaction_roles.append((role.id, msg.id, str(emoji.encode("utf-8"))))

        async with aiofiles.open("reaction_roles.txt", mode="a") as file:
            emoji_utf = emoji.encode("utf-8")
            await file.write(f"{role.id} {msg.id} {emoji_utf}\n")

        await ctx.channel.send("**Erfolgreich geladen.**")

@client.command()
async def adminhelp(ctx):
    embed = discord.Embed(title="Admin Befehle", color=discord.Colour.green())
    embed.add_field(name="#clear", value="Mit #clear (0-1000) kannst du Nachrichten löschen.", inline=False)
    embed.add_field(name="#kick", value="Mit #kick @User (Grund) kannst du Spieler kicken.", inline=False)
    embed.add_field(name="#ban", value="Mit #ban @User (Grund) kannst du Spieler bannen.", inline=False)
    embed.add_field(name="#unban", value="Mit #unban @User kannst du Spieler unbannen.", inline=False)
    embed.add_field(name="#set_reaction", value="Mit #set_reaction (@Role) (Message_ID) (Emoji) kannst du Rollen mit reactionen bestimmen.", inline=False)
    await ctx.send(embed=embed)

@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)

@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member : discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"{member.mention} wurde gekickt")

@client.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member : discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"{member.mention} wurde gebannt")

client.run(os.environ["TOKEN"])