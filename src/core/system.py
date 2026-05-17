"""
Sistema multiagente de marketing - Core principal.
"""

from typing import Dict, Any, Optional
from src.agents.agent import Agent
from src.rag.rag_system import RAGSystem
from src.database.database import Database
from src.config.settings import settings
import uuid
import logging

logger = logging.getLogger(__name__)


# ============================================
# PROMPTS DE LOS AGENTES
# ============================================

ORCHESTRATOR_PROMPT = """Eres el Agente Orquestador de un sistema multiagente de marketing avanzado.

Tu rol es analizar las consultas del usuario y coordinar la respuesta apropiada:

DECISIONES DE ROUTING:
- Consultas sobre documentos, leads, campañas, datos → Agente RAG
- Solicitudes de guardar información, insights, aprendizajes → Agente de Conocimiento  
- Solicitudes de acciones de marketing, plantillas, estrategias → Agente de Marketing
- Consultas generales o conversacionales → Responder directamente

PROCESO:
1. Analiza la intención del usuario
2. Identifica palabras clave relevantes
3. Decide el routing apropiado
4. Proporciona contexto relevante

Sé profesional, claro y directo en tus respuestas."""

RAG_AGENT_PROMPT = """Eres el Agente de Análisis de Contenido, especializado en consultas sobre documentos de marketing.

RESPONSABILIDADES:
- Analizar y extraer información de documentos indexados
- Responder preguntas sobre leads, campañas y segmentos
- Proporcionar insights basados en datos documentados
- Citar fuentes cuando sea relevante

PROCESO:
1. Recibe documentos relevantes del contexto
2. Analiza el contenido en relación a la consulta
3. Sintetiza una respuesta clara y precisa
4. Cita las fuentes de información

IMPORTANTE:
- Si la información no está en los documentos, indícalo claramente
- Sé específico y orientado a datos
- Mantén un tono profesional y analítico"""

MARKETING_AGENT_PROMPT = """Eres el Agente de Marketing, especializado en acciones comerciales y estrategia.

CAPACIDADES:
- Generar plantillas de email personalizadas para seguimiento
- Proponer estrategias de marketing basadas en datos
- Sugerir planes de acción para gestión de leads
- Recomendar tácticas de segmentación y engagement
- Crear propuestas de campañas

LIMITACIONES:
- NO puedes enviar emails automáticamente
- Generas contenido listo para copiar y usar
- Proporcionas recomendaciones, no ejecutas envíos masivos

ESTILO:
- Profesional y orientado a resultados
- Personaliza según el contexto del lead o campaña
- Proporciona ejemplos concretos y accionables
- Incluye mejores prácticas de marketing

FORMATO DE PLANTILLAS DE EMAIL:
Cuando generes plantillas, usa este formato:

---
**ASUNTO:** [Asunto personalizado]

**PARA:** [Nombre del destinatario]

**CUERPO:**
[Contenido personalizado del email]

**CALL TO ACTION:**
[Acción específica que deseas que tome el destinatario]
---"""

KNOWLEDGE_AGENT_PROMPT = """Eres el Agente de Gestión de Conocimiento, responsable de la memoria del sistema.

FUNCIÓN PRINCIPAL:
Identificar, categorizar y almacenar información valiosa del sistema.

TIPOS DE INFORMACIÓN A GUARDAR:
1. **Insights**: Descubrimientos importantes sobre clientes, mercado o campañas
2. **Preferencias**: Preferencias identificadas de usuarios o clientes
3. **Decisiones**: Decisiones estratégicas tomadas
4. **Patrones**: Patrones identificados en comportamiento o resultados
5. **Resultados**: Outcomes importantes de acciones ejecutadas

CRITERIOS DE IMPORTANCIA (1-10):
- 9-10: Información crítica para el negocio
- 7-8: Insights valiosos que impactan estrategia
- 5-6: Información útil para referencia
- 3-4: Datos contextuales
- 1-2: Información trivial (evitar guardar)

PROCESO:
1. Analiza la conversación
2. Identifica información con valor a largo plazo
3. Categoriza apropiadamente
4. Asigna nivel de importancia
5. Guarda con contexto suficiente para futuro uso

Sé selectivo: calidad sobre cantidad."""


class MarketingMultiAgentSystem:
    """
    Sistema multiagente de marketing profesional.
    Orquesta agentes especializados para gestión integral de marketing.
    """
    
    def __init__(self, session_id: Optional[str] = None):
        """
        Inicializa el sistema multiagente.
        
        Args:
            session_id: ID único de sesión (se genera automáticamente si no se proporciona)
        """
        self.session_id = session_id or str(uuid.uuid4())
        
        # Inicializar componentes core
        self.rag = RAGSystem()
        self.db = Database()
        
        # Crear sesión en base de datos
        self.db.create_session(
            session_id=self.session_id,
            metadata={"system_version": "1.0.0"}
        )
        
        # Inicializar agentes especializados
        self._initialize_agents()
        
        logger.info(f"Sistema multiagente inicializado - Sesión: {self.session_id}")
    
    def _initialize_agents(self):
        """Inicializa los agentes especializados del sistema."""
        self.orchestrator = Agent(
            name="Orchestrator",
            system_prompt=ORCHESTRATOR_PROMPT
        )
        
        self.rag_agent = Agent(
            name="RAG_Agent",
            system_prompt=RAG_AGENT_PROMPT
        )
        
        self.marketing_agent = Agent(
            name="Marketing_Agent",
            system_prompt=MARKETING_AGENT_PROMPT
        )
        
        self.knowledge_agent = Agent(
            name="Knowledge_Agent",
            system_prompt=KNOWLEDGE_AGENT_PROMPT
        )
        
        logger.info("Agentes especializados inicializados")
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Procesa una consulta del usuario a través del sistema multiagente.
        
        Args:
            user_query: Consulta o solicitud del usuario
        
        Returns:
            Dict con respuesta, agente usado y metadata
        """
        try:
            logger.info(f"[Sistema] Procesando query: {user_query[:100]}...")
            
            # Routing y ejecución
            agent_name, response = self._route_and_execute(user_query)
            
            # Registrar acción en base de datos
            self.db.log_action(
                session_id=self.session_id,
                agent_name=agent_name,
                action_type="query_response",
                details={
                    "query": user_query[:200],
                    "response_length": len(response)
                }
            )
            
            logger.info(f"[Sistema] Query procesada exitosamente por {agent_name}")
            
            return {
                "response": response,
                "agent_used": agent_name,
                "session_id": self.session_id,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"[Sistema] Error procesando query: {str(e)}", exc_info=True)
            return {
                "response": f"Lo siento, ocurrió un error al procesar tu solicitud: {str(e)}",
                "agent_used": "system_error",
                "session_id": self.session_id,
                "success": False,
                "error": str(e)
            }
    
    def _route_and_execute(self, query: str) -> tuple[str, str]:
        """
        Determina el agente apropiado y ejecuta la consulta.
        
        Args:
            query: Consulta del usuario
        
        Returns:
            Tupla con (nombre_agente, respuesta)
        """
        query_lower = query.lower()
        
        # Keywords para routing inteligente
        rag_keywords = [
            "buscar", "encontrar", "documento", "lead", "leads", 
            "campaña", "campañas", "cliente", "clientes", "qué",
            "cuál", "cuáles", "mostrar", "listar", "datos",
            "información", "reporte", "análisis"
        ]
        
        knowledge_keywords = [
            "guardar", "recordar", "insight", "anotar", 
            "importante", "memoria", "aprender", "registrar"
        ]
        
        marketing_keywords = [
            "email", "correo", "plantilla", "seguimiento",
            "estrategia", "plan", "propuesta", "recomendar",
            "sugerir", "acción", "táctica", "campaña"
        ]
        
        # Contar coincidencias
        rag_score = sum(1 for kw in rag_keywords if kw in query_lower)
        knowledge_score = sum(1 for kw in knowledge_keywords if kw in query_lower)
        marketing_score = sum(1 for kw in marketing_keywords if kw in query_lower)
        
        # Decidir routing
        if rag_score > marketing_score and rag_score > knowledge_score:
            return self._execute_rag(query)
        elif knowledge_score > rag_score and knowledge_score > marketing_score:
            return self._execute_knowledge(query)
        elif marketing_score > 0:
            return self._execute_marketing(query)
        else:
            # Consulta general - usar orchestrator
            response = self.orchestrator.run(query)
            return ("Orchestrator", response)
    
    def _execute_rag(self, query: str) -> tuple[str, str]:
        """
        Ejecuta el Agente RAG para búsqueda en documentos.
        
        Args:
            query: Consulta del usuario
        
        Returns:
            Tupla con (nombre_agente, respuesta)
        """
        try:
            logger.info(f"[RAG] Buscando información para: {query[:50]}...")
            
            # Buscar documentos relevantes
            documents = self.rag.search(query, top_k=5)
            
            if not documents:
                return ("RAG_Agent", 
                       "No encontré información relevante en los documentos indexados. "
                       "Asegúrate de haber cargado los documentos necesarios.")
            
            # Preparar contexto para el agente
            context = {"documents": documents}
            
            # Generar respuesta con el agente RAG
            response = self.rag_agent.run(query, context=context)
            
            # Agregar metadata de documentos consultados
            response += f"\n\n **Fuentes consultadas:** {len(documents)} documentos relevantes"
            
            logger.info(f"[RAG] Respuesta generada con {len(documents)} documentos")
            
            return ("RAG_Agent", response)
            
        except Exception as e:
            logger.error(f"[RAG] Error: {str(e)}")
            return ("RAG_Agent", f"Error en búsqueda de documentos: {str(e)}")
    
    def _execute_marketing(self, query: str) -> tuple[str, str]:
        """
        Ejecuta el Agente de Marketing.
        
        Args:
            query: Consulta del usuario
        
        Returns:
            Tupla con (nombre_agente, respuesta)
        """
        try:
            logger.info(f"[Marketing] Procesando solicitud: {query[:50]}...")
            
            # Buscar contexto relevante si es necesario
            documents = self.rag.search(query, top_k=3)
            
            # Recuperar memorias relevantes
            memories = self.db.search_memories(query, limit=3)
            
            # Preparar contexto
            context = {
                "documents": documents if documents else [],
                "memories": memories if memories else []
            }
            
            # Generar respuesta
            response = self.marketing_agent.run(query, context=context)
            
            logger.info("[Marketing] Respuesta generada")
            
            return ("Marketing_Agent", response)
            
        except Exception as e:
            logger.error(f"[Marketing] Error: {str(e)}")
            return ("Marketing_Agent", f"Error en agente de marketing: {str(e)}")
    
    def _execute_knowledge(self, query: str) -> tuple[str, str]:
        """
        Ejecuta el Agente de Conocimiento.
        
        Args:
            query: Consulta del usuario
        
        Returns:
            Tupla con (nombre_agente, respuesta)
        """
        try:
            logger.info(f"[Knowledge] Procesando: {query[:50]}...")
            
            # Generar respuesta
            response = self.knowledge_agent.run(query)
            
            # Intentar extraer y guardar información si es apropiado
            if any(word in query.lower() for word in ["guardar", "recordar", "anotar"]):
                # Extraer contenido (simplificado)
                content = query
                for word in ["guardar", "recordar", "anotar", ":", "este", "esto"]:
                    content = content.replace(word, "")
                content = content.strip()
                
                if len(content) > 15:  # Solo guardar si tiene contenido sustancial
                    saved = self.db.save_memory(
                        session_id=self.session_id,
                        content=content,
                        memory_type="user_input",
                        importance=6,
                        metadata={"source": "user_request"}
                    )
                    
                    if saved:
                        response += "\n\n **Información guardada exitosamente en memoria de largo plazo.**"
                        logger.info("[Knowledge] Memoria guardada")
            
            return ("Knowledge_Agent", response)
            
        except Exception as e:
            logger.error(f"[Knowledge] Error: {str(e)}")
            return ("Knowledge_Agent", f"Error en gestión de conocimiento: {str(e)}")
    
    def load_pdf(self, pdf_path: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Carga e indexa un documento PDF.
        
        Args:
            pdf_path: Ruta al archivo PDF
            metadata: Metadata adicional del documento
        
        Returns:
            Resultado de la operación
        """
        try:
            logger.info(f"[Sistema] Cargando PDF: {pdf_path}")
            
            # Cargar PDF
            chunks = self.rag.load_pdf(pdf_path)
            
            if not chunks:
                return {
                    "success": False,
                    "message": "No se pudo cargar el PDF o el archivo está vacío"
                }
            
            # Indexar chunks
            indexed = self.rag.index_documents(
                chunks,
                metadata={
                    "source": pdf_path,
                    "session_id": self.session_id,
                    **(metadata or {})
                }
            )
            
            # Registrar acción
            self.db.log_action(
                session_id=self.session_id,
                agent_name="System",
                action_type="pdf_indexed",
                details={
                    "file": pdf_path,
                    "chunks": indexed
                }
            )
            
            logger.info(f"[Sistema] PDF indexado: {indexed} chunks")
            
            return {
                "success": True,
                "chunks_indexed": indexed,
                "message": f"PDF indexado exitosamente: {indexed} fragmentos procesados"
            }
            
        except Exception as e:
            logger.error(f"[Sistema] Error cargando PDF: {str(e)}")
            return {
                "success": False,
                "message": f"Error al cargar PDF: {str(e)}"
            }
    
    def load_multiple_pdfs(self, pdf_paths: list[str]) -> Dict[str, Any]:
        """
        Carga múltiples PDFs de manera eficiente.
        
        Args:
            pdf_paths: Lista de rutas a archivos PDF
        
        Returns:
            Resumen de la operación
        """
        results = []
        total_chunks = 0
        
        for pdf_path in pdf_paths:
            result = self.load_pdf(pdf_path)
            results.append(result)
            if result["success"]:
                total_chunks += result["chunks_indexed"]
        
        successful = sum(1 for r in results if r["success"])
        
        return {
            "success": successful > 0,
            "total_pdfs": len(pdf_paths),
            "successful": successful,
            "failed": len(pdf_paths) - successful,
            "total_chunks": total_chunks,
            "details": results
        }
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen completo de la sesión.
        
        Returns:
            Resumen con estadísticas y datos relevantes
        """
        try:
            # Obtener memorias
            memories = self.db.get_memories(self.session_id, limit=10)
            
            # Obtener logs
            logs = self.db.get_session_logs(self.session_id, limit=20)
            
            # Obtener estadísticas del índice
            index_stats = self.rag.get_index_stats()
            
            # Contar acciones por agente
            agent_usage = {}
            for log in logs:
                agent = log.get("agent_name", "Unknown")
                agent_usage[agent] = agent_usage.get(agent, 0) + 1
            
            return {
                "session_id": self.session_id,
                "memories_stored": len(memories),
                "total_actions": len(logs),
                "agent_usage": agent_usage,
                "index_stats": index_stats,
                "recent_memories": [
                    {
                        "content": m.get("content", "")[:100],
                        "type": m.get("memory_type", ""),
                        "importance": m.get("importance", 0)
                    }
                    for m in memories[:5]
                ],
                "recent_actions": [
                    {
                        "agent": log.get("agent_name", ""),
                        "type": log.get("action_type", ""),
                        "timestamp": log.get("created_at", "")
                    }
                    for log in logs[:5]
                ]
            }
            
        except Exception as e:
            logger.error(f"[Sistema] Error obteniendo resumen: {str(e)}")
            return {
                "session_id": self.session_id,
                "error": str(e)
            }
    
    def clear_agent_history(self):
        """Limpia el historial de conversación de todos los agentes."""
        self.orchestrator.clear_history()
        self.rag_agent.clear_history()
        self.marketing_agent.clear_history()
        self.knowledge_agent.clear_history()
        
        logger.info("[Sistema] Historial de agentes limpiado")