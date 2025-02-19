import discord
from discord.ext import commands
import requests
import random
from datetime import datetime
import os
import logging
from dotenv import load_dotenv
import pytz

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

# Datos de memes/GIFs (URLs ejemplo)
MEMES = {
    "33": ["url_alonso_1", "url_alonso_2"],
    "bwoah": ["url_kimi_1", "url_kimi_2"],
    "por_que_siempre_yo": ["url_hamilton_1"],
    "multi21": ["url_webber_vettel"],
    "vamos_a_plan": ["url_alpine_1", "url_alpine_2"]
}

@bot.event
async def on_ready():
    logging.info(f'Bot conectado como {bot.user}')

def obtener_resultados_carrera_por_nombre(nombre_carrera, temporada):
    url = f"https://api.jolpi.ca/ergast/f1/{temporada}/{nombre_carrera}/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error al obtener resultados de carrera: {e}")
        return None

    data = response.json()
    races = data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
    if not races:
        return None

    for race in races:
        if race.get('raceName', '').lower() == nombre_carrera.lower():
            results = race.get('Results', [])
            if not results:
                return f"No se encontraron resultados en la carrera '{nombre_carrera}' de la temporada {temporada}."
            mensaje = f"Resultados del {race.get('raceName')}:\n"
            for result in results:
                posicion = result.get('position')
                driver = result.get('Driver', {})
                nombre = driver.get('givenName', 'N/A')
                apellido = driver.get('familyName', 'N/A')
                mensaje += f"{posicion}. {nombre} {apellido}\n"
            return mensaje
    return None

def obtener_id_circuito(nombre_gp, año):
    url = f'https://api.jolpi.ca/ergast/f1/{año}/circuits'
    try:
        respuesta = requests.get(url, timeout=10)
        respuesta.raise_for_status()
        datos = respuesta.json()
        circuitos = datos.get('MRData', {}).get('CircuitTable', {}).get('Circuits', [])
        for circuito in circuitos:
            circuit_name = circuito.get('circuitName', '')
            if nombre_gp.lower() in circuit_name.lower():
                logging.info(f"Circuito encontrado: {circuit_name} (ID: {circuito.get('circuitId')})")
                return circuito.get('circuitId')
        logging.info("No se encontró ningún circuito que coincida con el nombre proporcionado.")
    except Exception as e:
        logging.error(f"Error al obtener ID del circuito: {e}")
    return None

def obtener_resultados(circuito_id, año):
    url = f'https://api.jolpi.ca/ergast/f1/{año}/circuits/{circuito_id}/results'
    try:
        respuesta = requests.get(url, timeout=10)
        respuesta.raise_for_status()
        datos = respuesta.json()
        races = datos.get('MRData', {}).get('RaceTable', {}).get('Races', [])
        if races:
            logging.info("Resultados encontrados para el circuito.")
            # Se verifica que exista la clave Results en la primera carrera
            return races[0].get('Results', [])
        else:
            logging.info("No se encontraron carreras en los datos del circuito.")
    except Exception as e:
        logging.error(f"Error al obtener resultados del circuito: {e}")
    return None

@bot.command(name='resultados')
async def resultados(ctx, carrera: str):
    resultados_carrera = obtener_resultados_carrera_por_nombre(carrera, "1")
    if resultados_carrera:
        await ctx.send(resultados_carrera)
    else:
        await ctx.send("No se encontraron resultados para la carrera especificada.")

@bot.command(name='carrera')
async def carrera(ctx, nombre_carrera: str, temporada: str):
    resultados = obtener_resultados_carrera_por_nombre(nombre_carrera, temporada)
    if resultados:
        await ctx.send(f"Resultados del {nombre_carrera} de la temporada {temporada}:\n{resultados}")
    else:
        await ctx.send(f"No se encontraron resultados para el {nombre_carrera} de la temporada {temporada}.")

@bot.command(name='clasificacion')
async def clasificacion(ctx):
    try:
        response = requests.get('https://api.jolpica-f1.vercel.app/ergast/f1/current/driverStandings.json', timeout=10)
        response.raise_for_status()
        data = response.json()
        standings = data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']

        embed = discord.Embed(title="🏎️ Clasificación actual de pilotos", color=discord.Color.blue())
        for driver in standings[:10]:
            embed.add_field(name=f"{driver['position']}. {driver['Driver']['givenName']} {driver['Driver']['familyName']}",
                            value=f"{driver['points']} pts", inline=False)

        await ctx.send(embed=embed)
    except Exception as e:
        logging.error(f"Error al obtener la clasificación: {e}")
        await ctx.send("❌ Error al obtener la clasificación")

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

@bot.command(name='meme')
async def meme(ctx, tipo: str):
    tipo = tipo.lower()
    if (tipo in MEMES):
        meme_url = random.choice(MEMES[tipo])
        await ctx.send(meme_url)
    else:
        await ctx.send("❌ Meme no encontrado. Opciones disponibles: 33, bwoah, por_que_siempre_yo, multi21, vamos_a_plan")

@bot.command(name='circuito')
async def circuito(ctx, nombre: str):
    try:
        response = requests.get(f'https://api.jolpica-f1.vercel.app/ergast/f1/circuits/{nombre}.json', timeout=10)
        response.raise_for_status()
        data = response.json()
        circuit = data['MRData']['CircuitTable']['Circuits'][0]

        embed = discord.Embed(title="🏁 Información del circuito", color=discord.Color.gold())
        embed.add_field(name="Nombre", value=circuit['circuitName'], inline=False)
        embed.add_field(name="Localización", value=f"{circuit['Location']['locality']}, {circuit['Location']['country']}", inline=False)
        embed.add_field(name="Coordenadas", value=f"{circuit['Location']['lat']}, {circuit['Location']['long']}", inline=False)

        await ctx.send(embed=embed)
    except Exception as e:
        logging.error(f"Error al obtener información del circuito: {e}")
        await ctx.send("❌ Error al obtener información del circuito")

@bot.command(name='ayuda')
async def help_command(ctx):
    embed = discord.Embed(
        title="📖 Comandos Disponibles",
        description="Lista de todos los comandos que puedes usar",
        color=discord.Color.blue()
    )

    embed.add_field(name="!ayuda", value="Muestra este mensaje de ayuda", inline=False)
    embed.add_field(name="!meme [piloto]", value="Muestra un meme aleatorio (o de un piloto específico)", inline=False)
    embed.add_field(name="!carrera [temporada] [numero_carrera]", value="Muestra los resultados de una carrera específica por temporada y número de carrera", inline=False)
    embed.add_field(name="!clasificacion", value="Muestra la clasificación actual de pilotos", inline=False)
    embed.add_field(name="!proxima", value="Muestra información de la próxima carrera", inline=False)
    embed.add_field(name="!circuito [nombre]", value="Muestra información de un circuito específico", inline=False)
    embed.add_field(name="!indice_carreras", value="Muestra un índice de carreras disponibles", inline=False)

    embed.set_footer(text="Usa ! antes de cada comando")

    await ctx.send(embed=embed)

@bot.command(name='indice_carreras')
async def indice_carreras(ctx):
    try:
        response = requests.get('https://api.jolpica-f1.vercel.app/ergast/f1/current.json', timeout=10)
        response.raise_for_status()
        data = response.json()
        races = data['MRData']['RaceTable']['Races']

        mensaje = "📅 **Índice de Carreras de la Temporada Actual:**\n\n"
        for race in races:
            mensaje += f"{race['round']}. {race['raceName']} - {race['Circuit']['circuitName']}\n"

        await ctx.send(mensaje)
    except Exception as e:
        logging.error(f"Error al obtener el índice de carreras: {e}")
        await ctx.send("❌ Error al obtener el índice de carreras")

@bot.command(name='resultados_circuito')
async def resultados_circuito(ctx, nombre_gp: str, año: str):
    circuito_id = obtener_id_circuito(nombre_gp, año)
    if not circuito_id:
        await ctx.send(f"No se encontró el Gran Premio '{nombre_gp}' en el año {año}.")
        return

    resultados = obtener_resultados(circuito_id, año)
    if not resultados:
        await ctx.send(f"No se encontraron resultados para el Gran Premio '{nombre_gp}' en el año {año}.")
        return

    mensaje = f"Resultados del Gran Premio '{nombre_gp}' en {año}:\n\n"
    for resultado in resultados:
        posicion = resultado.get('position', 'N/A')
        driver = resultado.get('Driver', {})
        piloto = f"{driver.get('givenName', 'N/A')} {driver.get('familyName', 'N/A')}"
        nacionalidad = driver.get('nationality', 'N/A')
        equipo = resultado.get('Constructor', {}).get('name', 'N/A')
        tiempo = resultado.get('Time', {}).get('time', 'N/A')
        mensaje += (f"Posición: {posicion}\n"
                    f"Piloto: {piloto}\n"
                    f"Nacionalidad: {nacionalidad}\n"
                    f"Equipo: {equipo}\n"
                    f"Tiempo: {tiempo}\n\n")
    
    await ctx.send(mensaje)

def main():
    try:
        bot.run(token)
    except discord.errors.LoginFailure:
        logging.error("Error: Token inválido. Por favor verifica el token en el archivo .env")
    except Exception as e:
        logging.error(f"Error inesperado: {e}")

if __name__ == "__main__":
    main()
