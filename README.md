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
- `filters`: ubicaciones aceptadas, niveles junior/intern, títulos permitidos, palabras de exclusión, años mínimos a descartar y límite de resultados a enviar.

Ejemplo incluido:
```yaml
greenhouse_tokens:
  - ejemploempresa
lever_companies:
  - ejemplocompania
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

## Uso
Ejecuta el bot tras configurar `.env` y `config.yaml`:
```bash
python main.py
```

El script:
1. Carga la configuración y variables de entorno.
2. Obtiene vacantes de Greenhouse y Lever.
3. Aplica filtros de ubicación, nivel y años de experiencia, valida que el link funcione, y evita duplicados usando `seen_jobs.json`.
4. Envía por Telegram un resumen con título, empresa, ubicación, link y un mensaje personalizado (<=300 caracteres). Si el mensaje es largo, se divide en fragmentos de ~3500 caracteres.
