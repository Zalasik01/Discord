import discord
import logging
from discord.ext import commands
import os

# Configuração do logging
logging.basicConfig(
    filename='bot.log',  # Nome do arquivo de log
    level=logging.INFO,   # Nível de log (INFO registra todas as mensagens de log)
    format='%(asctime)s [%(levelname)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Criar um handler para o arquivo de log do Discord
discord_log_handler = logging.FileHandler('bot.log')
discord_log_handler.setLevel(logging.INFO)
discord_log_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] [Discord]: %(message)s'))

# Adicionar o handler do arquivo de log do Discord ao logger do Discord
discord_logger = logging.getLogger('discord')
discord_logger.addHandler(discord_log_handler)

intents = discord.Intents.default()
intents.message_content = True
intents.guild_messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Dicionário para mapear canais temporários
temp_chat_channels = {}

# Variável para armazenar a mensagem de boas-vindas
mensagem_boas_vindas = None

@bot.event
async def on_ready():
    global mensagem_boas_vindas
    print(f'Bot conectado como {bot.user}')
    # ID do canal onde o bot enviará a mensagem com a reação
    channel_id = 1134544000204951672
    channel = bot.get_channel(channel_id)
    if channel:
        mensagem_boas_vindas = await channel.send("Olá! Para abertura de chamado clique na reação ✅.")
        await mensagem_boas_vindas.add_reaction("✅")
        print(f"Mensagem de boas-vindas enviada no canal {channel_id}.")
    else:
        print(f"Não foi possível encontrar o canal com ID {channel_id}")

# Função para enviar a mensagem de boas-vindas no chat temporário
async def send_welcome_message(channel):
    message = await channel.send("Bem vindo ao chat temporário.")
    logging.info(f"Enviada mensagem de boas-vindas para o canal {channel.name} (ID: {channel.id}).")

# Função para excluir o canal temporário pelo seu ID
async def delete_temp_chat(channel_id):
    channel = bot.get_channel(channel_id)
    if channel:
        await channel.delete()
        del temp_chat_channels[channel.id]
        logging.info(f"Canal {channel.name} (ID: {channel.id}) excluído.")

@bot.event
async def on_reaction_add(reaction, user):
    global mensagem_boas_vindas
    if reaction.emoji == "✅" and not user.bot:
        channel = reaction.message.channel
        category = channel.category
        overwrites = {
            channel.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True),
        }
        temp_chat_channel = await category.create_text_channel(name=f'Atendimento-{user.name}', overwrites=overwrites, topic=f"ID do usuário: {user.id}")
        await send_welcome_message(temp_chat_channel)

        # Adicionar o canal temporário ao dicionário
        temp_chat_channels[temp_chat_channel.id] = 0

        logging.info(f"Usuário {user.name} (ID: {user.id}) abriu o chat temporário {temp_chat_channel.name} (ID: {temp_chat_channel.id}).")

@bot.command()
@commands.has_role(1134460000270565398)  # Verifica se o usuário tem o cargo com ID 1134460000270565398
async def logs(ctx):
    with open('bot.log', 'w') as file:
        file.write("")  # Limpa o conteúdo do arquivo bot.log
    if os.stat("bot.log").st_size == 0:
        await ctx.send("O arquivo de logs já está vazio.")
    else:
        await ctx.send("Arquivo de logs limpo com sucesso!")
        logging.info(f"Arquivo de logs limpo por {ctx.author.name} (ID: {ctx.author.id}).")

@bot.command()
async def resolver(ctx):
    await ctx.send("Finalizando e excluindo o chat temporário.")
    await delete_temp_chat(ctx.channel.id)

# Função assíncrona para rodar o bot usando asyncio.run()
async def run_bot():
    logging.info("Bot iniciado.")
    try:
        await bot.start('SEU_TOKEN_AQUI')  # Substitua "SEU_TOKEN_AQUI" pelo token real do seu bot
    except KeyboardInterrupt:
        logging.info("Bot encerrado por um sinal de teclado (KeyboardInterrupt).")
    finally:
        await bot.close()  # Finalizar o bot de forma limpa
        logging.info("Bot encerrado de forma limpa.")

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        pass
