import os
import asyncio
import discord
from dotenv import load_dotenv

# Cargar variables de entorno desde la raiz del proyecto
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

TOKEN = os.getenv('TOKEN')
GUILD_ID = os.getenv('GUILD_ID')
CHANNEL_ID = os.getenv('CHANNEL_ID')

if not TOKEN:
    raise ValueError("TOKEN no encontrado en .env")
if not GUILD_ID:
    raise ValueError("GUILD_ID no encontrado en .env")
if not CHANNEL_ID:
    raise ValueError("CHANNEL_ID no encontrado en .env")

try:
    GUILD_ID_INT = int(GUILD_ID)
    CHANNEL_ID_INT = int(CHANNEL_ID)
except ValueError:
    raise ValueError("GUILD_ID y CHANNEL_ID deben ser numeros")

client = discord.Client()
reconnecting = False
current_channel_id = CHANNEL_ID_INT  # Se actualiza cuando el bot es movido
pending_disconnect = False           # True cuando hay una desconexion pendiente de confirmar

@client.event
async def on_ready():
    print(f'Conectado como {client.user}')
    print(f'Guild ID: {GUILD_ID_INT}')
    print(f'Channel ID: {CHANNEL_ID_INT}')

    client.loop.create_task(keep_alive())
    await join_voice_channel(CHANNEL_ID_INT)

async def join_voice_channel(channel_id):
    global reconnecting

    if reconnecting:
        return
    reconnecting = True

    try:
        guild = client.get_guild(GUILD_ID_INT)
        if not guild:
            print(f'No se encontro el guild {GUILD_ID_INT}')
            return

        channel = guild.get_channel(channel_id)
        if not channel:
            print(f'No se encontro el canal de voz {channel_id}')
            return

        # Desconectar voice client existente del guild si hay uno
        if guild.voice_client:
            try:
                await guild.voice_client.disconnect(force=True)
            except Exception:
                pass
            await asyncio.sleep(1)

        voice = await channel.connect(
            self_mute=True,
            self_deaf=True,
            timeout=30,
            reconnect=True
        )
        print(f'Conectado al canal de voz: {channel.name}')
    except Exception as e:
        print(f'Error al conectar al canal de voz: {e}')
        await asyncio.sleep(5)
        reconnecting = False
        await join_voice_channel(channel_id)
    finally:
        reconnecting = False

@client.event
async def on_voice_state_update(member, before, after):
    global current_channel_id, pending_disconnect
    if member.id != client.user.id:
        return

    if before.channel == after.channel:
        return

    if after.channel is None:
        # Posible desconexion — esperar un momento por si es un movimiento de canal
        pending_disconnect = True
        await asyncio.sleep(1)
        if not pending_disconnect:
            # Fue un movimiento, ya se manejo en el otro evento
            return
        pending_disconnect = False
        # Desconexion real -> reconectar al canal actual
        print(f'Desconectado de {before.channel}. Reconectando a {current_channel_id}...')
        await asyncio.sleep(2)
        await join_voice_channel(current_channel_id)
    else:
        # Movido a otro canal -> cancelar cualquier reconexion pendiente y actualizar canal
        pending_disconnect = False
        current_channel_id = after.channel.id
        print(f'Movido a {after.channel.name} (ID: {current_channel_id}). Canal permanente actualizado.')

async def keep_alive():
    await client.wait_until_ready()
    while not client.is_closed():
        guild = client.get_guild(GUILD_ID_INT)
        if guild and guild.voice_client and guild.voice_client.is_connected():
            print(f'Conexion de voz activa en: {guild.voice_client.channel.name}')
        await asyncio.sleep(60)

if __name__ == '__main__':
    try:
        client.run(TOKEN)
    except KeyboardInterrupt:
        print("Bot detenido por el usuario")
    except Exception as e:
        print(f'Error al iniciar el bot: {e}')
