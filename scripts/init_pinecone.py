"""
Script para inicializar el índice de Pinecone.
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag.rag_system import RAGSystem
from src.config.settings import settings
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """
    Inicializa el índice de Pinecone.
    """
    print("=" * 60)
    print("INICIALIZACIÓN DE PINECONE")
    print("=" * 60)
    print()
    
    print(f" Configuración:")
    print(f"   - Index Name: {settings.pinecone_index_name}")
    print(f"   - Dimension: {settings.pinecone_dimension}")
    print(f"   - Metric: {settings.pinecone_metric}")
    print(f"   - Environment: {settings.pinecone_environment}")
    print()
    
    try:
        # Crear sistema RAG
        logger.info("Inicializando RAGSystem...")
        rag_system = RAGSystem()
        
        # Crear índice
        logger.info("Creando índice en Pinecone...")
        rag_system.initialize_index()
        
        # Verificar índice
        stats = rag_system.get_index_stats()
        
        print()
        print(" Índice creado exitosamente!")
        print()
        print(f" Estadísticas del índice:")
        print(f"   - Total de vectores: {stats.get('total_vectors', 0)}")
        print(f"   - Dimensión: {stats.get('dimension', 0)}")
        print(f"   - Fullness: {stats.get('index_fullness', 0):.2%}")
        print()
        print("=" * 60)
        print(" INICIALIZACIÓN COMPLETADA")
        print("=" * 60)
        print()
        print(" Próximos pasos:")
        print("   1. Coloca tus archivos PDF en la carpeta data/pdfs/")
        print("   2. Ejecuta: python scripts/index_pdfs.py")
        print()
        
    except Exception as e:
        logger.error(f"Error inicializando Pinecone: {str(e)}", exc_info=True)
        print()
        print(" Error durante la inicialización")
        print(f"   Error: {str(e)}")
        print()
        print(" Verifica que:")
        print("   - Tu PINECONE_API_KEY es correcta en el archivo .env")
        print("   - Tienes una cuenta activa en Pinecone")
        print("   - El nombre del índice no existe ya (o úsalo si existe)")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()