"""
Implementación de agentes del sistema multiagente.
"""

from typing import List, Dict, Any
from openai import OpenAI
from src.config.settings import settings
import json
import logging

logger = logging.getLogger(__name__)


class Agent:
    """
    Agente inteligente que interactúa directamente con OpenAI.
    Implementa el patrón ReAct (Reason + Act).
    """
    
    def __init__(
        self,
        name: str,
        system_prompt: str,
        tools_descriptions: List[Dict[str, str]] = None
    ):
        """
        Inicializa el agente.
        
        Args:
            name: Nombre del agente
            system_prompt: Instrucciones del sistema
            tools_descriptions: Descripciones de herramientas disponibles
        """
        self.name = name
        self.system_prompt = system_prompt
        self.tools_descriptions = tools_descriptions or []
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.conversation_history = []
        
        logger.info(f"Agente '{name}' inicializado")
    
    def run(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """
        Ejecuta el agente con un input del usuario.
        
        Args:
            user_input: Mensaje del usuario
            context: Contexto adicional
        
        Returns:
            Respuesta del agente
        """
        try:
            # Construir mensajes
            messages = self._build_messages(user_input, context)
            
            # Llamada a OpenAI
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                temperature=settings.openai_temperature,
                max_tokens=settings.openai_max_tokens
            )
            
            # Extraer respuesta
            answer = response.choices[0].message.content
            
            # Guardar en historial
            self.conversation_history.append({
                "role": "user",
                "content": user_input
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": answer
            })
            
            logger.info(f"[{self.name}] Respuesta generada")
            
            return answer
            
        except Exception as e:
            logger.error(f"Error en agente {self.name}: {str(e)}")
            return f"Error: {str(e)}"
    
    def _build_messages(
        self,
        user_input: str,
        context: Dict[str, Any] = None
    ) -> List[Dict[str, str]]:
        """Construye los mensajes para OpenAI."""
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Agregar contexto si existe
        if context:
            context_str = self._format_context(context)
            if context_str:
                messages.append({
                    "role": "system",
                    "content": f"Contexto adicional:\n{context_str}"
                })
        
        # Agregar historial (últimos 10 mensajes)
        if self.conversation_history:
            messages.extend(self.conversation_history[-10:])
        
        # Agregar mensaje actual
        messages.append({
            "role": "user",
            "content": user_input
        })
        
        return messages
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Formatea el contexto para incluirlo en el prompt."""
        parts = []
        
        if context.get("documents"):
            docs = context["documents"][:3]
            parts.append(f"Documentos relevantes encontrados: {len(docs)}")
            for i, doc in enumerate(docs, 1):
                parts.append(f"\nDocumento {i}:\n{doc.get('text', '')[:200]}...")
        
        if context.get("memories"):
            mems = context["memories"][:2]
            parts.append(f"\n\nInformación previa relevante:")
            for mem in mems:
                parts.append(f"- {mem.get('content', '')}")
        
        return "\n".join(parts)
    
    def clear_history(self):
        """Limpia el historial de conversación."""
        self.conversation_history = []
        logger.info(f"[{self.name}] Historial limpiado")