# AgentesAvanzado — Sistema multiagente de marketing (RAG)

Este repositorio implementa un sistema multiagente sencillo orientado a tareas de marketing,
que integra un subsistema RAG (Retrieval-Augmented Generation) para responder preguntas
basadas en documentos indexados. Está pensado como prototipo / base para aplicaciones
de asistencia en marketing, análisis de documentos y gestión de memorias.

Checklist rápido
- [ ] Revisar/establecer variables de entorno en `.env` (OpenAI, Pinecone, Supabase, DB)
- [ ] Inicializar infra (Pinecone, Supabase) usando los scripts en `scripts/`
- [ ] Indexar PDFs de `data/pdfs/` con `scripts/index_pdfs.py`
- [ ] Ejecutar la UI con Streamlit (`src/ui/app.py`) para probar el flujo

Arquitectura y flujo general
- RAGSystem (`src/rag/rag_system.py`): manejo de ingestión (PDF → chunks), generación de embeddings
  (OpenAI), indexación y búsqueda en Pinecone, y generación de respuestas combinando documentos.
- Agent wrapper (`src/agents/agent.py`): cliente ligero para llamadas a OpenAI Chat, mantiene historial
  y prepara el contexto para prompts.
- Core / Orquestador (`src/core/system.py`): instancia varios agentes especializados y decide
  el routing de consultas (heurístico por keywords). Integra RAG y la base de datos.
- Database (`src/database/database.py`): persistencia en Supabase para memorias, sesiones y logs.

Agentes que participan
- Orchestrator (prompt en `src/core/system.py`): decide a qué agente enviar la consulta y
  coordina el uso de contexto. Responde consultas generales si no se requiere otro agente.
- RAG_Agent: especializado en consultas sobre documentos; recibe documentos recuperados
  por el `RAGSystem` y genera respuestas basadas en ellos.
- Marketing_Agent: genera plantillas de email, estrategias, propuestas y recomendaciones
  de marketing. Recibe documentos y memorias como contexto.
- Knowledge_Agent: gestiona la memoria a largo plazo; puede sugerir guardar insights
  y ejecutar operaciones de persistencia en la base de datos.

Detalles del subsistema RAG
- Ingesta: `RAGSystem.load_pdf(pdf_path)` usa `pypdf` para extraer texto y lo divide en chunks
  con tamaño y overlap definidos en `src/config/settings.py` (`chunk_size`, `chunk_overlap`).
- Embeddings: `RAGSystem.generate_embedding(text)` llama a OpenAI para obtener vectores.
- Indexación: `index_documents` sube batches a Pinecone y guarda metadata mínima por chunk.
- Recuperación: `search(query, top_k)` genera embedding de la query y consulta Pinecone.
- Generación: `answer_question` arma un prompt que incluye los documentos recuperados y
  llama al modelo de chat para sintetizar la respuesta.

Tecnologías y dependencias principales
- Python 3.12
- OpenAI (cliente oficial usado para embeddings y chat)
- Pinecone (vector DB para indexación y búsqueda)
- Supabase (persistencia Postgres para memorias, sesiones y logs)
- pypdf (extracción de texto desde PDFs)
- streamlit (UI ligera en `src/ui/app.py`)

Variables de entorno / configuración
Coloca un archivo `.env` en la raíz o exporta variables en tu entorno con las claves:

- OPENAI_API_KEY
- PINECONE_API_KEY
- PINECONE_ENVIRONMENT (o región)
- PINECONE_INDEX_NAME (opcional)
- SUPABASE_URL
- SUPABASE_KEY
- DATABASE_URL (Postgres)

Comandos útiles (ejemplos)
Primero activa tu entorno virtual (ejemplo con conda):

```bash
conda activate agente
```

Inicializar Pinecone y Supabase (scripts incluidos):

```bash
conda run -n agente python scripts/init_pinecone.py
conda run -n agente python scripts/init_supabase.py
```

Indexar PDFs (ej. carpeta `data/pdfs/`):

```bash
conda run -n agente python scripts/index_pdfs.py
```

Ejecutar la UI (Streamlit):

```bash
streamlit run src/ui/app.py
```
