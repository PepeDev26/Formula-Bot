import discord
from discord.ext import commands
import requests
import random
from datetime import datetime
import os
import logging
from dotenv import load_dotenv
import pytz
import re

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
    circuitos_especiales = {
        "mexico": "rodriguez",
        "interlagos": "interlagos",
        "brasil": "interlagos",
        "brazilian": "interlagos",
        "albert park": "albert_park",
        "australia": "albert_park",
        "melbourne": "albert_park",
        "americas": "americas",
        "usa": "americas",
        "united states": "americas",
        "cota": "americas",
        "austin": "americas",
        "abu dhabi": "yas_marina",
        "arabia": "jeddah",
        "saudi": "jeddah",
        "jeddah": "jeddah",
        "las vegas": "vegas",
        "monaco": "monaco",
        "mexican": "rodriguez",
        "silverstone": "silverstone",
        "britain": "silverstone",
        "british": "silverstone",
        "monza": "monza",
        "italy": "monza",
        "italian": "monza",
        "spa": "spa",
        "belgium": "spa",
        "belgian": "spa",
        "hungaroring": "hungaroring",
        "hungary": "hungaroring",
        "hungarian": "hungaroring",
        "zandvoort": "zandvoort",
        "netherlands": "zandvoort",
        "dutch": "zandvoort",
        "suzuka": "suzuka",
        "japan": "suzuka",
        "japanese": "suzuka",
        "barcelona": "catalunya",
        "catalunya": "catalunya",
        "spain": "catalunya",
        "spanish": "catalunya",
        "baku": "baku",
        "azerbaijan": "baku",
        "shanghai": "shanghai",
        "china": "shanghai",
        "chinese": "shanghai",
        "bahrain": "bahrain",
        "sakhir": "bahrain",
        "imola": "imola",
        "emilia": "imola",
        "romagna": "imola",
        "portugal": "portimao",
        "portimao": "portimao",
        "singapore": "marina_bay",
        "marina bay": "marina_bay",
        "montreal": "villeneuve",
        "canada": "villeneuve",
        "canadian": "villeneuve",
        "villeneuve": "villeneuve",
        "istanbul": "istanbul",
        "turkey": "istanbul",
        "turkish": "istanbul",
        "sochi": "sochi",
        "russia": "sochi",
        "russian": "sochi",
        "austria": "red_bull_ring",
        "red bull ring": "red_bull_ring",
        "styrian": "red_bull_ring",
        "sepang": "sepang",
        "malaysia": "sepang",
        "malaysian": "sepang",
        "nurburgring": "nurburgring",
        "germany": "nurburgring",
        "german": "nurburgring",
        "hockenheim": "hockenheimring",
        "france": "paul_ricard",
        "french": "paul_ricard",
        "paul ricard": "paul_ricard",
        "hanoi": "hanoi",
        "vietnam": "hanoi",
        "vietnamese": "hanoi",
        "losail": "losail",
        "qatar": "losail",
        "qatari": "losail",
        "miami": "miami",
        "yas marina": "yas_marina"
    }
    
    nombre_busqueda = nombre_gp.lower().strip()
    
    # Primero intentamos con el diccionario de circuitos especiales
    if nombre_busqueda in circuitos_especiales:
        nombre_busqueda = circuitos_especiales[nombre_busqueda]

    try:
        # Para años anteriores a 2012, usar una API alternativa o ajustar la búsqueda
        url = f'https://api.jolpi.ca/ergast/f1/{año}/circuits'
        respuesta = requests.get(url, timeout=10)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            
            # Si no hay circuitos en la respuesta, puede ser un problema con la API
            if 'MRData' not in datos or 'CircuitTable' not in datos['MRData'] or 'Circuits' not in datos['MRData']['CircuitTable']:
                logging.error(f"Formato de respuesta inesperado para año {año}")
                return None
            
            circuits = datos['MRData']['CircuitTable']['Circuits']
            if not circuits:
                logging.warning(f"No se encontraron circuitos para el año {año}")
                # Intentemos con el año más reciente disponible
                return buscar_circuito_en_años_recientes(nombre_busqueda)
                
            for circuito in circuits:
                nombre_circuito = circuito['circuitName'].lower()
                circuito_id = circuito['circuitId'].lower()
                
                # Buscar coincidencias en nombre del circuito o ID
                if (nombre_busqueda in nombre_circuito or 
                    nombre_circuito in nombre_busqueda or 
                    nombre_busqueda in circuito_id or
                    re.search(nombre_busqueda, nombre_circuito) or
                    re.search(nombre_busqueda, circuito_id)):
                    return circuito['circuitId']
                    
        else:
            logging.error(f"Error al obtener circuitos para año {año}: {respuesta.status_code}")
            return buscar_circuito_en_años_recientes(nombre_busqueda)
            
    except Exception as e:
        logging.error(f"Excepción al buscar circuito '{nombre_gp}' en {año}: {e}")
        return buscar_circuito_en_años_recientes(nombre_busqueda)
        
    return None

def buscar_circuito_en_años_recientes(nombre_busqueda):
    """Intenta encontrar un circuito en años recientes cuando falla la búsqueda en el año especificado"""
    años_a_probar = ["2023", "2022", "2021", "2020", "2019"]
    
    for año in años_a_probar:
        try:
            url = f'https://api.jolpi.ca/ergast/f1/{año}/circuits'
            respuesta = requests.get(url, timeout=10)
            if respuesta.status_code == 200:
                datos = respuesta.json()
                circuits = datos['MRData']['CircuitTable']['Circuits']
                
                for circuito in circuits:
                    nombre_circuito = circuito['circuitName'].lower()
                    circuito_id = circuito['circuitId'].lower()
                    
                    if (nombre_busqueda in nombre_circuito or 
                        nombre_circuito in nombre_busqueda or 
                        nombre_busqueda in circuito_id):
                        logging.info(f"Circuito encontrado en año alternativo {año}: {circuito['circuitId']}")
                        return circuito['circuitId']
        except Exception as e:
            logging.error(f"Error buscando en año alternativo {año}: {e}")
            continue
    
    return None

def obtener_resultados(circuito_id, año):
    try:
        url = f'https://api.jolpi.ca/ergast/f1/{año}/circuits/{circuito_id}/results'
        respuesta = requests.get(url, timeout=10)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            if ('MRData' in datos and 'RaceTable' in datos['MRData'] and 
                'Races' in datos['MRData']['RaceTable'] and 
                len(datos['MRData']['RaceTable']['Races']) > 0):
                return datos['MRData']['RaceTable']['Races'][0]['Results']
            else:
                logging.warning(f"No se encontraron resultados para circuito {circuito_id} en año {año}")
                return None
        else:
            logging.error(f"Error al obtener resultados: {respuesta.status_code}")
            return None
    except Exception as e:
        logging.error(f"Excepción al buscar resultados para {circuito_id} en {año}: {e}")
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
        "Argentinian": "🇦🇷",
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
    """Obtiene los resultados de un Gran Premio específico"""
    await ctx.send(f"🔍 Buscando resultados para '{nombre_gp}' en {año}...")
    
    circuito_id = obtener_id_circuito(nombre_gp, año)
    if not circuito_id:
        await ctx.send(f"❌ No se encontró el Gran Premio '{nombre_gp}' en el año {año}. Por favor verifica el nombre del circuito o Gran Premio.")
        return

    resultados = obtener_resultados(circuito_id, año)
    if not resultados:
        await ctx.send(f"❌ No se encontraron resultados para el Gran Premio '{nombre_gp}' en el año {año}. Puede que esta carrera no se haya celebrado o haya un error en la API.")
        return

    try:
        embed = discord.Embed(title=f"Resultados del Gran Premio '{nombre_gp}' en {año}", color=discord.Color.blue())
        
        # Limitamos a 25 resultados por embed para evitar límites de Discord
        max_resultados = min(25, len(resultados))
        for i in range(max_resultados):
            resultado = resultados[i]
            posicion = resultado.get('position', 'N/A')
            driver = resultado.get('Driver', {})
            piloto = f"{driver.get('givenName', 'N/A')} {driver.get('familyName', 'N/A')}"
            nacionalidad = driver.get('nationality', 'N/A')
            bandera = obtener_bandera(nacionalidad)
            equipo = resultado.get('Constructor', {}).get('name', 'N/A')
            
            # Manejo de tiempo más robusto
            if 'Time' in resultado and resultado['Time']:
                tiempo = resultado['Time'].get('time', 'N/A')
            elif 'status' in resultado:
                tiempo = resultado['status']  # Para DNF, DSQ, etc.
            else:
                tiempo = 'N/A'
                
            embed.add_field(
                name=f"Posición {posicion}",
                value=f"Piloto: {piloto}\nNacionalidad: {bandera} {nacionalidad}\nEquipo: {equipo}\nTiempo: {tiempo}",
                inline=False
            )
        
        await ctx.send(embed=embed)
        
        # Si hay más de 25 resultados, enviamos embeds adicionales
        if len(resultados) > 25:
            remaining = len(resultados) - 25
            chunks = (remaining + 24) // 25  # Calcular cuántos embeds adicionales necesitamos
            
            for chunk in range(chunks):
                start_idx = 25 + (chunk * 25)
                end_idx = min(start_idx + 25, len(resultados))
                
                embed = discord.Embed(
                    title=f"Resultados del Gran Premio '{nombre_gp}' en {año} (continuación {chunk+1})",
                    color=discord.Color.blue()
                )
                
                for i in range(start_idx, end_idx):
                    resultado = resultados[i]
                    # ... (mismo código para cada resultado)
                    posicion = resultado.get('position', 'N/A')
                    driver = resultado.get('Driver', {})
                    piloto = f"{driver.get('givenName', 'N/A')} {driver.get('familyName', 'N/A')}"
                    nacionalidad = driver.get('nationality', 'N/A')
                    bandera = obtener_bandera(nacionalidad)
                    equipo = resultado.get('Constructor', {}).get('name', 'N/A')
                    
                    if 'Time' in resultado and resultado['Time']:
                        tiempo = resultado['Time'].get('time', 'N/A')
                    elif 'status' in resultado:
                        tiempo = resultado['status']
                    else:
                        tiempo = 'N/A'
                        
                    embed.add_field(
                        name=f"Posición {posicion}",
                        value=f"Piloto: {piloto}\nNacionalidad: {bandera} {nacionalidad}\nEquipo: {equipo}\nTiempo: {tiempo}",
                        inline=False
                    )
                
                await ctx.send(embed=embed)
    except Exception as e:
        logging.error(f"Error al procesar resultados: {e}")
        await ctx.send("❌ Se produjo un error al procesar los resultados. Por favor, inténtalo más tarde.")


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
    """
    Obtener información de un piloto de F1 por su nombre.
    
    Args:
        ctx: Contexto del comando.
        nombre_piloto: Nombre del piloto a buscar.
    """
    url = f'https://api.jolpi.ca/ergast/f1/drivers/{nombre_piloto}'
    respuesta = requests.get(url, timeout=10)
    if respuesta.status_code == 200:
        datos = respuesta.json()
        piloto = datos['MRData']['DriverTable']['Drivers'][0]
        nombre = f"{piloto['givenName']} {piloto['familyName']}"
        fecha_nacimiento = piloto['dateOfBirth']
        nacionalidad = piloto['nationality']

        embed = discord.Embed(title=f"Información de {nombre}", color=discord.Color.gold())
        embed.add_field(name="Nombre", value=nombre, inline=False)
        embed.add_field(name="Fecha de nacimiento", value=fecha_nacimiento, inline=False)
        embed.add_field(name="Nacionalidad", value=nacionalidad, inline=False)

        await ctx.send(embed=embed)
    else:
        await ctx.send(f"No se encontró información para el piloto '{nombre_piloto}'.")

@bot.command(name='mundialpilotos')
async def mundial_pilotos(ctx, año: str = "current"):
    """Obtiene la clasificación del mundial de pilotos"""
    try:
        url = f'https://api.jolpi.ca/ergast/f1/{año}/driverStandings'
        respuesta = requests.get(url, timeout=10)
        respuesta.raise_for_status()
        
        datos = respuesta.json()
        clasificacion = datos['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']

        # Crear múltiples embeds si hay más de 25 pilotos
        pilotos_por_embed = 25
        total_pilotos = len(clasificacion)
        numero_embeds = (total_pilotos + pilotos_por_embed - 1) // pilotos_por_embed

        for i in range(numero_embeds):
            inicio = i * pilotos_por_embed
            fin = min((i + 1) * pilotos_por_embed, total_pilotos)
            
            titulo = f"🏆 Clasificación Mundial de Pilotos {año}"
            if numero_embeds > 1:
                titulo += f" (Parte {i+1}/{numero_embeds})"

            embed = discord.Embed(
                title=titulo,
                color=discord.Color.gold()
            )

            for piloto in clasificacion[inicio:fin]:
                try:
                    posicion = piloto.get('position', 'N/A')
                    driver = piloto.get('Driver', {})
                    nombre = f"{driver.get('givenName', 'N/A')} {driver.get('familyName', 'N/A')}"
                    puntos = piloto.get('points', '0')
                    constructores = piloto.get('Constructors', [{}])
                    equipo = constructores[0].get('name', 'N/A') if constructores else 'N/A'
                    nacionalidad = driver.get('nationality', 'N/A')
                    bandera = obtener_bandera(nacionalidad)

                    embed.add_field(
                        name=f"{posicion}. {nombre} {bandera}",
                        value=f"Puntos: {puntos}\nEquipo: {equipo}",
                        inline=False
                    )
                except Exception as e:
                    logging.error(f"Error procesando piloto: {e}")
                    continue

            await ctx.send(embed=embed)

    except Exception as e:
        logging.error(f"Error al obtener clasificación de pilotos: {e}")
        await ctx.send("❌ Error al obtener la clasificación del mundial de pilotos")

@bot.command(name='constructores')
async def mundial_constructores(ctx, año: str = "current"):
    """Obtiene la clasificación del mundial de constructores"""
    try:
        url = f'https://api.jolpi.ca/ergast/f1/{año}/constructorStandings'
        respuesta = requests.get(url, timeout=10)
        respuesta.raise_for_status()
        
        datos = respuesta.json()
        clasificacion = datos['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']

        embed = discord.Embed(
            title=f"🏆 Clasificación Mundial de Constructores {año}", 
            color=discord.Color.blue()
        )

        for constructor in clasificacion:
            posicion = constructor['position']
            nombre = constructor['Constructor']['name']
            puntos = constructor['points']
            nacionalidad = constructor['Constructor']['nationality']
            bandera = obtener_bandera(nacionalidad)

            embed.add_field(
                name=f"{posicion}. {nombre} {bandera}",
                value=f"Puntos: {puntos}",
                inline=False
            )

        await ctx.send(embed=embed)
    except Exception as e:
        logging.error(f"Error al obtener clasificación de constructores: {e}")
        await ctx.send("❌ Error al obtener la clasificación del mundial de constructores")


# Comando para mandar un gif de Carlos Sainz en McLaren cantando Smooth Operator
@bot.command(name='sainz')
async def sainz(ctx):
    gifs = [
        "https://media1.tenor.com/m/aFg7WRHu9gAAAAAC/f1-carlos-sainz.gif",
        "https://media1.tenor.com/m/XIJE7knWL_UAAAAd/treatsbettr-carlos-sainz.gif"
    ]
    gif = random.choice(gifs)
    await ctx.send(gif)
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
