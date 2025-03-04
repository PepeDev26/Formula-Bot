# Formula Bot

Este bot de Discord proporciona información sobre la Fórmula 1, incluidos resultados de carreras, clasificaciones, calendarios y más.

## Comandos disponibles

- `!calendario [año]`: Muestra el calendario de la temporada especificada.
- `!resultados [nombre_gp] [año]`: Muestra los resultados de un Gran Premio específico.
  - Ejemplo: `!resultados monza 2023` o `!resultados italia 2005`
- `!proxima`: Muestra información sobre la próxima carrera programada.
- `!piloto [nombre]`: Muestra información sobre un piloto.
- `!mundialpilotos [año]`: Muestra la clasificación del mundial de pilotos.
- `!constructores [año]`: Muestra la clasificación del mundial de constructores.
- `!sainz`: Muestra un GIF aleatorio de Carlos Sainz.

## Notas sobre la búsqueda de carreras

Para los circuitos, puedes buscarlos por:
- Nombre del GP (ej. "Spanish")
- Nombre del país (ej. "Spain")
- Nombre del circuito (ej. "Catalunya")

Para años antiguos (especialmente antes de 2012), la búsqueda puede ser menos precisa debido a limitaciones de la API, pero el bot intentará encontrar la información buscando coincidencias alternativas.

## Configuración

El bot requiere un archivo `.env` con la variable `DISCORD_TOKEN` configurada con un token válido de Discord.
