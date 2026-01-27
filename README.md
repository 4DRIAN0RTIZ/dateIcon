# Date Icon API

API REST para generar iconos de fecha personalizables con diferentes temas, idiomas y tamaños.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)

## Endpoints

| Endpoint | Descripcion |
|----------|-------------|
| `GET /` | Informacion de la API |
| `GET /icon/{date}` | Genera icono de fecha (formato: `DD_MM`) |
| `GET /themes` | Lista de temas disponibles |
| `GET /languages` | Lista de idiomas disponibles |
| `GET /sizes` | Tamanios permitidos |

## Uso

```
GET /icon/25_12?theme=default&lang=es&size=128
```

### Parametros

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| `date` | path | - | Fecha en formato `DD_MM` |
| `theme` | query | `default` | Tema de colores |
| `lang` | query | `es` | Idioma para el mes |
| `size` | query | `64` | Tamanio en pixeles |
| `bar_color` | query | - | Color de barra (hex, solo con tema `custom`) |
| `bg_color` | query | - | Color de fondo (hex, solo con tema `custom`) |
| `text_color` | query | - | Color de texto (hex, solo con tema `custom`) |

### Temas

- `default` - Naranja y crema
- `dark` - Modo oscuro
- `ocean` - Azul oceano
- `forest` - Verde bosque
- `sunset` - Rojo atardecer
- `custom` - Colores personalizados

### Idiomas

- `es` - Espanol
- `en` - Ingles
- `fr` - Frances
- `de` - Aleman
- `pt` - Portugues

### Tamanios

16, 24, 32, 48, 64, 128, 256, 512, 1024 px

## Instalacion

```bash
# Clonar repositorio
git clone <repo-url>
cd dateIcon

# Crear entorno virtual
python -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Copiar configuracion
cp .env.example .env

# Ejecutar
python app.py
```

## Configuracion

Variables de entorno (ver `.env.example`):

| Variable | Default | Descripcion |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Host del servidor |
| `PORT` | `8000` | Puerto del servidor |
| `WORKERS` | `4` | Numero de workers |
| `RATE_LIMIT_PER_MINUTE` | `60` | Limite de peticiones por minuto |
| `ALLOWED_ORIGINS` | `*` | Origenes CORS permitidos |
| `LOG_LEVEL` | `INFO` | Nivel de logging |
| `PRODUCTION` | `false` | Modo produccion |

## LICENCIA

[GNU GPLv3](LICENSE)
