"""
Sistema RAG (Retrieval Augmented Generation) del sistema multiagente.
"""

from typing import List, Dict, Any
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from pypdf import PdfReader
from pathlib import Path
from src.config.settings import settings
import logging
import time

logger = logging.getLogger(__name__)


class RAGSystem:
    """
    Sistema de Retrieval Augmented Generation.
    Gestiona la indexación y búsqueda de documentos.
    """
    
    def __init__(self):
        """Inicializa el sistema RAG."""
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.pinecone_client = Pinecone(api_key=settings.pinecone_api_key)
        self.index_name = settings.pinecone_index_name
        self.index = None
        
        logger.info("RAGSystem inicializado")
    
    def initialize_index(self):
        """Crea e inicializa el índice de Pinecone."""
        try:
            existing_indexes = [idx.name for idx in self.pinecone_client.list_indexes()]
            
            if self.index_name not in existing_indexes:
                logger.info(f"Creando índice {self.index_name}...")
                
                self.pinecone_client.create_index(
                    name=self.index_name,
                    dimension=settings.pinecone_dimension,
                    metric=settings.pinecone_metric,
                    spec=ServerlessSpec(
                        cloud='aws',
                        region=settings.pinecone_environment
                    )
                )
                
                # Esperar a que esté listo
                while not self.pinecone_client.describe_index(self.index_name).status['ready']:
                    time.sleep(1)
            
            self.index = self.pinecone_client.Index(self.index_name)
            logger.info(f"Índice {self.index_name} listo")
            
        except Exception as e:
            logger.error(f"Error inicializando índice: {str(e)}")
            raise
    
    def load_pdf(self, pdf_path: str) -> List[str]:
        """
        Carga un PDF y lo divide en chunks.
        
        Args:
            pdf_path: Ruta al archivo PDF
        
        Returns:
            Lista de chunks de texto
        """
        try:
            reader = PdfReader(pdf_path)
            text = ""
            
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            # Dividir en chunks
            chunks = self._chunk_text(text)
            
            logger.info(f"PDF cargado: {len(chunks)} chunks de {Path(pdf_path).name}")
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error cargando PDF: {str(e)}")
            return []
    
    def _chunk_text(self, text: str) -> List[str]:
        """Divide texto en chunks de tamaño fijo con overlap."""
        chunk_size = settings.chunk_size
        overlap = settings.chunk_overlap
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            if chunk.strip():
                chunks.append(chunk)
            
            start += chunk_size - overlap
        
        return chunks
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Genera embedding usando OpenAI.
        
        Args:
            text: Texto a convertir
        
        Returns:
            Vector de embedding
        """
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error generando embedding: {str(e)}")
            return []
    
    def index_documents(
        self,
        chunks: List[str],
        metadata: Dict[str, Any] = None
    ) -> int:
        """
        Indexa chunks en Pinecone.
        
        Args:
            chunks: Lista de chunks de texto
            metadata: Metadata adicional
        
        Returns:
            Número de chunks indexados
        """
        if not self.index:
            self.initialize_index()
        
        try:
            vectors = []
            
            for i, chunk in enumerate(chunks):
                # Generar embedding
                embedding = self.generate_embedding(chunk)
                
                if not embedding:
                    continue
                
                # Preparar vector
                vector_id = f"doc_{i}_{hash(chunk)}"
                vector_metadata = {
                    "text": chunk[:1000],  # Primeros 1000 chars
                    "chunk_index": i,
                    **(metadata or {})
                }
                
                vectors.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": vector_metadata
                })
                
                # Indexar en lotes de 100
                if len(vectors) >= 100:
                    self.index.upsert(vectors=vectors)
                    vectors = []
            
            # Indexar resto
            if vectors:
                self.index.upsert(vectors=vectors)
            
            logger.info(f"{len(chunks)} chunks indexados exitosamente")
            
            return len(chunks)
            
        except Exception as e:
            logger.error(f"Error indexando documentos: {str(e)}")
            return 0
    
    def search(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Busca documentos relevantes.
        
        Args:
            query: Query de búsqueda
            top_k: Número de resultados
        
        Returns:
            Lista de documentos encontrados
        """
        if not self.index:
            self.initialize_index()
        
        try:
            # Generar embedding de la query
            query_embedding = self.generate_embedding(query)
            
            if not query_embedding:
                return []
            
            # Buscar en Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            # Formatear resultados
            documents = []
            for match in results.matches:
                documents.append({
                    "text": match.metadata.get("text", ""),
                    "score": match.score,
                    "metadata": match.metadata
                })
            
            logger.info(f"Búsqueda completada: {len(documents)} resultados para '{query[:50]}...'")
            
            return documents
            
        except Exception as e:
            logger.error(f"Error en búsqueda: {str(e)}")
            return []
    
    def answer_question(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        """
        Genera respuesta usando documentos como contexto.
        
        Args:
            query: Pregunta del usuario
            context_docs: Documentos relevantes
        
        Returns:
            Respuesta generada
        """
        try:
            # Construir contexto
            context_text = "\n\n".join([
                f"Documento {i+1} (relevancia: {doc['score']:.2f}):\n{doc['text']}"
                for i, doc in enumerate(context_docs)
            ])
            
            # Construir prompt
            messages = [
                {
                    "role": "system",
                    "content": "Eres un asistente experto en marketing que responde preguntas basándote en los documentos proporcionados. Cita las fuentes cuando sea relevante."
                },
                {
                    "role": "user",
                    "content": f"Contexto de documentos:\n{context_text}\n\nPregunta: {query}\n\nRespuesta:"
                }
            ]
            
            # Llamar a OpenAI
            response = self.openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generando respuesta: {str(e)}")
            return f"Error: {str(e)}"
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del índice."""
        try:
            if not self.index:
                self.initialize_index()
            
            stats = self.index.describe_index_stats()
            
            return {
                "total_vectors": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness
            }
        except Exception as e:
            logger.error(f"Error obteniendo stats: {str(e)}")
            return {}