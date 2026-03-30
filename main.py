import discord
from discord.ext import commands
import os
from datetime import timedelta

# ============================================================
# CONFIGURAÇÕES — edite aqui para personalizar o bot
# ============================================================

# Canal onde a mensagem de ENTRADA será enviada
CANAL_ENTRADA = "join"

# Canal onde a mensagem de SAÍDA será enviada
CANAL_SAIDA = "exit"

# Prefixo dos comandos de moderação
PREFIXO = "!"

# Cargo com permissão para usar os comandos do bot
CARGO_MODERACAO = "Administrador"

# Mensagem de ENTRADA
TITULO_ENTRADA = "Bem-vindo(a)!"
MENSAGEM_ENTRADA = "{membro} Bem vindo a {servidor}!"
COR_ENTRADA = discord.Color.green()
IMAGEM_ENTRADA = "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExN2xka2tva2gwNTVydDZkMWNzaHpnNWVyM2pwazduOHpkZjY3bTk3bCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/DeBBINXN86r8Q/giphy.gif"

# Mensagem de SAÍDA
TITULO_SAIDA = "Tchau!"
MENSAGEM_SAIDA = "{nome} foi pra puta q pariu"
COR_SAIDA = discord.Color.red()
IMAGEM_SAIDA = "https://media.tenor.com/f4xSIqFf3gwAAAAi/konakonagifs-touhou.gif"

# ============================================================
# CÓDIGO DO BOT — não precisa editar abaixo
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
    if nome_canal is None:
        return guild.system_channel
    canal = discord.utils.get(guild.text_channels, name=nome_canal)
    if canal is None:
        print(f"[AVISO] Canal '#{nome_canal}' não encontrado. Usando canal padrão.")
        return guild.system_channel
    return canal


@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")
    print(f"Canal de entrada:  #{CANAL_ENTRADA}")
    print(f"Canal de saída:    #{CANAL_SAIDA}")


@bot.event
async def on_member_join(member):
    guild = member.guild
    channel = get_canal(guild, CANAL_ENTRADA)

    if channel is not None:
        embed = discord.Embed(
            title=TITULO_ENTRADA.format(servidor=guild.name),
            description=MENSAGEM_ENTRADA.format(
                membro=member.mention,
                servidor=guild.name,
                contagem=guild.member_count
            ),
            color=COR_ENTRADA
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_image(url=IMAGEM_ENTRADA)
        await channel.send(embed=embed)
        print(f"Boas-vindas enviadas para {member.name} em #{channel.name}")


@bot.event
async def on_member_remove(member):
    guild = member.guild
    channel = get_canal(guild, CANAL_SAIDA)

    if channel is not None:
        embed = discord.Embed(
            title=TITULO_SAIDA,
            description=MENSAGEM_SAIDA.format(
                nome=member.name,
                servidor=guild.name
            ),
            color=COR_SAIDA
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_image(url=IMAGEM_SAIDA)
        await channel.send(embed=embed)
        print(f"Mensagem de saída enviada para {member.name} em #{channel.name}")


# ── Comandos gerais ──────────────────────────────────────────

@bot.command()
@tem_cargo_mod()
async def ping(ctx):
    await ctx.send("Pong! 🏓")


@bot.command()
@tem_cargo_mod()
async def ajuda(ctx):
    embed = discord.Embed(title="Comandos disponíveis", color=discord.Color.blue())
    embed.add_field(name="Gerais", value=(
        "`!ping` — Verifica se o bot está online\n"
        "`!ajuda` — Mostra esta mensagem\n"
    ), inline=False)
    embed.add_field(name="Moderação (só admins)", value=(
        "`!ban @usuário [motivo]` — Bane um membro\n"
        "`!unban usuário#tag` — Remove ban de um membro\n"
        "`!mute @usuário [minutos] [motivo]` — Silencia por X minutos (padrão: 10)\n"
        "`!unmute @usuário` — Remove o silêncio\n"
        "`!kick @usuário [motivo]` — Expulsa um membro\n"
    ), inline=False)
    await ctx.send(embed=embed)


# ── Comandos de moderação ────────────────────────────────────

@bot.command()
@tem_cargo_mod()
@commands.has_permissions(ban_members=True)
async def ban(ctx, membro: discord.Member, *, motivo="Sem motivo informado"):
    await membro.ban(reason=motivo)
    embed = discord.Embed(
        title="🔨 Membro banido",
        description=f"**{membro}** foi colocado em seu devido lugar... (inferno)\nMotivo: {motivo}",
        color=discord.Color.dark_red()
    )
    embed.set_image(url="https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHNua3JlaWNrN3RxZWo4NXp3a281MnludWNjdHJzcHdnODJ3NG9hZyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/xUO4t2gkWBxDi/giphy.gif")
    await ctx.send(embed=embed)


@bot.command()
@tem_cargo_mod()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, nome_usuario):
    bans = [entry async for entry in ctx.guild.bans()]
    for ban_entry in bans:
        user = ban_entry.user
        if str(user) == nome_usuario:
            await ctx.guild.unban(user)
            embed = discord.Embed(
                title="✅ Ban removido",
                description=f"**{user}** foi desbanido.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            return
    await ctx.send(f"Usuário `{nome_usuario}` não encontrado na lista de banidos.")


@bot.command()
@tem_cargo_mod()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, membro: discord.Member, minutos: int = 10, *, motivo="Sem motivo informado"):
    duracao = timedelta(minutes=minutos)
    await membro.timeout(duracao, reason=motivo)
    embed = discord.Embed(
        title="🔇 Membro silenciado",
        description=f"**{membro.mention}** foi silenciado por **{minutos} minuto(s)**.\nMotivo: {motivo}",
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed)


@bot.command()
@tem_cargo_mod()
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, membro: discord.Member):
    await membro.timeout(None)
    embed = discord.Embed(
        title="🔊 Silêncio removido",
        description=f"**{membro.mention}** pode falar novamente.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)


@bot.command()
@tem_cargo_mod()
@commands.has_permissions(kick_members=True)
async def kick(ctx, membro: discord.Member, *, motivo="Sem motivo informado"):
    await membro.kick(reason=motivo)
    embed = discord.Embed(
        title="👢 Membro expulso",
        description=f"**{membro}** foi expulso.\nMotivo: {motivo}",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)


# ── Erros de permissão ───────────────────────────────────────

@ban.error
@unban.error
@mute.error
@unmute.error
@kick.error
async def erro_permissao(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Você não tem permissão para usar este comando.")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Membro não encontrado. Mencione o usuário com @.")
    else:
        await ctx.send(f"❌ Erro: {error}")


TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

if not TOKEN:
    raise ValueError("Variável de ambiente DISCORD_BOT_TOKEN não encontrada.")

bot.run(TOKEN)
