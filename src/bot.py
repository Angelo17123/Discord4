import os
import sys
import asyncio
import random
import time
import discord
from discord.voice_state import VoiceConnectionState
from dotenv import load_dotenv
from webserver import keep_alive as start_webserver

# Forzar SelectorEventLoop en Windows para evitar WinError 10038 con asyncio ProactorEventLoop
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

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

# ID del servidor especial donde el bot debe mantenerse a toda costa
SPECIAL_GUILD_ID = 1374566026003611718
IS_SPECIAL_GUILD = (GUILD_ID_INT == SPECIAL_GUILD_ID)

# Configuracion de backoff (mas agresivo para servidor especial)
MAX_RETRIES = 5 if not IS_SPECIAL_GUILD else 10
BASE_DELAY = 2 if not IS_SPECIAL_GUILD else 1
MAX_DELAY = 60 if not IS_SPECIAL_GUILD else 30

# Configuracion de logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Canal objetivo - se actualiza cuando el bot es movido
TARGET_CHANNEL_ID = CHANNEL_ID_INT

# Monkey-patch de voice_state_update para interceptar movimientos ANTES que discord.py-self
_original_vs_update = VoiceConnectionState.voice_state_update

async def _patched_voice_state_update(self, data):
    """Interceptar voice state update para prevenir reconexion al mover de canal"""
    channel_id = data.get('channel_id')
    if channel_id is not None:
        new_channel_id = int(channel_id)
        if self.voice_client and self.voice_client.channel:
            current_channel_id = self.voice_client.channel.id
            if new_channel_id != current_channel_id:
                # Bot fue movido a otro canal - prevenir reconexion interna
                global TARGET_CHANNEL_ID
                TARGET_CHANNEL_ID = new_channel_id
                self._disconnected.set()
                self._expecting_disconnect = True
                if self._runner:
                    self._runner.cancel()
                    self._runner = None
                if self._connector:
                    self._connector.cancel()
                    self._connector = None
                self._update_voice_channel(new_channel_id)
                return
    await _original_vs_update(self, data)

VoiceConnectionState.voice_state_update = _patched_voice_state_update

def log(level, message):
    """Log con timestamp, nivel y canal de voz actual"""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    try:
        voice_info = get_current_voice_info()
    except Exception:
        voice_info = "desconocido"
    print(f'[{timestamp}] [{level:8}] [Voz: {voice_info}] {message}')

def get_current_voice_info():
    """Obtener informacion del canal de voz actual si esta conectado"""
    guild = client.get_guild(GUILD_ID_INT)
    if guild and guild.voice_client and guild.voice_client.is_connected():
        channel = guild.voice_client.channel
        return f"en canal #{channel.name} (ID: {channel.id})"
    return "desconectado"

def get_backoff_delay(attempt, is_special=False):
    """Backoff exponencial con jitter"""
    delay = min(BASE_DELAY * (2 ** attempt), MAX_DELAY)
    jitter = random.uniform(0, 1)
    final_delay = delay + jitter
    
    if is_special and attempt < 3:
        final_delay = min(final_delay, 3)
    
    return final_delay

# Cliente Discord
client = discord.Client()

# Lock para sincronizacion de reconexiones - EVITA RACE CONDITIONS
voice_lock = asyncio.Lock()

# Estado de conexion
TARGET_CHANNEL_ID = CHANNEL_ID_INT
pending_disconnect = False
voice_retry_count = 0
last_connected_channel_id = None

# Circuit breaker
CIRCUIT_BREAKER_THRESHOLD = 10
CIRCUIT_BREAKER_TIMEOUT = 300
circuit_breaker_failures = 0
circuit_breaker_last_failure = 0

def reset_retry_count():
    """Resetear contador de reintentos y circuit breaker"""
    global voice_retry_count, circuit_breaker_failures
    voice_retry_count = 0
    circuit_breaker_failures = 0
    log('INFO', 'Contadores reseteados')

def check_circuit_breaker():
    """Verificar si el circuit breaker esta abierto"""
    global circuit_breaker_failures, circuit_breaker_last_failure
    
    if circuit_breaker_failures >= CIRCUIT_BREAKER_THRESHOLD:
        time_since_last = time.time() - circuit_breaker_last_failure
        if time_since_last < CIRCUIT_BREAKER_TIMEOUT:
            log('WARNING', f'Circuit breaker ABIERTO ({circuit_breaker_failures} fallos). Esperando {int(CIRCUIT_BREAKER_TIMEOUT - time_since_last)}s')
            return False
        else:
            log('INFO', 'Circuit breaker reseteado por timeout')
            circuit_breaker_failures = 0
    return True

def record_failure():
    """Registrar un fallo para el circuit breaker"""
    global circuit_breaker_failures, circuit_breaker_last_failure
    circuit_breaker_failures += 1
    circuit_breaker_last_failure = time.time()
    log('WARNING', f'Fallo registrado ({circuit_breaker_failures}/{CIRCUIT_BREAKER_THRESHOLD})')

async def handle_connection_failure(channel_id):
    """Manejar fallo de conexion con backoff"""
    global voice_retry_count
    
    record_failure()
    voice_retry_count += 1
    
    if voice_retry_count > MAX_RETRIES:
        wait_seconds = 60 if not IS_SPECIAL_GUILD else 30
        log('ERROR', f'Maximo reintentos ({MAX_RETRIES}). Esperando {wait_seconds}s...')
        await asyncio.sleep(wait_seconds)
        voice_retry_count = 0
    else:
        delay = get_backoff_delay(voice_retry_count, IS_SPECIAL_GUILD)
        log('INFO', f'Esperando {delay:.1f}s antes de reintentar ({voice_retry_count}/{MAX_RETRIES})...')
        await asyncio.sleep(delay)
    
    await join_voice_channel(channel_id, reason=f"reintento_{voice_retry_count}")

async def join_voice_channel(channel_id, reason="inicial"):
    """Conectar al canal de voz con manejo robusto de errores"""
    global voice_retry_count, pending_disconnect, last_connected_channel_id
    
    if not check_circuit_breaker():
        return
    
    try:
        acquired = await asyncio.wait_for(voice_lock.acquire(), timeout=10.0)
        if not acquired:
            log('WARNING', f'No se pudo adquirir lock ({reason})')
            return
    except asyncio.TimeoutError:
        log('ERROR', f'Timeout adquiriendo lock ({reason})')
        return
    
    try:
        guild = client.get_guild(GUILD_ID_INT)
        if not guild:
            log('ERROR', f'No se encontro el guild {GUILD_ID_INT}')
            record_failure()
            return
        
        # Verificar si ya estamos conectados al canal correcto
        if guild.voice_client and guild.voice_client.is_connected():
            current_channel = guild.voice_client.channel
            if current_channel.id == channel_id:
                log('INFO', f'Ya conectado al canal objetivo #{current_channel.name}')
                reset_retry_count()
                last_connected_channel_id = channel_id
                return
            else:
                log('INFO', f'Conectado a canal diferente #{current_channel.name}, migrando...')
        
        channel = guild.get_channel(channel_id)
        if not channel:
            log('ERROR', f'No se encontro el canal de voz {channel_id}')
            record_failure()
            return
        
        # Desconectar voice client existente si hay uno
        if guild.voice_client:
            try:
                log('INFO', f'Desconectando de canal actual para migrar a #{channel.name}...')
                await guild.voice_client.disconnect(force=True)
                await asyncio.sleep(1)
            except Exception as e:
                log('WARNING', f'Error al desconectar voice client: {e}')
        
        # Conectar al canal
        log('INFO', f'Conectando a #{channel.name} (razon: {reason})...')
        
        voice = await channel.connect(
            self_mute=True,
            self_deaf=True,
            timeout=30,
            reconnect=False
        )
        
        log('INFO', f'[SUCCESS] Conectado a #{channel.name} (ID: {channel.id})')
        reset_retry_count()
        last_connected_channel_id = channel_id
        pending_disconnect = False
        
    except asyncio.TimeoutError:
        log('ERROR', f'Timeout al conectar')
        await handle_connection_failure(channel_id)
    except Exception as e:
        log('ERROR', f'Error al conectar: {type(e).__name__}: {e}')
        await handle_connection_failure(channel_id)
    finally:
        voice_lock.release()

@client.event
async def on_ready():
    log('INFO', f'Bot conectado como {client.user} (ID: {client.user.id})')
    log('INFO', f'Guild ID: {GUILD_ID_INT} {"[SERVIDOR ESPECIAL]" if IS_SPECIAL_GUILD else ""}')
    log('INFO', f'Canal objetivo ID: {TARGET_CHANNEL_ID}')
    log('INFO', f'Estado inicial: {get_current_voice_info()}')
    
    client.loop.create_task(monitor_voice())
    client.loop.create_task(periodic_status_report())
    
    await join_voice_channel(TARGET_CHANNEL_ID, reason="inicial")

@client.event
async def on_disconnect():
    log('WARNING', 'Gateway desconectado')

@client.event
async def on_resumed():
    log('INFO', 'Gateway reconectado')

@client.event
async def on_voice_state_update(member, before, after):
    """Manejar cambios de estado de voz del bot"""
    global pending_disconnect, last_connected_channel_id
    
    if member.id != client.user.id:
        return
    
    if before.channel == after.channel:
        return
    
    guild = client.get_guild(GUILD_ID_INT)
    
    log('INFO', f'Voice state: {before.channel} -> {after.channel}')
    
    if after.channel is None:
        # Desconectado
        pending_disconnect = True
        last_connected_channel_id = before.channel.id if before.channel else None
        
        log('WARNING', f'Desconectado de #{before.channel.name if before.channel else "?"}')
        
        wait_time = 1.0 if IS_SPECIAL_GUILD else 3.0
        await asyncio.sleep(wait_time)
        
        if not pending_disconnect:
            log('INFO', 'Desconexion ya manejada')
            return
        
        pending_disconnect = False
        
        # Verificar si ya reconecto
        guild = client.get_guild(GUILD_ID_INT)
        if guild and guild.voice_client and guild.voice_client.is_connected():
            log('INFO', f'Ya reconectado a #{guild.voice_client.channel.name}')
            reset_retry_count()
            return
        
        if IS_SPECIAL_GUILD:
            log('INFO', '[ESPECIAL] Reconectando inmediatamente...')
        else:
            log('INFO', f'Reconectando al canal {TARGET_CHANNEL_ID}...')
        
        await join_voice_channel(TARGET_CHANNEL_ID, reason="reconexion_post_desconexion")
        
    else:
        # Movido a otro canal - TARGET_CHANNEL_ID ya fue actualizado por el monkey-patch
        pending_disconnect = False
        last_connected_channel_id = after.channel.id
        log('INFO', f'Movido a #{after.channel.name} - nuevo canal objetivo: {TARGET_CHANNEL_ID}')

async def monitor_voice():
    """Monitorear estado de conexion de voz"""
    await client.wait_until_ready()
    await asyncio.sleep(5)
    
    while not client.is_closed():
        try:
            await asyncio.sleep(30)
            
            guild = client.get_guild(GUILD_ID_INT)
            if not guild:
                log('WARNING', f'Guild no encontrado')
                continue
            
            is_connected = guild.voice_client and guild.voice_client.is_connected()
            
            if is_connected:
                channel = guild.voice_client.channel
                log('DEBUG', f'Check: En #{channel.name}')
            else:
                log('WARNING', 'Check: Voz desconectada')
                
                if not voice_lock.locked() and not pending_disconnect:
                    log('INFO', 'Reconexion desde monitor...')
                    await join_voice_channel(TARGET_CHANNEL_ID, reason="monitor_reconexion")
                else:
                    log('INFO', f'Reconexion pospuesta: lock={voice_lock.locked()}, pending={pending_disconnect}')
                    
        except Exception as e:
            log('ERROR', f'Error en monitor: {e}')

async def periodic_status_report():
    """Reportar estado periodicamente"""
    await client.wait_until_ready()
    
    while not client.is_closed():
        try:
            await asyncio.sleep(300)
            
            guild = client.get_guild(GUILD_ID_INT)
            if guild and guild.voice_client and guild.voice_client.is_connected():
                channel = guild.voice_client.channel
                log('INFO', f'[STATUS] En #{channel.name} | Retries: {voice_retry_count} | Circuit: {circuit_breaker_failures}/{CIRCUIT_BREAKER_THRESHOLD}')
            else:
                log('INFO', f'[STATUS] Desconectado | Retries: {voice_retry_count} | Circuit: {circuit_breaker_failures}/{CIRCUIT_BREAKER_THRESHOLD}')
                
        except Exception as e:
            log('ERROR', f'Error en status: {e}')

if __name__ == '__main__':
    start_webserver()
    try:
        log('INFO', 'Iniciando bot...')
        client.run(TOKEN)
    except KeyboardInterrupt:
        log('INFO', 'Bot detenido por usuario')
    except Exception as e:
        log('CRITICAL', f'Error fatal: {e}')
