import asyncio
import google.generativeai as genai
from typing import List, Dict, Any
import traceback
from app.services.retrieval import SimpleRetriever
from app.core.database import db_manager
from app.models.schemas import Chunk
from app.core.config import settings
import os
from dotenv import load_dotenv

load_dotenv()

class GeminiSpeculativeRAG:
    """Production-grade Gemini RAG with query expansion and verification"""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.available = False
        
        if api_key and api_key != "your_gemini_api_key_here":
            try:
                genai.configure(api_key=api_key)
                test_model = genai.GenerativeModel(settings.drafter_model)
                test_model.generate_content("test")
                self.available = True
                print(f"✓ Gemini API initialized with {settings.drafter_model}")
            except Exception as e:
                print(f"✗ Gemini API initialization failed: {e}")
                self.available = False
        else:
            print("✗ No valid Gemini API key found")
            self.available = False
    
    async def expand_query(self, query: str) -> List[str]:
        """Generate query variations for better retrieval"""
        if not self.available:
            return [query]
        
        try:
            model = genai.GenerativeModel(settings.drafter_model)
            prompt = f"""Generate 2 alternative phrasings of this query (one per line, no numbering):
{query}

Alternatives:"""
            
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(temperature=0.3, max_output_tokens=100)
            )
            
            alternatives = [line.strip() for line in response.text.strip().split('\n') if line.strip() and len(line.strip()) > 10]
            return [query] + alternatives[:2]
        except:
            return [query]
    
    async def generate_answer(self, query: str, chunks: List[Chunk]) -> Dict[str, Any]:
        """Production-grade answer generation with query expansion"""
        
        print(f"\n=== GENERATION START ===")
        print(f"Query: {query}")
        print(f"Chunks available: {len(chunks)}")
        
        if not chunks:
            return self._no_docs_response(query)
        
        # Step 1: Query expansion for better context selection
        expanded_queries = await self.expand_query(query)
        print(f"Expanded queries: {len(expanded_queries)}")
        
        # Step 2: Select best chunks using expanded queries
        best_chunks = self._select_best_chunks(query, expanded_queries, chunks)
        print(f"Selected {len(best_chunks)} best chunks")
        
        # Step 3: Generate with Gemini
        if self.available:
            try:
                result = await self._generate_with_gemini(query, best_chunks)
                print(f"✓ Gemini generation successful")
                return result
            except Exception as e:
                print(f"✗ Gemini generation failed: {e}")
        
        return self._enhanced_extraction(query, best_chunks)
    
    def _select_best_chunks(self, original_query: str, expanded_queries: List[str], chunks: List[Chunk]) -> List[Chunk]:
        """Select most relevant chunks using query expansion"""
        if len(chunks) <= 8:
            return chunks
        
        # Score each chunk against all query variations
        chunk_scores = {}
        for chunk in chunks:
            score = 0
            content_lower = chunk.content.lower()
            
            for query in expanded_queries:
                query_words = set(query.lower().split())
                content_words = set(content_lower.split())
                overlap = len(query_words.intersection(content_words))
                score += overlap / len(query_words) if query_words else 0
            
            # Add vector similarity if available
            if hasattr(chunk, 'similarity_score') and chunk.similarity_score:
                score += chunk.similarity_score * 2
            
            chunk_scores[chunk.id] = score
        
        # Sort by score and return top 8
        sorted_chunks = sorted(chunks, key=lambda c: chunk_scores.get(c.id, 0), reverse=True)
        return sorted_chunks[:8]
    
    async def _generate_with_gemini(self, query: str, chunks: List[Chunk]) -> Dict[str, Any]:
        """Generate answer with strict context adherence"""
        
        context_parts = []
        for i, chunk in enumerate(chunks):
            context_parts.append(f"[Source {i+1}]\n{chunk.content}")
        
        context = "\n\n".join(context_parts)
        
        prompt = f"""You are a precise AI assistant. Answer ONLY using the provided sources.

STRICT RULES:
1. Use ONLY information from sources below
2. Cite each statement with [Source X]
3. If sources lack information, say "I don't have enough information in the provided sources"
4. Never add external knowledge
5. Quote relevant parts when possible

SOURCES:
{context}

QUESTION: {query}

ANSWER (with citations):"""
        
        try:
            model = genai.GenerativeModel(settings.verifier_model)  # Use verifier for better quality
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.05,  # Very low for maximum factuality
                    top_p=0.9,
                    top_k=40,
                    max_output_tokens=2048,
                )
            )
            
            answer_text = response.text
            
            # Validate response
            if not answer_text or len(answer_text.strip()) < 20:
                raise ValueError("Generated answer too short or empty")
            
            # Calculate confidence
            confidence = self._calculate_confidence(answer_text, chunks)
            
            return {
                "answer": answer_text,
                "confidence": confidence,
                "sources": self._extract_sources(chunks),
                "model": settings.verifier_model
            }
            
        except Exception as e:
            print(f"Gemini API call failed: {e}")
            raise
    
    def _no_docs_response(self, query: str) -> Dict[str, Any]:
        """Response when no documents are available"""
        return {
            "answer": f"I don't have any relevant documents to answer your question: '{query}'. Please upload documents first.",
            "confidence": 0.1,
            "sources": [],
            "model": "no-documents"
        }
    
    def _enhanced_extraction(self, query: str, chunks: List[Chunk]) -> Dict[str, Any]:
        """Enhanced extraction when AI models unavailable"""
        
        # Build comprehensive answer from chunks
        answer_parts = [f"Based on the available documents, here's what I found regarding '{query}':\n"]
        
        for i, chunk in enumerate(chunks[:5], 1):
            # Extract key sentences
            content = chunk.content[:500]
            answer_parts.append(f"\n{i}. From document section {chunk.id}:\n{content}...")
        
        answer_parts.append(f"\n\nThis information is compiled from {len(chunks)} relevant document sections.")
        
        return {
            "answer": "".join(answer_parts),
            "confidence": 0.75,
            "sources": self._extract_sources(chunks[:5]),
            "model": "enhanced-extraction"
        }
    
    def _calculate_confidence(self, answer: str, chunks: List[Chunk]) -> float:
        """Calculate confidence based on answer-context overlap and citations"""
        if not answer or len(answer) < 20:
            return 0.3
        
        # Check groundedness
        answer_words = set(answer.lower().split())
        context_words = set(' '.join([c.content for c in chunks]).lower().split())
        overlap = len(answer_words.intersection(context_words))
        groundedness = min(overlap / len(answer_words) if answer_words else 0, 1.0)
        
        # Check for citations
        citation_count = answer.count('[Source')
        has_citations = citation_count > 0
        
        # Check answer length (not too short, not too long)
        length_score = min(len(answer) / 200, 1.0) if len(answer) < 1000 else 0.9
        
        # Calculate final confidence
        base_confidence = (groundedness * 0.5) + (length_score * 0.3)
        if has_citations:
            base_confidence += 0.2
        
        return min(round(base_confidence, 2), 0.98)
    
    def _extract_sources(self, chunks: List[Chunk]) -> List[Dict[str, Any]]:
        return [{
            "chunk_id": c.id, 
            "document_id": c.document_id,
            "content": c.content,  # Full content for metrics
            "content_preview": c.content[:200]
        } for c in chunks]

gemini_speculative_rag = GeminiSpeculativeRAG()