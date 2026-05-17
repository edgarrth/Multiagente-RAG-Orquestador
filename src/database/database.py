"""
Gestor de base de datos del sistema multiagente.
"""

from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from src.config.settings import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Database:
    """
    Gestor de base de datos para memoria de largo plazo.
    Interactúa directamente con Supabase.
    """
    
    def __init__(self):
        """Inicializa conexión con Supabase."""
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
        logger.info("Database inicializado")
    
    # ============================================
    # MEMORIAS DE LARGO PLAZO
    # ============================================
    
    def save_memory(
        self,
        session_id: str,
        content: str,
        memory_type: str = "insight",
        importance: int = 5,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Guarda una memoria en el sistema.
        
        Args:
            session_id: ID de sesión
            content: Contenido de la memoria
            memory_type: Tipo de memoria (insight, preference, decision, etc.)
            importance: Importancia de 1 a 10
            metadata: Metadata adicional
        
        Returns:
            Memoria guardada
        """
        try:
            data = {
                "session_id": session_id,
                "content": content,
                "memory_type": memory_type,
                "importance": importance,
                "metadata": metadata or {},
                "created_at": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat()
            }
            
            result = self.client.table("long_term_memories").insert(data).execute()
            
            logger.info(f"Memoria guardada: {memory_type} - Importancia: {importance}")
            
            return result.data[0] if result.data else {}
            
        except Exception as e:
            logger.error(f"Error guardando memoria: {str(e)}")
            return {}
    
    def get_memories(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Recupera memorias de una sesión.
        
        Args:
            session_id: ID de sesión
            limit: Número máximo de memorias
        
        Returns:
            Lista de memorias ordenadas por importancia
        """
        try:
            result = self.client.table("long_term_memories")\
                .select("*")\
                .eq("session_id", session_id)\
                .order("importance", desc=True)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error recuperando memorias: {str(e)}")
            return []
    
    def search_memories(
        self,
        search_term: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Busca memorias por contenido.
        
        Args:
            search_term: Término de búsqueda
            limit: Número de resultados
        
        Returns:
            Memorias que contienen el término
        """
        try:
            result = self.client.table("long_term_memories")\
                .select("*")\
                .ilike("content", f"%{search_term}%")\
                .order("importance", desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error buscando memorias: {str(e)}")
            return []
    
    def update_memory_access(self, memory_id: str) -> bool:
        """
        Actualiza el timestamp de último acceso.
        
        Args:
            memory_id: ID de la memoria
        
        Returns:
            True si se actualizó correctamente
        """
        try:
            self.client.table("long_term_memories")\
                .update({"last_accessed": datetime.now().isoformat()})\
                .eq("id", memory_id)\
                .execute()
            
            return True
        except Exception as e:
            logger.error(f"Error actualizando acceso: {str(e)}")
            return False
    
    # ============================================
    # SESIONES
    # ============================================
    
    def create_session(
        self,
        session_id: str,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Crea una nueva sesión.
        
        Args:
            session_id: ID único de sesión
            metadata: Metadata adicional
        
        Returns:
            Sesión creada
        """
        try:
            data = {
                "session_id": session_id,
                "metadata": metadata or {},
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            result = self.client.table("sessions").insert(data).execute()
            
            logger.info(f"Sesión creada: {session_id}")
            
            return result.data[0] if result.data else {}
            
        except Exception as e:
            logger.error(f"Error creando sesión: {str(e)}")
            return {}
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información de una sesión.
        
        Args:
            session_id: ID de sesión
        
        Returns:
            Datos de sesión o None
        """
        try:
            result = self.client.table("sessions")\
                .select("*")\
                .eq("session_id", session_id)\
                .execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"Error obteniendo sesión: {str(e)}")
            return None
    
    def update_session(
        self,
        session_id: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Actualiza metadata de una sesión.
        
        Args:
            session_id: ID de sesión
            metadata: Nueva metadata
        
        Returns:
            True si se actualizó correctamente
        """
        try:
            self.client.table("sessions")\
                .update({
                    "metadata": metadata,
                    "updated_at": datetime.now().isoformat()
                })\
                .eq("session_id", session_id)\
                .execute()
            
            return True
        except Exception as e:
            logger.error(f"Error actualizando sesión: {str(e)}")
            return False
    
    # ============================================
    # LOGS DE ACCIONES
    # ============================================
    
    def log_action(
        self,
        session_id: str,
        agent_name: str,
        action_type: str,
        details: Dict[str, Any] = None,
        status: str = "completed"
    ) -> Dict[str, Any]:
        """
        Registra una acción ejecutada.
        
        Args:
            session_id: ID de sesión
            agent_name: Nombre del agente que ejecutó la acción
            action_type: Tipo de acción
            details: Detalles adicionales
            status: Estado de la acción
        
        Returns:
            Log creado
        """
        try:
            data = {
                "session_id": session_id,
                "agent_name": agent_name,
                "action_type": action_type,
                "action_details": details or {},
                "status": status,
                "created_at": datetime.now().isoformat()
            }
            
            result = self.client.table("action_logs").insert(data).execute()
            
            logger.info(f"Acción registrada: {agent_name} - {action_type}")
            
            return result.data[0] if result.data else {}
            
        except Exception as e:
            logger.error(f"Error registrando acción: {str(e)}")
            return {}
    
    def get_session_logs(
        self,
        session_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Obtiene logs de una sesión.
        
        Args:
            session_id: ID de sesión
            limit: Número máximo de logs
        
        Returns:
            Lista de logs
        """
        try:
            result = self.client.table("action_logs")\
                .select("*")\
                .eq("session_id", session_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error obteniendo logs: {str(e)}")
            return []