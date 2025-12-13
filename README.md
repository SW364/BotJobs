# BotJobs

Bot para recopilar vacantes públicas desde Greenhouse y Lever, filtrar posiciones junior o de práctica en Monterrey/Remoto MX y enviar un resumen por Telegram.

## Requisitos
- Python 3.10+
- Token del bot de Telegram y chat ID

## Instalación
1. Crea un entorno virtual:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # En Windows: .venv\\Scripts\\activate
   ```
2. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Copia las variables de entorno y añade tus valores:
   ```bash
   cp .env.example .env
   # Edita .env para agregar TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID
   ```

## Configuración
Edita `config.yaml` para definir las fuentes y filtros:
- `greenhouse_tokens`: lista de tokens de board de Greenhouse.
- `lever_companies`: slugs de compañías en Lever.
- `external_sources`: conectores HTTP hacia APIs/RSS de terceros (por ejemplo RapidAPI o webhooks que entreguen vacantes de Indeed,
  Computrabajo o LinkedIn). Permite definir endpoint, headers, params y llaves para mapear campos.
- `filters`: ubicaciones aceptadas, niveles junior/intern, títulos permitidos, palabras de exclusión, años mínimos a descartar y límite de resultados a enviar.

Ejemplo incluido:
```yaml
greenhouse_tokens:
  - ejemploempresa
lever_companies:
  - ejemplocompania
external_sources:
  - name: "Indeed via RapidAPI"
    endpoint: "https://ejemplo-indeed.p.rapidapi.com/jobs"
    headers:
      X-RapidAPI-Key: "TU_API_KEY"
      X-RapidAPI-Host: "ejemplo-indeed.p.rapidapi.com"
    params:
      location: "Monterrey"
    data_key: "data"
    title_key: "title"
    company_key: "company"
    location_key: "location"
    url_key: "url"
    description_key: "description"
filters:
  ubicaciones:
    - Monterrey
    - "Área Metropolitana"
    - "Nuevo León"
    - "Remoto México"
  niveles:
    - Intern
    - Practicante
    - Becario
    - Trainee
    - Junior
    - Entry
  titulos_permitidos:
    - Software Engineer
    - Full Stack
    - Backend
    - Frontend
    - Android
    - QA Automation
    - Data Analyst
  exclusiones:
    - Senior
    - Lead
    - Staff
    - Principal
    - Manager
 exclusion_por_anos: 3
  limite_envio: 25
```

### Pasos para conectar Indeed/Computrabajo/LinkedIn vía terceros
1. Crea o contrata un conector que exponga las vacantes en formato JSON (por ejemplo, proveedores en RapidAPI que ya integran
   Indeed/Computrabajo/LinkedIn o un pequeño webhook propio que consuma sus APIs oficiales/feeds).
2. Obtén el endpoint público del conector y las cabeceras necesarias (p. ej. `X-RapidAPI-Key`).
3. Añade una entrada en `external_sources` con el `endpoint`, `headers`, `params` y, si el JSON viene anidado, `data_key` con la
   clave que contiene la lista. Usa los `*_key` para mapear los nombres de campo a `title`, `company`, `location`, `url` y
   `description` según el formato que entregue tu proveedor.
4. Ejecuta `python main.py` y el bot agregará esas vacantes junto con las de Greenhouse y Lever, aplicando los mismos filtros,
   validación de links y deduplicación.

## Uso
Ejecuta el bot tras configurar `.env` y `config.yaml`:
```bash
python main.py
```

 El script:
 1. Carga la configuración y variables de entorno.
 2. Obtiene vacantes de Greenhouse, Lever y cualquier conector definido en `external_sources`.
 3. Aplica filtros de ubicación, nivel y años de experiencia, valida que el link funcione, y evita duplicados usando `seen_jobs.json`.
 4. Envía por Telegram un resumen con título, empresa, ubicación, link y un mensaje personalizado (<=300 caracteres). Si el mensaje es largo, se divide en fragmentos de ~3500 caracteres.
