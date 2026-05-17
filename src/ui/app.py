"""
Interfaz de usuario profesional con Streamlit.
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.system import MarketingMultiAgentSystem
from src.config.settings import settings
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================

st.set_page_config(
    page_title="Sistema Multiagente de Marketing",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================
# ESTILOS CSS PROFESIONALES
# ============================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
        font-size: 1.1rem;
    }
    
    .agent-badge {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        border-radius: 0.5rem;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 0.2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .agent-orchestrator { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; 
    }
    .agent-rag { 
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white; 
    }
    .agent-marketing { 
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white; 
    }
    .agent-knowledge { 
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        color: white; 
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# INICIALIZACIÓN DE ESTADO
# ============================================

def init_session_state():
    """Inicializa el estado de la sesión de Streamlit."""
    if "system" not in st.session_state:
        st.session_state.system = None
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "pdfs_indexed" not in st.session_state:
        st.session_state.pdfs_indexed = 0


init_session_state()


# ============================================
# SIDEBAR - PANEL DE CONTROL
# ============================================

with st.sidebar:
    st.markdown("##  Panel de Control")
    
    # Estado del sistema
    st.markdown("###  Estado del Sistema")
    
    if st.session_state.system:
        st.success("Sistema Activo")
        session_short = st.session_state.system.session_id[:8]
        st.code(f"Sesión: {session_short}...", language=None)
        
        # Opciones de sesión
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(" Resumen", use_container_width=True):
                with st.spinner("Generando resumen..."):
                    summary = st.session_state.system.get_session_summary()
                    st.json(summary)
        
        with col2:
            if st.button(" Limpiar", use_container_width=True):
                st.session_state.messages = []
                st.session_state.system.clear_agent_history()
                st.success("Historial limpiado")
                st.rerun()
    else:
        st.warning(" Sistema Inactivo")
        
        if st.button(" Iniciar Sistema", type="primary", use_container_width=True):
            with st.spinner("Inicializando sistema..."):
                st.session_state.system = MarketingMultiAgentSystem()
                st.success("Sistema iniciado correctamente")
                st.rerun()
    
    st.markdown("---")
    
    # Gestión de documentos
    st.markdown("###  Gestión de Documentos")
    
    uploaded_files = st.file_uploader(
        "Cargar documentos PDF",
        type=["pdf"],
        accept_multiple_files=True,
        help="Sube documentos de marketing para indexación"
    )
    
    if uploaded_files and st.session_state.system:
        if st.button(" Indexar Documentos", use_container_width=True):
            with st.spinner(f"Indexando {len(uploaded_files)} documento(s)..."):
                temp_paths = []
                
                # Guardar archivos temporalmente
                for uploaded_file in uploaded_files:
                    temp_path = f"./data/pdfs/{uploaded_file.name}"
                    Path(temp_path).parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    temp_paths.append(temp_path)
                
                # Indexar documentos
                result = st.session_state.system.load_multiple_pdfs(temp_paths)
                
                if result["success"]:
                    st.success(
                        f"{result['successful']}/{result['total_pdfs']} "
                        f"documentos indexados ({result['total_chunks']} fragmentos)"
                    )
                    st.session_state.pdfs_indexed += result['successful']
                else:
                    st.error(" Error al indexar documentos")
                
                # Mostrar detalles
                with st.expander("Ver detalles"):
                    for i, detail in enumerate(result['details'], 1):
                        status = "" if detail['success'] else ""
                        st.write(f"{status} Documento {i}: {detail['message']}")
    
    st.markdown("---")
    
    # Métricas del sistema
    st.markdown("###  Métricas")
    
    if st.session_state.system:
        st.metric("Documentos Indexados", st.session_state.pdfs_indexed)
        st.metric("Mensajes en Sesión", len(st.session_state.messages))
    
    st.markdown("---")
    
    # Información del sistema
    with st.expander("ℹ Información del Sistema"):
        st.markdown(f"""
        **Configuración:**
        - Modelo: `{settings.openai_model}`
        - Temperatura: `{settings.openai_temperature}`
        - Índice Pinecone: `{settings.pinecone_index_name}`
        
        **Agentes Disponibles:**
        -  Orchestrator (Coordinador)
        -  RAG Agent (Análisis de Documentos)
        -  Marketing Agent (Acciones Comerciales)
        -  Knowledge Agent (Gestión de Memoria)
        """)


# ============================================
# CONTENIDO PRINCIPAL
# ============================================

st.markdown('<h1 class="main-header"> Sistema Multiagente de Marketing</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Plataforma inteligente para gestión integral de marketing</p>', unsafe_allow_html=True)

# Métricas principales
if st.session_state.system:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(" Agentes", "4", help="Agentes especializados activos")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(" Documentos", st.session_state.pdfs_indexed, help="PDFs indexados")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(" Mensajes", len(st.session_state.messages), help="Interacciones en esta sesión")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(" Estado", "Activo", help="Sistema operativo")
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ============================================
# INTERFAZ DE CHAT
# ============================================

if not st.session_state.system:
    # Pantalla de bienvenida
    st.info(" Inicia el sistema desde el panel lateral para comenzar")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ###  Capacidades del Sistema
        
        **Agentes Especializados:**
        -  **Orchestrator**: Coordina y optimiza el routing de consultas
        -  **RAG Agent**: Analiza documentos con búsqueda semántica avanzada
        -  **Marketing Agent**: Genera estrategias y plantillas personalizadas
        -  **Knowledge Agent**: Gestiona memoria y aprendizaje continuo
        
        **Características:**
        - Procesamiento de documentos PDF
        - Búsqueda semántica con Pinecone
        - Memoria de largo plazo con Supabase
        - Generación de contenido personalizado
        """)
    
    with col2:
        st.markdown("""
        ###  Ejemplos de Consultas
        
        **Análisis de Documentos:**
```
        ¿Qué leads tenemos con mayor puntuación?
```
        
        **Marketing y Estrategia:**
```
        Genera una plantilla de email para seguimiento
        de Juan Pérez interesado en el producto X
```
        
        **Gestión de Conocimiento:**
```
        Guarda este insight: Los clientes del sector
        tecnológico prefieren demos virtuales
```
        
        **Planificación:**
```
        Propón una estrategia para re-engagement
        de leads fríos del Q3
```
        """)

else:
    # Interfaz de chat activa
    
    # Mostrar historial de mensajes
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Mostrar badge del agente si es respuesta del asistente
            if message["role"] == "assistant" and "agent" in message:
                agent_name = message["agent"].lower().replace("_", "-")
                agent_display = message["agent"].replace("_", " ")
                st.markdown(
                    f'<span class="agent-badge agent-{agent_name}">🤖 {agent_display}</span>',
                    unsafe_allow_html=True
                )
    
    # Input del usuario
    if prompt := st.chat_input("Escribe tu consulta aquí..."):
        # Agregar mensaje del usuario
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Mostrar mensaje del usuario
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Procesar con el sistema
        with st.chat_message("assistant"):
            with st.spinner(" Procesando..."):
                try:
                    # Procesar query
                    result = st.session_state.system.process_query(prompt)
                    
                    response = result["response"]
                    agent_used = result["agent_used"]
                    
                    # Mostrar respuesta
                    st.markdown(response)
                    
                    # Mostrar badge del agente
                    agent_name = agent_used.lower().replace("_", "-")
                    agent_display = agent_used.replace("_", " ")
                    st.markdown(
                        f'<span class="agent-badge agent-{agent_name}">🤖 {agent_display}</span>',
                        unsafe_allow_html=True
                    )
                    
                    # Guardar en historial
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "agent": agent_used
                    })
                    
                except Exception as e:
                    error_msg = f" Error al procesar la solicitud: {str(e)}"
                    st.error(error_msg)
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "agent": "system_error"
                    })


# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p style='font-size: 1.1rem; font-weight: 600;'>Sistema Multiagente de Marketing Profesional</p>
    <p>Powered by Axiz IS</p>
    <p style='font-size: 0.9rem;'>Versión 1.1.0 | Agentes LangChain</p>
</div>
""", unsafe_allow_html=True)