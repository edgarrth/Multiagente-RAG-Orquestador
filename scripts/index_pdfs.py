"""
Script para indexar PDFs en Pinecone.
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
    Indexa todos los PDFs del directorio data/pdfs/.
    """
    print("=" * 60)
    print("INDEXACIÓN DE DOCUMENTOS PDF")
    print("=" * 60)
    print()
    
    # Directorio de PDFs
    pdf_dir = Path("./data/pdfs")
    
    if not pdf_dir.exists():
        print(f" El directorio {pdf_dir} no existe")
        print(f"   Créalo con: mkdir -p {pdf_dir}")
        print(f"   Y coloca tus PDFs allí")
        sys.exit(1)
    
    # Buscar PDFs
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"  No se encontraron archivos PDF en {pdf_dir}")
        print(f"   Coloca tus PDFs de marketing en ese directorio")
        print()
        print(" Tipos de documentos recomendados:")
        print("   - Base de datos de leads")
        print("   - Historial de campañas")
        print("   - Segmentación de clientes")
        print("   - Plantillas de email")
        print("   - Notas de reuniones")
        print()
        sys.exit(0)
    
    print(f"Directorio: {pdf_dir}")
    print(f" Archivos encontrados: {len(pdf_files)}")
    print()
    
    for i, pdf in enumerate(pdf_files, 1):
        print(f"   {i}. {pdf.name}")
    print()
    
    try:
        # Inicializar sistema RAG
        logger.info("Inicializando RAGSystem...")
        rag_system = RAGSystem()
        
        # Asegurar que el índice existe
        logger.info("Verificando índice de Pinecone...")
        rag_system.initialize_index()
        
        print(" Sistema RAG inicializado")
        print()
        
        # Procesar cada PDF
        total_chunks = 0
        successful = 0
        failed = 0
        
        for i, pdf_path in enumerate(pdf_files, 1):
            print(f" Procesando {i}/{len(pdf_files)}: {pdf_path.name}")
            
            try:
                # Cargar PDF
                chunks = rag_system.load_pdf(str(pdf_path))
                
                if not chunks:
                    print(f"     No se pudieron extraer chunks")
                    failed += 1
                    continue
                
                print(f"    Extraídos {len(chunks)} fragmentos")
                
                # Indexar en Pinecone
                indexed = rag_system.index_documents(
                    chunks,
                    metadata={
                        "source": str(pdf_path),
                        "filename": pdf_path.name
                    }
                )
                
                if indexed > 0:
                    print(f"    Indexados {indexed} fragmentos")
                    total_chunks += indexed
                    successful += 1
                else:
                    print(f"     No se pudieron indexar fragmentos")
                    failed += 1
                
                print()
                
            except Exception as e:
                print(f"    Error: {str(e)}")
                failed += 1
                print()
        
        # Resumen final
        print("=" * 60)
        print(" RESUMEN DE INDEXACIÓN")
        print("=" * 60)
        print(f"Total de PDFs procesados: {len(pdf_files)}")
        print(f"    Exitosos: {successful}")
        print(f"    Fallidos: {failed}")
        print(f"    Total de fragmentos indexados: {total_chunks}")
        print()
        
        # Verificar índice final
        stats = rag_system.get_index_stats()
        print(f" Estado final del índice:")
        print(f"   - Total de vectores: {stats.get('total_vectors', 0)}")
        print(f"   - Dimensión: {stats.get('dimension', 0)}")
        print()
        
        if successful > 0:
            print("=" * 60)
            print(" INDEXACIÓN COMPLETADA")
            print("=" * 60)
            print()
            print(" Próximos pasos:")
            print("   1. Inicia la aplicación: streamlit run src/ui/app.py")
            print("   2. Prueba consultas como:")
            print("      - '¿Qué leads tenemos disponibles?'")
            print("      - 'Resume las campañas recientes'")
            print()
        else:
            print("  No se indexaron documentos exitosamente")
            print("   Revisa los errores anteriores")
        
    except Exception as e:
        logger.error(f"Error durante la indexación: {str(e)}", exc_info=True)
        print()
        print(" Error crítico durante la indexación")
        print(f"   Error: {str(e)}")
        print()
        print(" Verifica que:")
        print("   - Pinecone está correctamente configurado")
        print("   - Los PDFs no están corruptos o protegidos")
        print("   - Tienes conexión a internet")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()