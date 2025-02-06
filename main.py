import discord
from discord.ext import commands
import requests
import random
from datetime import datetime
import os
from dotenv import load_dotenv

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
    print(f'Bot conectado como {bot.user}')

@bot.command(name='resultados')
async def resultados(ctx, carrera: str):
    # Implementar la lógica para obtener los resultados de la carrera específica
    # Por ejemplo, podemos simular la obtención de los resultados
    resultados_carrera = obtener_resultados_carrera(carrera, "1")  # Assuming "1" as a default value for numero_carrera
    await ctx.send(resultados_carrera)

@bot.command(name='carrera')
async def carrera(ctx, nombre_carrera: str, temporada: str):
    """Muestra los resultados de una carrera específica por nombre y temporada"""
    resultados = obtener_resultados_carrera_por_nombre(nombre_carrera, temporada)
    if resultados:
        await ctx.send(f"Resultados del {nombre_carrera} de la temporada {temporada}:\n{resultados}")
    else:
        await ctx.send(f"No se encontraron resultados para el {nombre_carrera} de la temporada {temporada}.")

def obtener_resultados_carrera_por_nombre(nombre_carrera, temporada):
    # Conectar con la API de Ergast para obtener los resultados de la carrera por nombre y temporada
    url = f"http://ergast.com/api/f1/{temporada}/circuits/{nombre_carrera}/results.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        resultados = []
        for result in data['MRData']['RaceTable']['Races'][0]['Results']:
            piloto = result['Driver']['familyName']
            posicion = result['position']
            resultados.append(f"{posicion}. {piloto}")
        return "\n".join(resultados)
    else:
        return None

@bot.command(name='clasificacion')
async def clasificacion(ctx):
    try:
        response = requests.get('http://ergast.com/api/f1/current/driverStandings.json')
        data = response.json()
        standings = data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
        
        mensaje = "🏎️ **Clasificación actual de pilotos:**\n\n"
        for driver in standings[:10]:  # Top 10
            mensaje += f"{driver['position']}. {driver['Driver']['givenName']} {driver['Driver']['familyName']} - {driver['points']} pts\n"
        
        await ctx.send(mensaje)
    except Exception as e:
        await ctx.send("❌ Error al obtener la clasificación")

@bot.command(name='proxima')
async def proxima_carrera(ctx):
    try:
        response = requests.get('http://ergast.com/api/f1/current/next.json')
        data = response.json()
        race = data['MRData']['RaceTable']['Races'][0]
        
        fecha = datetime.strptime(f"{race['date']} {race['time']}", "%Y-%m-%d %H:%M:%SZ")
        fecha_esp = fecha.replace(tzinfo=pytz.UTC).astimezone(pytz.timezone('Europe/Madrid'))
        
        mensaje = f"📅 **Próxima carrera:**\n\n"
        mensaje += f"GP de {race['raceName']}\n"
        mensaje += f"Circuito: {race['Circuit']['circuitName']}\n"
        mensaje += f"Fecha: {fecha_esp.strftime('%d/%m/%Y %H:%M')} (hora española)\n"
        
        await ctx.send(mensaje)
    except Exception as e:
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
        response = requests.get(f'http://ergast.com/api/f1/circuits/{nombre}.json')
        data = response.json()
        circuit = data['MRData']['CircuitTable']['Circuits'][0]
        
        mensaje = f"🏁 **Información del circuito:**\n\n"
        mensaje += f"Nombre: {circuit['circuitName']}\n"
        mensaje += f"Localización: {circuit['Location']['locality']}, {circuit['Location']['country']}\n"
        mensaje += f"Coordenadas: {circuit['Location']['lat']}, {circuit['Location']['long']}\n"
        
        await ctx.send(mensaje)
    except Exception as e:
        await ctx.send("❌ Error al obtener información del circuito")

@bot.command(name='ayuda')
async def help_command(ctx):
    """Muestra todos los comandos disponibles"""
    embed = discord.Embed(
        title="📖 Comandos Disponibles",
        description="Lista de todos los comandos que puedes usar",
        color=discord.Color.blue()
    )
    
    # Añadir los comandos al embed
    embed.add_field(
        name="!ayuda", 
        value="Muestra este mensaje de ayuda", 
        inline=False
    )
    embed.add_field(
        name="!meme [piloto]", 
        value="Muestra un meme aleatorio (o de un piloto específico)", 
        inline=False
    )
    embed.add_field(
        name="!carrera [temporada] [numero_carrera]", 
        value="Muestra los resultados de una carrera específica por temporada y número de carrera", 
        inline=False
    )
    # Puedes añadir más comandos aquí según vayas implementándolos
    
    embed.set_footer(text="Usa ! antes de cada comando")
    
    await ctx.send(embed=embed)

@bot.command(name='ayuda_bot')
async def ayuda_bot(ctx):
    # Implementar la lógica para el comando de ayuda
    embed = discord.Embed(title="Comandos del Bot", description="Lista de comandos disponibles:")
    embed.add_field(name="!resultados <carrera>", value="Obtiene los resultados de una carrera específica.", inline=False)
    # Puedes añadir más comandos aquí según vayas implementándolos
    embed.set_footer(text="Usa ! antes de cada comando")
    await ctx.send(embed=embed)

def main():
    try:
        bot.run(token)
    except discord.errors.LoginFailure:
        print("Error: Token inválido. Por favor verifica el token en el archivo .env")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    main()