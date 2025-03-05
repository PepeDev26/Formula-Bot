###############################################################################
# Bot de Discord para Fórmula 1
# 
# Este bot proporciona información sobre Fórmula 1 mediante comandos de Discord.
# Permite consultar resultados de carreras, clasificaciones, información de 
# pilotos, circuitos y más a través de la API Ergast F1.
# 
# Funcionalidades:
# - Consulta de resultados de carreras históricas
# - Información sobre pilotos y clasificación
# - Datos de constructores
# - Calendario de temporadas
# - Próximas carreras
###############################################################################

# Importación de librerías
import discord                # Biblioteca principal para interactuar con Discord
from discord.ext import commands  # Extensión para comandos de Discord
import requests              # Para hacer peticiones HTTP a la API
import random                # Para selección aleatoria de GIFs
from datetime import datetime # Para manejo de fechas y horas
import os                    # Para interactuar con variables de entorno
import logging               # Para registro de eventos y errores
from dotenv import load_dotenv # Para cargar variables desde archivo .env
import pytz                  # Para manejo de zonas horarias
import re                    # Para expresiones regulares en búsquedas

# Configuración del sistema de logging
logging.basicConfig(level=logging.INFO)  # Configurar nivel INFO para los logs

# Cargar variables de entorno desde archivo .env
load_dotenv()

# Obtener y verificar el token de Discord
token = os.getenv('DISCORD_TOKEN')
if not token:
    raise ValueError("No se encontró el token de Discord en las variables de entorno. Asegúrate de tener un archivo .env con DISCORD_TOKEN=tu_token")

# Configuración de los permisos (intents) del bot
intents = discord.Intents.default()
intents.message_content = True  # Habilitar acceso al contenido de mensajes

# Crear instancia del bot con prefijo '!' para los comandos
bot = commands.Bot(command_prefix='!', intents=intents)

###############################################################################
# FUNCIONES AUXILIARES PARA OBTENER DATOS DE CARRERAS
###############################################################################

def obtener_id_circuito(nombre_gp, año):
    """
    Busca y devuelve el ID del circuito según su nombre o el nombre del Gran Premio.
    
    Args:
        nombre_gp (str): Nombre del circuito o Gran Premio a buscar
        año (str): Año de la temporada
        
    Returns:
        str: ID del circuito si se encuentra, None en caso contrario
    """
    # Diccionario de nombres alternativos para circuitos
    # Mapea nombres comunes o variaciones a los IDs estándar de la API
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
    
    # Normalizar el nombre de búsqueda (minúsculas y sin espacios extras)
    nombre_busqueda = nombre_gp.lower().strip()
    
    # Buscar primero en el diccionario de mapeos especiales
    if nombre_busqueda in circuitos_especiales:
        nombre_busqueda = circuitos_especiales[nombre_busqueda]

    try:
        # Consultar la API para obtener los circuitos del año especificado
        url = f'https://api.jolpi.ca/ergast/f1/{año}/circuits'
        respuesta = requests.get(url, timeout=10)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            
            # Verificar que la respuesta tenga la estructura esperada
            if 'MRData' not in datos or 'CircuitTable' not in datos['MRData'] or 'Circuits' not in datos['MRData']['CircuitTable']:
                logging.error(f"Formato de respuesta inesperado para año {año}")
                return None
            
            circuits = datos['MRData']['CircuitTable']['Circuits']
            if not circuits:
                logging.warning(f"No se encontraron circuitos para el año {año}")
                # Intentar con años recientes como alternativa
                return buscar_circuito_en_años_recientes(nombre_busqueda)
                
            # Recorrer todos los circuitos buscando coincidencias
            for circuito in circuits:
                nombre_circuito = circuito['circuitName'].lower()
                circuito_id = circuito['circuitId'].lower()
                
                # Algoritmo de coincidencia flexible para encontrar el circuito
                if (nombre_busqueda in nombre_circuito or 
                    nombre_circuito in nombre_busqueda or 
                    nombre_busqueda in circuito_id or
                    re.search(nombre_busqueda, nombre_circuito) or
                    re.search(nombre_busqueda, circuito_id)):
                    return circuito['circuitId']
                    
        else:
            logging.error(f"Error al obtener circuitos para año {año}: {respuesta.status_code}")
            # En caso de error, intentar con años más recientes
            return buscar_circuito_en_años_recientes(nombre_busqueda)
            
    except Exception as e:
        logging.error(f"Excepción al buscar circuito '{nombre_gp}' en {año}: {e}")
        # En caso de excepción, intentar con años más recientes
        return buscar_circuito_en_años_recientes(nombre_busqueda)
        
    return None

def buscar_circuito_en_años_recientes(nombre_busqueda):
    """
    Intenta encontrar un circuito en años recientes cuando falla la búsqueda en el año especificado.
    Útil para circuitos que cambiaron de nombre o para temporadas antiguas con datos incompletos.
    
    Args:
        nombre_busqueda (str): Nombre normalizado del circuito a buscar
        
    Returns:
        str: ID del circuito si se encuentra, None en caso contrario
    """
    # Lista de años recientes para buscar de forma alternativa
    años_a_probar = ["2023", "2022", "2021", "2020", "2019"]
    
    # Probar cada año hasta encontrar una coincidencia
    for año in años_a_probar:
        try:
            url = f'https://api.jolpi.ca/ergast/f1/{año}/circuits'
            respuesta = requests.get(url, timeout=10)
            if respuesta.status_code == 200:
                datos = respuesta.json()
                circuits = datos['MRData']['CircuitTable']['Circuits']
                
                # Recorrer todos los circuitos del año buscando coincidencias
                for circuito in circuits:
                    nombre_circuito = circuito['circuitName'].lower()
                    circuito_id = circuito['circuitId'].lower()
                    
                    # Comprobar si hay coincidencia
                    if (nombre_busqueda in nombre_circuito or 
                        nombre_circuito in nombre_busqueda or 
                        nombre_busqueda in circuito_id):
                        logging.info(f"Circuito encontrado en año alternativo {año}: {circuito['circuitId']}")
                        return circuito['circuitId']
        except Exception as e:
            logging.error(f"Error buscando en año alternativo {año}: {e}")
            continue
    
    # Si llegamos aquí, no se encontró el circuito en ningún año
    return None

def obtener_resultados(circuito_id, año):
    """
    Obtiene los resultados de una carrera según el ID del circuito y año.
    
    Args:
        circuito_id (str): ID del circuito
        año (str): Año de la temporada
        
    Returns:
        list: Lista de resultados si se encuentra, None en caso contrario
    """
    try:
        # Consultar la API para obtener resultados de la carrera
        url = f'https://api.jolpi.ca/ergast/f1/{año}/circuits/{circuito_id}/results'
        respuesta = requests.get(url, timeout=10)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            # Verificar que la respuesta tenga la estructura esperada
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
    """
    Devuelve el emoji de bandera correspondiente a una nacionalidad.
    
    Args:
        nacionalidad (str): Nombre de la nacionalidad en inglés
        
    Returns:
        str: Emoji de la bandera o cadena vacía si no se encuentra
    """
    # Diccionario que mapea nacionalidades a emojis de banderas
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
    # Retornar la bandera o cadena vacía si no existe
    return banderas.get(nacionalidad, '')

###############################################################################
# COMANDOS DEL BOT
###############################################################################

# Comando para consultar el calendario de una temporada específica
@bot.command(name='calendario')
async def calendario_temporada(ctx, año: str):
    """
    Muestra el calendario completo de una temporada de F1.
    
    Args:
        ctx: Contexto del comando
        año (str): Año de la temporada a consultar
    """
    # Consultar la API para obtener las carreras del año
    url = f'https://api.jolpi.ca/ergast/f1/{año}/races'
    respuesta = requests.get(url)
    if respuesta.status_code == 200:
        datos = respuesta.json()
        carreras = datos['MRData']['RaceTable']['Races']
        if not carreras:
            await ctx.send(f"No se encontró información de carreras para la temporada {año}.")
            return

        # Crear un embed para mostrar la información
        embed = discord.Embed(title=f"Calendario de la temporada {año}", color=discord.Color.blue())
        # Añadir cada carrera como un campo en el embed
        for carrera in carreras:
            nombre_gp = carrera['raceName']
            fecha = carrera['date']
            circuito = carrera['Circuit']['circuitName']
            embed.add_field(name=nombre_gp, value=f"Circuito: {circuito}\nFecha: {fecha}", inline=False)
        
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"Error al obtener el calendario para la temporada {año}.")


# Comando para obtener resultados de un Gran Premio específico
@bot.command(name='resultados')
async def resultados_circuito(ctx, nombre_gp: str, año: str):
    """
    Obtiene y muestra los resultados de un Gran Premio específico.
    
    Args:
        ctx: Contexto del comando
        nombre_gp (str): Nombre del Gran Premio o circuito
        año (str): Año de la carrera
    """
    # Mensaje de espera mientras se busca
    await ctx.send(f"🔍 Buscando resultados para '{nombre_gp}' en {año}...")
    
    # Buscar el circuito por nombre
    circuito_id = obtener_id_circuito(nombre_gp, año)
    if not circuito_id:
        await ctx.send(f"❌ No se encontró el Gran Premio '{nombre_gp}' en el año {año}. Por favor verifica el nombre del circuito o Gran Premio.")
        return

    # Obtener resultados para el circuito
    resultados = obtener_resultados(circuito_id, año)
    if not resultados:
        await ctx.send(f"❌ No se encontraron resultados para el Gran Premio '{nombre_gp}' en el año {año}. Puede que esta carrera no se haya celebrado o haya un error en la API.")
        return

    try:
        # Crear un embed para los primeros 25 resultados (límite de Discord)
        embed = discord.Embed(title=f"Resultados del Gran Premio '{nombre_gp}' en {año}", color=discord.Color.blue())
        
        # Procesar y mostrar resultados (limitados a 25 por embed)
        max_resultados = min(25, len(resultados))
        for i in range(max_resultados):
            resultado = resultados[i]
            posicion = resultado.get('position', 'N/A')
            driver = resultado.get('Driver', {})
            piloto = f"{driver.get('givenName', 'N/A')} {driver.get('familyName', 'N/A')}"
            nacionalidad = driver.get('nationality', 'N/A')
            bandera = obtener_bandera(nacionalidad)
            equipo = resultado.get('Constructor', {}).get('name', 'N/A')
            
            # Manejo de tiempos y estados especiales (DNF, DSQ, etc.)
            if 'Time' in resultado and resultado['Time']:
                tiempo = resultado['Time'].get('time', 'N/A')
            elif 'status' in resultado:
                tiempo = resultado['status']  # Para DNF, DSQ, etc.
            else:
                tiempo = 'N/A'
                
            # Añadir campo con la información del piloto
            embed.add_field(
                name=f"Posición {posicion}",
                value=f"Piloto: {piloto}\nNacionalidad: {bandera} {nacionalidad}\nEquipo: {equipo}\nTiempo: {tiempo}",
                inline=False
            )
        
        await ctx.send(embed=embed)
        
        # Si hay más de 25 resultados, crear y enviar embeds adicionales
        if len(resultados) > 25:
            remaining = len(resultados) - 25
            chunks = (remaining + 24) // 25  # Calcular número de embeds adicionales
            
            for chunk in range(chunks):
                start_idx = 25 + (chunk * 25)
                end_idx = min(start_idx + 25, len(resultados))
                
                # Crear embed adicional
                embed = discord.Embed(
                    title=f"Resultados del Gran Premio '{nombre_gp}' en {año} (continuación {chunk+1})",
                    color=discord.Color.blue()
                )
                
                # Añadir los resultados restantes
                for i in range(start_idx, end_idx):
                    resultado = resultados[i]
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


# Comando para mostrar información sobre la próxima carrera
@bot.command(name='proxima')
async def proxima_carrera(ctx):
    """
    Muestra información sobre la próxima carrera del calendario de F1.
    
    Args:
        ctx: Contexto del comando
    """
    try:
        # Obtener datos de carreras para la temporada actual
        response = requests.get('https://api.jolpi.ca/ergast/f1/2025/races', timeout=10)
        response.raise_for_status()
        data = response.json()
        races = data['MRData']['RaceTable']['Races']
        if not races:
            await ctx.send("❌ No se encontró información de carreras")
            return

        # Calcular qué carreras están por celebrarse
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

        # Seleccionar la carrera más cercana en el tiempo
        next_race = min(upcoming, key=lambda x: x[0])[1]
        race_date = next_race.get('date')
        race_time = next_race.get('time', "00:00:00Z")
        
        # Convertir hora UTC a hora local de España
        race_datetime = datetime.strptime(f"{race_date} {race_time}", "%Y-%m-%d %H:%M:%SZ")
        race_datetime_madrid = race_datetime.replace(tzinfo=pytz.UTC).astimezone(pytz.timezone('Europe/Madrid'))

        # Crear y enviar embed con la información
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
    Obtener información de un piloto de F1 por su nombre o código.
    
    Args:
        ctx: Contexto del comando
        nombre_piloto (str): Nombre o código del piloto a buscar
    """
    # Consultar la API para obtener información del piloto
    url = f'https://api.jolpi.ca/ergast/f1/drivers/{nombre_piloto}'
    respuesta = requests.get(url, timeout=10)
    if respuesta.status_code == 200:
        datos = respuesta.json()
        piloto = datos['MRData']['DriverTable']['Drivers'][0]
        nombre = f"{piloto['givenName']} {piloto['familyName']}"
        fecha_nacimiento = piloto['dateOfBirth']
        nacionalidad = piloto['nationality']

        # Crear y enviar embed con la información
        embed = discord.Embed(title=f"Información de {nombre}", color=discord.Color.gold())
        embed.add_field(name="Nombre", value=nombre, inline=False)
        embed.add_field(name="Fecha de nacimiento", value=fecha_nacimiento, inline=False)
        embed.add_field(name="Nacionalidad", value=nacionalidad, inline=False)

        await ctx.send(embed=embed)
    else:
        await ctx.send(f"No se encontró información para el piloto '{nombre_piloto}'.")

# Comando para mostrar la clasificación del mundial de pilotos
@bot.command(name='mundialpilotos')
async def mundial_pilotos(ctx, año: str = "current"):
    """
    Obtiene y muestra la clasificación del mundial de pilotos para un año específico.
    Si no se especifica año, muestra la temporada actual.
    
    Args:
        ctx: Contexto del comando
        año (str, opcional): Año de la temporada. Por defecto "current" (actual)
    """
    try:
        # Consultar la API para la clasificación de pilotos
        url = f'https://api.jolpi.ca/ergast/f1/{año}/driverStandings'
        respuesta = requests.get(url, timeout=10)
        respuesta.raise_for_status()
        
        # Procesar la respuesta
        datos = respuesta.json()
        clasificacion = datos['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']

        # Calcular cuántos embeds necesitamos (máximo 25 campos por embed)
        pilotos_por_embed = 25
        total_pilotos = len(clasificacion)
        numero_embeds = (total_pilotos + pilotos_por_embed - 1) // pilotos_por_embed

        # Crear y enviar cada embed
        for i in range(numero_embeds):
            inicio = i * pilotos_por_embed
            fin = min((i + 1) * pilotos_por_embed, total_pilotos)
            
            # Título del embed (incluir parte si hay más de uno)
            titulo = f"🏆 Clasificación Mundial de Pilotos {año}"
            if numero_embeds > 1:
                titulo += f" (Parte {i+1}/{numero_embeds})"

            embed = discord.Embed(
                title=titulo,
                color=discord.Color.gold()
            )

            # Añadir un campo por cada piloto en esta parte
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

# Comando para mostrar la clasificación del mundial de constructores
@bot.command(name='constructores')
async def mundial_constructores(ctx, año: str = "current"):
    """
    Obtiene y muestra la clasificación del mundial de constructores para un año específico.
    Si no se especifica año, muestra la temporada actual.
    
    Args:
        ctx: Contexto del comando
        año (str, opcional): Año de la temporada. Por defecto "current" (actual)
    """
    try:
        # Consultar la API para la clasificación de constructores
        url = f'https://api.jolpi.ca/ergast/f1/{año}/constructorStandings'
        respuesta = requests.get(url, timeout=10)
        respuesta.raise_for_status()
        
        # Procesar la respuesta
        datos = respuesta.json()
        clasificacion = datos['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']

        # Crear y enviar embed con la clasificación
        embed = discord.Embed(
            title=f"🏆 Clasificación Mundial de Constructores {año}", 
            color=discord.Color.blue()
        )

        # Añadir un campo por cada constructor
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

# Comando para mandar un gif de Fernando Alonso
@bot.command(name='33')
async def nano(ctx):
    """
    Envía un GIF de Fernando Alonso.
    
    Args:
        ctx: Contexto del comando
    """
    gifs = [
        "https://i.pinimg.com/736x/35/0c/bf/350cbfa78e4806cefeaf23892ac46c65.jpg",
    ]
    gif = random.choice(gifs)
    await ctx.send(gif)

@bot.command(name='smoothoperator')
async def smoothoperator(ctx):
    """
    Envía un GIF de Carlos Sainz.
    
    Args:
        ctx: Contexto del comando
    """
    gif = ["https://media1.tenor.com/m/aFg7WRHu9gAAAAAd/f1-carlos-sainz.gif"]
    gifs = random.choice(gif)
    await ctx.send(gifs)

@bot.command(name='totowolffdescuido')
async def toto(ctx):
    """
    Envía un GIF de Toto Wolff.
    
    Args:
        ctx: Contexto del comando
    """
    gif = ["https://media1.tenor.com/m/xDF917mITKkAAAAd/totowolff-toto.gif"]
    gifs = random.choice(gif)
    await ctx.send(gifs)

@bot.command(name='laqueriatanto')
async def alonsostare(ctx):
    """
    Envía un GIF de Fernando Alonso.
    
    Args:
        ctx: Contexto del comando
    """
    gif = ["https://media1.tenor.com/m/l4hNoe4ig-0AAAAC/alonso-gif.gif"]
    gifs = random.choice(gif)
    await ctx.send(gifs)

@bot.command(name='bwoah')
async def bwoah(ctx):
    """
    Envía un GIF de Kimi Räikkönen.
    
    Args:
        ctx: Contexto del comando
    """
    gif = ["https://media1.tenor.com/m/tudJo6DsrG4AAAAC/kimi-r%C3%A4ikk%C3%B6nen-raikkonen.gif", "https://media1.tenor.com/m/wRg7qgCknqAAAAAC/kimi-raikonnen.gif", ]
    gifs = random.choice(gif)
    await ctx.send(gifs)

#Crea un comando de Ayuda
@bot.command(name='ayuda')
async def ayuda(ctx):
    """
    Muestra la lista de comandos disponibles.
    
    Args:
        ctx: Contexto del comando
    """
    embed = discord.Embed(
        title="📚 Lista de comandos",
        color=discord.Color.blue()
    )
    embed.add_field(name="!calendario [año]", value="Muestra el calendario de una temporada", inline=False)
    embed.add_field(name="!resultados [nombre_gp] [año]", value="Muestra los resultados de un Gran Premio", inline=False)
    embed.add_field(name="!proxima", value="Muestra información sobre la próxima carrera", inline=False)
    embed.add_field(name="!piloto [nombre_piloto]", value="Muestra información de un piloto", inline=False)
    embed.add_field(name="!mundialpilotos [año]", value="Muestra la clasificación del mundial de pilotos", inline=False)
    embed.add_field(name="!constructores [año]", value="Muestra la clasificación del mundial de constructores", inline=False)
    embed.add_field(name="!33", value="Envía un GIF de Fernando Alonso", inline=False)
    embed.add_field(name="!smoothoperator", value="Envía un GIF de Carlos Sainz", inline=False)
    embed.add_field(name="!totowolffdescuido", value="Envía un GIF de Toto Wolff", inline=False)
    embed.add_field(name="!laqueriatanto", value="Envía un GIF de Fernando Alonso", inline=False)
    embed.add_field(name="!bwoah", value="Envía un GIF de Kimi Räikkönen", inline=False)
    await ctx.send(embed=embed)

# Evento de terminal cuando el bot esté listo
@bot.event
async def on_ready():
    """
    Evento que se ejecuta cuando el bot está listo y conectado.
    """
    logging.info(f'Bot conectado como {bot.user}')

# Iniciar el bot
if __name__ == "__main__":
    try:
        bot.run(token)
    except discord.errors.LoginFailure:
        logging.error("Error: Token inválido. Por favor verifica el token en el archivo .env")
    except Exception as e:
        logging.error(f"Error inesperado: {e}")
