"""
Script para inicializar las tablas en Supabase.
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.database import Database
from src.config.settings import settings
from supabase import create_client
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# SQL para crear las tablas
SQL_CREATE_TABLES = """
-- Tabla de sesiones
CREATE TABLE IF NOT EXISTS sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sessions_session_id ON sessions(session_id);

-- Tabla de memorias de largo plazo
CREATE TABLE IF NOT EXISTS long_term_memories (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    memory_type VARCHAR(100) NOT NULL,
    importance INTEGER DEFAULT 5 CHECK (importance >= 1 AND importance <= 10),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ltm_session_id ON long_term_memories(session_id);
CREATE INDEX IF NOT EXISTS idx_ltm_memory_type ON long_term_memories(memory_type);
CREATE INDEX IF NOT EXISTS idx_ltm_importance ON long_term_memories(importance);

-- Tabla de logs de acciones
CREATE TABLE IF NOT EXISTS action_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    agent_name VARCHAR(100) NOT NULL,
    action_type VARCHAR(100) NOT NULL,
    action_details JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'completed',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_actions_session_id ON action_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_actions_agent_name ON action_logs(agent_name);
CREATE INDEX IF NOT EXISTS idx_actions_created_at ON action_logs(created_at);

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para sessions
DROP TRIGGER IF EXISTS update_sessions_updated_at ON sessions;
CREATE TRIGGER update_sessions_updated_at
    BEFORE UPDATE ON sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
"""


def main():
    """
    Crea las tablas necesarias en Supabase.
    """
    print("=" * 60)
    print("INICIALIZACIÓN DE SUPABASE")
    print("=" * 60)
    print()
    
    print(f" Configuración:")
    print(f"   - URL: {settings.supabase_url}")
    print(f"   - Database: PostgreSQL")
    print()
    
    try:
        # Conectar a Supabase
        logger.info("Conectando a Supabase...")
        client = create_client(settings.supabase_url, settings.supabase_key)
        
        print("  NOTA: Las tablas deben crearse manualmente en Supabase SQL Editor")
        print()
        print(" Copia y ejecuta el siguiente SQL en tu proyecto de Supabase:")
        print()
        print("-" * 60)
        print(SQL_CREATE_TABLES)
        print("-" * 60)
        print()
        
        # Verificar conexión creando instancia de Database
        logger.info("Verificando conexión...")
        db = Database()
        
        print("Conexión a Supabase verificada")
        print()
        print("=" * 60)
        print("VERIFICACIÓN COMPLETADA")
        print("=" * 60)
        print()
        print(" Próximos pasos:")
        print("   1. Copia el SQL mostrado arriba")
        print("   2. Ve a tu proyecto en Supabase (https://supabase.com)")
        print("   3. Abre el SQL Editor")
        print("   4. Pega y ejecuta el SQL")
        print("   5. Verifica que las tablas se hayan creado")
        print()
        
    except Exception as e:
        logger.error(f"Error inicializando Supabase: {str(e)}", exc_info=True)
        print()
        print(" Error durante la verificación")
        print(f"   Error: {str(e)}")
        print()
        print(" Asegúrate de que:")
        print("   - Las variables de entorno están configuradas correctamente en .env")
        print("   - La URL y API key de Supabase son válidas")
        print("   - Tienes acceso al proyecto de Supabase")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()