# 🏎️ Formula Bot - Bot de Discord para Fórmula 1

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Discord.py](https://img.shields.io/badge/discord.py-2.0+-blue.svg)](https://discordpy.readthedocs.io/en/stable/)

Bot de Discord que proporciona información completa sobre la Fórmula 1, incluyendo resultados de carreras, clasificaciones, información de pilotos, equipos, calendarios y más, utilizando la API Ergast F1.

## ✨ Características principales

- Consulta de resultados de carreras históricas desde 1950
- Clasificación actual e histórica de pilotos y equipos
- Información detallada sobre pilotos y constructores
- Calendario de temporadas pasadas y actuales
- Información sobre la próxima carrera
- Comandos divertidos con GIFs de pilotos y equipos

## 📋 Requisitos previos

- Python 3.8 o superior
- Cuenta de Discord y permisos para añadir bots
- Token de bot de Discord (obtenido desde [Discord Developer Portal](https://discord.com/developers/applications))

## 🚀 Instalación

1. Clone este repositorio o descargue los archivos:

```bash
git clone https://github.com/tuusuario/formula-bot.git
cd formula-bot
```

2. Instale las dependencias necesarias:

```bash
pip install -r requirements.txt
```

3. Cree un archivo `.env` en el directorio raíz con su token de Discord:

```
DISCORD_TOKEN=su_token_aqui
```

4. Ejecute el bot:

```bash
python BotMain.py
```

## 📝 Comandos disponibles

### Información sobre carreras

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `!calendario [año]` | Muestra el calendario completo de una temporada | `!calendario 2023` |
| `!resultados [nombre_gp] [año]` | Muestra los resultados de un Gran Premio específico | `!resultados monaco 2022` |
| `!proxima` | Muestra información sobre la próxima carrera | `!proxima` |

### Pilotos y equipos

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `!piloto [nombre]` | Muestra información sobre un piloto específico | `!piloto alonso` |
| `!mundialpilotos [año]` | Muestra la clasificación del mundial de pilotos | `!mundialpilotos 2023` |
| `!constructores [año]` | Muestra la clasificación del mundial de constructores | `!constructores 2023` |

### Comandos divertidos

| Comando | Descripción |
|---------|-------------|
| `!33` | Muestra un GIF de Fernando Alonso |
| `!smoothoperator` | Muestra un GIF de Carlos Sainz |
| `!totowolffdescuido` | Muestra un GIF de Toto Wolff |
| `!laqueriatanto` | Muestra un GIF de Fernando Alonso mirando fijamente |
| `!bwoah` | Muestra un GIF aleatorio de Kimi Räikkönen |

### Ayuda

| Comando | Descripción |
|---------|-------------|
| `!ayuda` | Muestra la lista completa de comandos disponibles |

## 🔍 Consejos para búsqueda de carreras

Para encontrar resultados de un Gran Premio, puedes utilizar diferentes términos de búsqueda:

- **Nombre del GP**: `!resultados Spanish 2023`
- **Nombre del país**: `!resultados Spain 2023`
- **Nombre del circuito**: `!resultados Catalunya 2023`
- **Apodo común**: `!resultados Barcelona 2023`

El bot utiliza un sistema de coincidencia flexible para identificar circuitos, incluso con búsquedas aproximadas.

### Búsquedas alternativas por circuito

| País | Términos de búsqueda aceptados |
|------|-------------------------------|
| España | Spain, Spanish, Catalunya, Barcelona |
| Italia | Italy, Italian, Monza, Imola |
| Reino Unido | Britain, British, Silverstone |
| Estados Unidos | USA, United States, Americas, COTA, Austin, Miami, Las Vegas |
| México | Mexico, Mexican, Rodriguez |

## 🛠️ Configuración avanzada

El bot está configurado para funcionar con configuración mínima, pero puedes personalizar:

- El prefijo de los comandos (por defecto `!`)
- Los permisos (intents) requeridos en Discord
- El sistema de logging

## 🌐 API utilizada

Este bot utiliza la API Ergast F1, alojada en [https://api.jolpi.ca/ergast/](https://api.jolpi.ca/ergast/), que es un espejo de la API oficial de Ergast Motor Racing Data. La API proporciona datos históricos completos de Fórmula 1 desde 1950.

## 📊 Ejemplos de respuesta

El bot responde con embeds de Discord que incluyen información formateada:

- Los resultados de carrera muestran posición, nombre del piloto, equipo y tiempo
- Las clasificaciones de campeonato incluyen posición, nombre, nacionalidad (con bandera) y puntos
- La información de pilotos incluye datos biográficos e históricos

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Consulte el archivo LICENSE para más detalles.

## 👥 Contribuciones

Las contribuciones son bienvenidas. Por favor, abra un issue para discutir los cambios antes de enviar pull requests.
