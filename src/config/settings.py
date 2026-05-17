"""
Configuración centralizada del sistema.
Maneja todas las variables de entorno y configuraciones globales.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    Configuración global del sistema.
    Lee variables de entorno y proporciona valores por defecto.
    """
    
    # Configuración de Pydantic para permitir campos extra
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  
    )
    
    # ============================================
    # GENERAL
    # ============================================
    environment: str = Field(default="development")
    log_level: str = Field(default="INFO")
    
    # ============================================
    # OPENAI
    # ============================================
    openai_api_key: str = Field(..., description="API Key de OpenAI")
    openai_model: str = Field(default="gpt-4o-mini")
    openai_temperature: float = Field(default=0.7)
    openai_max_tokens: int = Field(default=4000)
    
    # ============================================
    # PINECONE
    # ============================================
    pinecone_api_key: str = Field(..., description="API Key de Pinecone")
    pinecone_environment: str = Field(default="us-east-1")
    pinecone_index_name: str = Field(default="marketing-knowledge")
    pinecone_dimension: int = Field(default=1536)
    pinecone_metric: str = Field(default="cosine")
    
    # ============================================
    # SUPABASE
    # ============================================
    supabase_url: str = Field(..., description="URL del proyecto Supabase")
    supabase_key: str = Field(..., description="Supabase anon key")
    database_url: str = Field(..., description="URL de conexión PostgreSQL")
    
    # ============================================
    # CALENDLY 
    # ============================================
    calendly_api_key: Optional[str] = Field(default=None, description="Token de API de Calendly")
    calendly_user_uri: Optional[str] = Field(default=None, description="URI del usuario Calendly")
    calendly_event_type: Optional[str] = Field(default=None, description="Tipo de evento Calendly")
    
    # ============================================
    # RAG
    # ============================================
    chunk_size: int = Field(default=1000)
    chunk_overlap: int = Field(default=200)
    max_retrieval_documents: int = Field(default=5)


# Instancia global
settings = Settings()