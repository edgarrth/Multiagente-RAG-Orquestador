# Variables de entorno (.env)

Este archivo describe las variables que el proyecto espera en el archivo `.env` o en el entorno.
Incluye si son obligatorias, su tipo, valor por defecto (si aplica) y un ejemplo.

Formato de ejemplo en `.env`:

```
OPENAI_API_KEY=sk-xxxx
PINECONE_API_KEY=xxxx
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=marketing-knowledge
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=xxxx
DATABASE_URL=postgresql://user:pass@host:5432/dbname
# Opcionales
CALENDLY_API_KEY=
CALENDLY_USER_URI=
CALENDLY_EVENT_TYPE=
```

---

## Variables

- OPENAI_API_KEY
  - Obligatoria: Sí
  - Tipo: string
  - Descripción: API Key para usar los endpoints de OpenAI (embeddings y chat).
  - Ejemplo: `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

- OPENAI_MODEL
  - Obligatoria: No (tiene valor por defecto en `settings.py`)
  - Tipo: string
  - Valor por defecto: `gpt-4o-mini`
  - Descripción: Nombre del modelo de OpenAI a usar para chat/completions.
  - Ejemplo: `gpt-4o-mini`

- OPENAI_TEMPERATURE
  - Obligatoria: No
  - Tipo: float
  - Valor por defecto: `0.7`
  - Descripción: Control de aleatoriedad en las respuestas del modelo.
  - Ejemplo: `0.3`

- OPENAI_MAX_TOKENS
  - Obligatoria: No
  - Tipo: integer
  - Valor por defecto: `4000`
  - Descripción: Número máximo de tokens para las respuestas del modelo.
  - Ejemplo: `1000`

- PINECONE_API_KEY
  - Obligatoria: Sí (si quieres usar indexación/búsqueda)
  - Tipo: string
  - Descripción: API Key de Pinecone para administrar índices y consultas.
  - Ejemplo: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

- PINECONE_ENVIRONMENT
  - Obligatoria: No
  - Tipo: string
  - Valor por defecto: `us-east-1` (según `settings.py`)
  - Descripción: Región/entorno de Pinecone.
  - Ejemplo: `us-east-1`

- PINECONE_INDEX_NAME
  - Obligatoria: No
  - Tipo: string
  - Valor por defecto: `marketing-knowledge`
  - Descripción: Nombre del índice de vectores en Pinecone.
  - Ejemplo: `marketing-knowledge`

- PINECONE_DIMENSION
  - Obligatoria: No
  - Tipo: integer
  - Valor por defecto: `1536`
  - Descripción: Dimensión del embedding esperado (coincidente con el modelo de embeddings).
  - Ejemplo: `1536`

- PINECONE_METRIC
  - Obligatoria: No
  - Tipo: string
  - Valor por defecto: `cosine`
  - Descripción: Métrica de similitud usada en el índice (e.g., `cosine`, `dotproduct`).
  - Ejemplo: `cosine`

- SUPABASE_URL
  - Obligatoria: Sí
  - Tipo: string (URL)
  - Descripción: URL del proyecto Supabase (para tablas de memorias, sesiones y logs).
  - Ejemplo: `https://abcd1234.supabase.co`

- SUPABASE_KEY
  - Obligatoria: Sí
  - Tipo: string
  - Descripción: Key (anon o service role según necesidades) para conectar con Supabase.
  - Ejemplo: `eyJhbGciOiJIUzI1NiIsInR5cCI6...`

- DATABASE_URL
  - Obligatoria: Sí
  - Tipo: string (DSN)
  - Descripción: URL/DSN de la base de datos Postgres utilizada por Supabase u otra DB.
  - Ejemplo: `postgresql://user:password@host:5432/database`

- CALENDLY_API_KEY
  - Obligatoria: No
  - Tipo: string
  - Descripción: API Key de Calendly (si se integra funcionalidad de agendamiento).
  - Ejemplo: `Bearer xxxxxxxx`

- CALENDLY_USER_URI
  - Obligatoria: No
  - Tipo: string
  - Descripción: URI del usuario en Calendly (opcional, para operaciones específicas).
  - Ejemplo: `https://api.calendly.com/users/ABCD`

- CALENDLY_EVENT_TYPE
  - Obligatoria: No
  - Tipo: string
  - Descripción: Tipo de evento predeterminado en Calendly (opcional).
  - Ejemplo: `https://api.calendly.com/event_types/EFGH`

- ENVIRONMENT
  - Obligatoria: No
  - Tipo: string
  - Valor por defecto: `development`
  - Descripción: Entorno de ejecución (development, staging, production).
  - Ejemplo: `production`

- LOG_LEVEL
  - Obligatoria: No
  - Tipo: string
  - Valor por defecto: `INFO`
  - Descripción: Nivel de logging deseado (`DEBUG`, `INFO`, `WARNING`, `ERROR`).
  - Ejemplo: `DEBUG`

- CHUNK_SIZE
  - Obligatoria: No
  - Tipo: integer
  - Valor por defecto: `1000`
  - Descripción: Tamaño en caracteres para dividir el texto en chunks durante la ingestión.
  - Ejemplo: `1000`

- CHUNK_OVERLAP
  - Obligatoria: No
  - Tipo: integer
  - Valor por defecto: `200`
  - Descripción: Solapamiento (overlap) entre chunks en caracteres.
  - Ejemplo: `200`

- MAX_RETRIEVAL_DOCUMENTS
  - Obligatoria: No
  - Tipo: integer
  - Valor por defecto: `5`
  - Descripción: Número máximo de documentos a recuperar para construir el contexto.
  - Ejemplo: `5`

---

Notas
- Guarda este archivo como referencia y crea un `.env` en la raíz con las variables necesarias antes de ejecutar los scripts.
- Algunas variables están configuradas con valores por defecto en `src/config/settings.py`; si no las incluyes en `.env` se usarán esos valores.
- Protege tus claves: no subas el `.env` a repositorios públicos.

______________
# .env.example — Copia este archivo a .env y rellena las claves secretas
# No subas tu archivo .env al repositorio.

# ----------------------------
# OpenAI
# ----------------------------
OPENAI_API_KEY=
# Opcional: modelo por defecto (se usa el valor de settings si no se especifica)
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=4000

# ----------------------------
# Pinecone (vector DB)
# ----------------------------
PINECONE_API_KEY=
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=marketing-knowledge
PINECONE_DIMENSION=1536
PINECONE_METRIC=cosine

# ----------------------------
# Supabase / Database
# ----------------------------
SUPABASE_URL=
SUPABASE_KEY=
DATABASE_URL=

# ----------------------------
# Calendly (opcional)
# ----------------------------
CALENDLY_API_KEY=
CALENDLY_USER_URI=
CALENDLY_EVENT_TYPE=

# ----------------------------
# General / App settings
# ----------------------------
ENVIRONMENT=development
LOG_LEVEL=INFO

# ----------------------------
# RAG settings
# ----------------------------
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_RETRIEVAL_DOCUMENTS=5
