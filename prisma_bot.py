import discord  
from discord.ext import commands

import sqlite3
from config import settings

intents = discord.Intents.all()
intents.message_content = True

client = commands.Bot(command_prefix = settings['PREFIX'], intents=intents) #test_guilds=[937586330676895804])
client.remove_command('help')

connection = sqlite3.connect('server.db')
cursor = connection.cursor()

@client.event
async def on_ready():
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        name TEXT,
        id INT,
        cash BIGINT,
        rep INT,
        lvl INT
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS shop (
        role_id INT,
        id INT,
        cost BIGINT
    )""")
    connection.commit()

    for guild in client.guilds:
        for member in guild.members:
            if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
                cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0, 1)")
            else:
                pass
    connection.commit()

@client.event
async def on_member_oin(member):
            if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
                cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0, 1)")
                connection.commit()
            else:
                pass

@client.command(aliases = ['balance', 'cash'])
async def __balance(ctx, member: discord.Member = None):
    await ctx.channel.purge(limit =1)

    if member is None:
        await ctx.send(embed = discord.Embed(
            description=f"""Balance of user **{ctx.author}** is **{cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]} :moneybag:**"""
        ))
    else:
        await ctx.send(embed = discord.Embed(
            description=f"""Balance of user **{member}** is **{cursor.execute("SELECT cash FROM users WHERE id = {}".format(member.id)).fetchone()[0]} :moneybag:**"""
        ))
        
@client.command(aliases = ['award'])
@commands.has_permissions(administrator = True)
async def __award(ctx, member: discord.Member = None, amount: int = None):
    await ctx.channel.purge(limit = 1)

    if member is None:
        await ctx.send(f"**{ctx.author}**, specify member")
    else:
        if amount is None:
            await ctx.send(f"**{ctx.author}**, specify amount of money")
        elif amount < 1: 
            await ctx.send(f"**{ctx.author}**, specify amount of money more then 1")
        else: 
            cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(amount, member.id))
            connection.commit()

            text = await ctx.send(f'Success! {ctx.author}')
            await text.add_reaction('✅')

@client.command(aliases = ['comission'])
#@commands.has_permissions(administrator = True)
async def __comis(ctx, member: discord.Member = None, amount: int = None):
    await ctx.channel.purge(limit = 1)

    if member is None:
        await ctx.send(f"**{ctx.author}**, specify member")
    else:
        if amount is None:
            await ctx.send(f"**{ctx.author}**, specify amount of money")
        elif amount < 1: 
            await ctx.send(f"**{ctx.author}**, specify amount of money more then 1")
        else: 
            if cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0] > amount:
                cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(amount, member.id))
                connection.commit()

                text = await ctx.send(f'Success! {ctx.author}')
                await text.add_reaction('✅')
            else: 
                await ctx.send(f'awdaw')

@client.command(aliases = ['add-shop'])
async def __add_shop(ctx, role: discord.Role = None, cost: int = None):
    await ctx.channel.purge(limit = 1)

    if role is None:
        await ctx.send(f'**{ctx.author}**, enter role, witch you shuod add at shop.')
    else: 
        if cost is None:
            await ctx.send(f'**{ctx.author}**, enter sell of this role.')
        elif cost < 0:
            await ctx.send(f'**{ctx.author}**, so low sell of this role.')
        else: 
            cursor.execute("INSERT INTO shop VALUES ({}, {}, {})".format(role.id, ctx.guild.id, cost))
            connection.commit()

            text = await ctx.send(f'Success!')
            await text.add_reaction('✅')

@client.command(aliases = ['remove-shop'])
async def __remove_shop(ctx, role: discord.Role = None):
    await ctx.channel.purge(limit = 1)

    if role is None:
        await ctx.send(f'**{ctx.author}**, enter role, witch you shuod remove at shop.')
    else:
        cursor.execute("DELETE FROM shop WHERE role_id = {}".format(role.id))

        text = await ctx.send(f'Succcess!')
        await text.add_reaction('✅')

@client.command(aliases = ['shop'])
async def __shop(ctx):
    await ctx.channel.purge(limit = 1)

    embed = discord.Embed(title='Roles shop')

    for row in cursor.execute("SELECT role_id, cost FROM shop WHERE id = {}".format(ctx.guild.id)):
        if ctx.guild.get_role(row[0]) != None:
            embed.add_field(
                name = f"Sell {row[1]}",
                value= f"You can buy: {ctx.guild.get_role(row[0]).mention}",
                inline = False 
            )
        else:
            pass

    await ctx.send(embed = embed)

@client.command(aliases = ['buy', 'buy-role'])
async def __buy(ctx, role: discord.Role = None):

    if role is None:
        await ctx.send(f'**{ctx.author}**, enter role, witch you shuod buy.') 
    else: 
        if role in ctx.author.roles:
            await ctx.send(f'**{ctx.author}**, you can`t buy, what you have') 
        elif cursor.execute("SELECT cost FROM shop WHERE role_id = {}".format(role.id)).fetchone()[0] > cursor.execute('SELECT cash FROM users WHERE id = {}'.format(ctx.author.id)).fetchone()[0]:
            await ctx.send(f'You did`n have money for it.')
        else:
            await ctx.author.add_roles(role)
            cursor.execute("UPDATE users SET cash = cash - {0} WHERE id = {1}".format(cursor.execute("SELECT cost FROM shop WHERE role_id = {}".format(role.id)).fetchone()[0], ctx.author.id))
            connection.commit()

            text = await ctx.send(f'Success buying!')
            await text.add_reaction('✅')


client.run("MTA2ODg5NjExNzg2Mjk2MTIzMg.GdDhHy.khzfuQuuYQZX15dcu7XCNBe0QcPf_xS_jS9rHo")