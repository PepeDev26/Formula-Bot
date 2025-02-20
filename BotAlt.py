import discord
from discord.ext import commands
import requests
import random
from datetime import datetime
import os
import logging
from dotenv import load_dotenv
import pytz

#A
# Configuración de logging
logging.basicConfig(level=logging.INFO)

# Cargar variables de entorno
load_dotenv()

# Obtener y verificar el token
token = os.getenv('DISCORD_TOKEN')
if not token:
    raise ValueError("No se encontró el token de Discord en las variables de entorno. Asegúrate de tener un archivo .env con DISCORD_TOKEN=tu_token")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Funciones para obtener datos de carreras

def obtener_id_circuito(nombre_gp, año):
    url = f'https://api.jolpi.ca/ergast/f1/{año}/circuits'
    respuesta = requests.get(url)
    if respuesta.status_code == 200:
        datos = respuesta.json()
        for circuito in datos['MRData']['CircuitTable']['Circuits']:
            if nombre_gp.lower() in circuito['circuitName'].lower():
                return circuito['circuitId']
    return None

def obtener_resultados(circuito_id, año):
    url = f'https://api.jolpi.ca/ergast/f1/{año}/circuits/{circuito_id}/results'
    respuesta = requests.get(url)
    if respuesta.status_code == 200:
        datos = respuesta.json()
        return datos['MRData']['RaceTable']['Races'][0]['Results']
    return None

def obtener_bandera(nacionalidad):
    banderas = {
        "British": "🇬🇧",
        "German": "🇩🇪",
        "Spanish": "🇪🇸",
        "French": "🇫🇷",
        "Italian": "🇮🇹",
        "Dutch": "🇳🇱",
        "Finnish": "🇫🇮",
        "Australian": "🇦🇺",
        "Canadian": "🇨🇦",
        "Brazilian": "🇧🇷",
        "Mexican": "🇲🇽",
        "American": "🇺🇸",
        "Russian": "🇷🇺",
        "Japanese": "🇯🇵",
        "Austrian": "🇦🇹",
        "Argentine": "🇦🇷",
        "Swiss": "🇨🇭",
        "Belgian": "🇧🇪",
        "Danish": "🇩🇰",
        "Swedish": "🇸🇪",
        "South African": "🇿🇦",
        "Portuguese": "🇵🇹",
        "New Zealander": "🇳🇿",
        "Indian": "🇮🇳",
        "Malaysian": "🇲🇾",
        "Colombian": "🇨🇴",
        "Venezuelan": "🇻🇪",
        "Polish": "🇵🇱",
        "Czech": "🇨🇿",
        "Hungarian": "🇭🇺",
        "Indonesian": "🇮🇩",
        "Thai": "🇹🇭",
        "Chinese": "🇨🇳",
        "Korean": "🇰🇷",
        "Bahraini": "🇧🇭",
        "Qatari": "🇶🇦",
        "Emirati": "🇦🇪",
        "Saudi": "🇸🇦",
        "Kuwaiti": "🇰🇼",
        "Monegasque": "🇲🇨",
    }
    return banderas.get(nacionalidad, '')

# Consultar calendario de una temporada
@bot.command(name='calendario')
async def calendario_temporada(ctx, año: str):
    url = f'https://api.jolpi.ca/ergast/f1/{año}/races'
    respuesta = requests.get(url)
    if respuesta.status_code == 200:
        datos = respuesta.json()
        carreras = datos['MRData']['RaceTable']['Races']
        if not carreras:
            await ctx.send(f"No se encontró información de carreras para la temporada {año}.")
            return

        embed = discord.Embed(title=f"Calendario de la temporada {año}", color=discord.Color.blue())
        for carrera in carreras:
            nombre_gp = carrera['raceName']
            fecha = carrera['date']
            circuito = carrera['Circuit']['circuitName']
            embed.add_field(name=nombre_gp, value=f"Circuito: {circuito}\nFecha: {fecha}", inline=False)
        
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"Error al obtener el calendario para la temporada {año}.")



# Comando para obtener resultados de un Gran Premio
@bot.command(name='resultados')
async def resultados_circuito(ctx, nombre_gp: str, año: str):
    circuito_id = obtener_id_circuito(nombre_gp, año)
    if not circuito_id:
        await ctx.send(f"No se encontró el Gran Premio '{nombre_gp}' en el año {año}.")
        return

    resultados = obtener_resultados(circuito_id, año)
    if not resultados:
        await ctx.send(f"No se encontraron resultados para el Gran Premio '{nombre_gp}' en el año {año}.")
        return

    embed = discord.Embed(title=f"Resultados del Gran Premio '{nombre_gp}' en {año}", color=discord.Color.blue())
    for resultado in resultados:
        posicion = resultado.get('position', 'N/A')
        driver = resultado.get('Driver', {})
        piloto = f"{driver.get('givenName', 'N/A')} {driver.get('familyName', 'N/A')}"
        nacionalidad = driver.get('nationality', 'N/A')
        bandera = obtener_bandera(nacionalidad)
        equipo = resultado.get('Constructor', {}).get('name', 'N/A')
        tiempo = resultado.get('Time', {}).get('time', 'N/A')
        embed.add_field(name=f"Posición {posicion}", value=f"Piloto: {piloto}\nNacionalidad: {bandera} {nacionalidad}\nEquipo: {equipo}\nTiempo: {tiempo}", inline=False)
    
    await ctx.send(embed=embed)


#Comando para las carreras siguientes
@bot.command(name='proxima')
async def proxima_carrera(ctx):
    try:
        response = requests.get('https://api.jolpi.ca/ergast/f1/2025/races', timeout=10)
        response.raise_for_status()
        data = response.json()
        races = data['MRData']['RaceTable']['Races']
        if not races:
            await ctx.send("❌ No se encontró información de carreras")
            return

        now = datetime.utcnow()
        upcoming = []
        for race in races:
            race_date = race.get('date')
            race_time = race.get('time', "00:00:00Z")
            race_datetime = datetime.strptime(f"{race_date} {race_time}", "%Y-%m-%d %H:%M:%SZ")
            if race_datetime > now:
                upcoming.append((race_datetime, race))
        
        if not upcoming:
            await ctx.send("❌ No se encontró información de la próxima carrera")
            return

        # Seleccionar la carrera más próxima
        next_race = min(upcoming, key=lambda x: x[0])[1]
        race_date = next_race.get('date')
        race_time = next_race.get('time', "00:00:00Z")
        race_datetime = datetime.strptime(f"{race_date} {race_time}", "%Y-%m-%d %H:%M:%SZ")
        race_datetime_madrid = race_datetime.replace(tzinfo=pytz.UTC).astimezone(pytz.timezone('Europe/Madrid'))

        embed = discord.Embed(title="📅 Próxima carrera", color=discord.Color.green())
        embed.add_field(name="GP", value=next_race['raceName'], inline=False)
        embed.add_field(name="Circuito", value=next_race['Circuit']['circuitName'], inline=False)
        embed.add_field(name="Fecha", value=race_datetime_madrid.strftime('%d/%m/%Y %H:%M') + " (hora española)", inline=False)

        await ctx.send(embed=embed)
    except Exception as e:
        logging.error(f"Error al obtener información de la próxima carrera: {e}")
        await ctx.send("❌ Error al obtener información de la próxima carrera")


# Comando para obtener información de un piloto
@bot.command(name='piloto')
async def info_piloto(ctx, nombre_piloto: str):
    url = f'https://api.jolpi.ca/ergast/f1/drivers/{nombre_piloto}'
    respuesta = requests.get(url)
    if respuesta.status_code == 200:
        datos = respuesta.json()
        piloto = datos['MRData']['DriverTable']['Drivers'][0]
        nombre = f"{piloto['givenName']} {piloto['familyName']}"
        fecha_nacimiento = piloto['dateOfBirth']
        nacionalidad = piloto

        embed = discord.Embed(title=f"Información de {nombre}", color=discord.Color.gold())
        embed.add_field(name="Nombre", value=nombre, inline=False)
        embed.add_field(name="Fecha de nacimiento", value=fecha_nacimiento, inline=False)
        embed.add_field(name="Nacionalidad", value=nacionalidad, inline=False)

# Evento de terminal cuando el bot esté listo
@bot.event
async def on_ready():
    logging.info(f'Bot conectado como {bot.user}')

# Iniciar el bot
if __name__ == "__main__":
    try:
        bot.run(token)
    except discord.errors.LoginFailure:
        logging.error("Error: Token inválido. Por favor verifica el token en el archivo .env")
    except Exception as e:
        logging.error(f"Error inesperado: {e}")
