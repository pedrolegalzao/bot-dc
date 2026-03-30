import discord
from discord.ext import commands
import os
from datetime import timedelta

# ============================================================
# CONFIGURAÇÕES
# ============================================================

CANAL_ENTRADA = "join"
CANAL_SAIDA = "exit"
PREFIXO = "!"
CARGO_MODERACAO = "kami"

# Entrada
TITULO_ENTRADA = "Bem-vindo(a)!"
MENSAGEM_ENTRADA = "{membro} Bem vindo a {servidor}!"
COR_ENTRADA = discord.Color.green()
IMAGEM_ENTRADA = "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExN2xka2tva2gwNTVydDZkMWNzaHpnNWVyM2pwazduOHpkZjY3bTk3bCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/DeBBINXN86r8Q/giphy.gif"

# Saída
TITULO_SAIDA = "Tchau!"
MENSAGEM_SAIDA = "{nome} foi pra puta q pariu"
COR_SAIDA = discord.Color.red()
IMAGEM_SAIDA = "https://media.tenor.com/f4xSIqFf3gwAAAAi/konakonagifs-touhou.gif"

# ============================================================
# BOT
# ============================================================

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIXO, intents=intents)


def tem_cargo_mod():
    async def predicate(ctx):
        cargo = discord.utils.get(ctx.author.roles, name=CARGO_MODERACAO)
        if cargo is None:
            await ctx.send(f"❌ Você precisa ter o cargo **{CARGO_MODERACAO}** para usar este comando.")
            return False
        return True
    return commands.check(predicate)


def get_canal(guild, nome_canal):
    canal = discord.utils.get(guild.text_channels, name=nome_canal)
    if canal is None:
        return guild.system_channel
    return canal


@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")


# 🔥 ENTRADA (COM CARGO AUTOMÁTICO)
@bot.event
async def on_member_join(member):
    guild = member.guild

    # Cargo automático
    cargo = discord.utils.get(guild.roles, name="kami")

    if cargo:
        await member.add_roles(cargo)
        print(f"Cargo '{cargo.name}' adicionado a {member.name}")
    else:
        print("Cargo 'kami' não encontrado")

    # Mensagem
    channel = get_canal(guild, CANAL_ENTRADA)

    if channel:
        embed = discord.Embed(
            title=TITULO_ENTRADA,
            description=MENSAGEM_ENTRADA.format(
                membro=member.mention,
                servidor=guild.name
            ),
            color=COR_ENTRADA
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_image(url=IMAGEM_ENTRADA)

        await channel.send(embed=embed)


# 🔻 SAÍDA
@bot.event
async def on_member_remove(member):
    guild = member.guild
    channel = get_canal(guild, CANAL_SAIDA)

    if channel:
        embed = discord.Embed(
            title=TITULO_SAIDA,
            description=MENSAGEM_SAIDA.format(nome=member.name),
            color=COR_SAIDA
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_image(url=IMAGEM_SAIDA)

        await channel.send(embed=embed)


# ── COMANDOS ─────────────────────────────────

@bot.command()
@tem_cargo_mod()
async def ping(ctx):
    await ctx.send("Pong! 🏓")


@bot.command()
@tem_cargo_mod()
async def ajuda(ctx):
    embed = discord.Embed(title="Comandos", color=discord.Color.blue())
    embed.add_field(name="Gerais", value="!ping\n!ajuda", inline=False)
    embed.add_field(name="Moderação", value="!ban\n!unban\n!mute\n!unmute\n!kick", inline=False)
    await ctx.send(embed=embed)


@bot.command()
@tem_cargo_mod()
@commands.has_permissions(ban_members=True)
async def ban(ctx, membro: discord.Member, *, motivo="Sem motivo"):
    await membro.ban(reason=motivo)
    await ctx.send(f"{membro} foi banido. Motivo: {motivo}")


@bot.command()
@tem_cargo_mod()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, nome_usuario):
    bans = [entry async for entry in ctx.guild.bans()]
    for ban_entry in bans:
        if str(ban_entry.user) == nome_usuario:
            await ctx.guild.unban(ban_entry.user)
            await ctx.send(f"{ban_entry.user} foi desbanido.")
            return


@bot.command()
@tem_cargo_mod()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, membro: discord.Member, minutos: int = 10):
    await membro.timeout(timedelta(minutes=minutos))
    await ctx.send(f"{membro} silenciado por {minutos} minutos")


@bot.command()
@tem_cargo_mod()
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, membro: discord.Member):
    await membro.timeout(None)
    await ctx.send(f"{membro} pode falar novamente")


@bot.command()
@tem_cargo_mod()
@commands.has_permissions(kick_members=True)
async def kick(ctx, membro: discord.Member):
    await membro.kick()
    await ctx.send(f"{membro} foi expulso")


# ── ERROS ─────────────────────────────────

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Sem permissão")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Membro não encontrado")
    else:
        print(error)


# TOKEN
TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

if not TOKEN:
    raise ValueError("Token não encontrado")

bot.run(TOKEN)
