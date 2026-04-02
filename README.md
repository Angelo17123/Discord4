# Self-Bot de Discord con Funcionalidades de Voz

Un self-bot de Discord que se une a un canal de voz específico, permanece muteado y ensordecido, y reconecta automáticamente si es movido o desconectado.

## ⚠️ Advertencia Importante

El uso de self-bots viola los Todos de Servicio de Discord. Tu cuenta puede ser suspendida permanentemente. Usa este bot bajo tu propia responsabilidad.

## Características

- Se une automáticamente a un canal de voz específico
- Permanece muteado y ensordecido (self_mute, self_deaf)
- Detecta cuando es movido a otro canal y mantiene la conexión
- Reconecta automáticamente si es desconectado
- Mantiene la conexión activa para evitar timeouts

## Requisitos

- Python 3.10 o superior
- Cuenta de Discord (token de usuario)
- Acceso a un servidor y canal de voz

## Configuración

1. **Clona o descarga este repositorio**

2. **Ejecuta el script de instalación**:
   ```bash
   install.bat
   ```

3. **Edita el archivo `.env`** con tus credenciales:
   ```
   TOKEN=your_discord_user_token_here
   GUILD_ID=your_guild_id_here
   CHANNEL_ID=your_voice_channel_id_here
   ```

## Uso

1. **Ejecuta el bot**:
   ```bash
   run.bat
   ```

2. El bot se conectará automáticamente al canal de voz especificado.

3. Para detener el bot, presiona `Ctrl+C` en la consola.

## Estructura del Proyecto

```
discord-selfbot-python/
├── src/
│   └── bot.py          # Código principal del bot
├── .env                # Variables de entorno (token, IDs)
├── .gitignore          # Archivos ignorados por git
├── install.bat         # Script de instalación
├── run.bat             # Script de ejecución
└── README.md           # Este archivo
```

## Notas Técnicas

- Utiliza `discord.py-self`, una bifurcación de discord.py para cuentas de usuario
- La reconexión se maneja a través del evento `on_voice_state_update`
- La conexión se mantiene activa con verificaciones periódicas

## Solución de Problemas

- **No se conecta al canal**: Verifica que los IDs sean correctos y que el bot tenga acceso al servidor
- **Timeout de conexión**: Aumenta el timeout en `bot.py` o verifica la conexión a internet
- **Error de token**: Asegúrate de que el token sea válido y no haya expirado

## Licencia

Este proyecto es solo para fines educativos. Úsalo bajo tu propio riesgo.