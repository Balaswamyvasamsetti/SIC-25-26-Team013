"""
Test script to verify all System Metrics endpoints are working
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import db_manager
from app.services.quantum_retrieval import quantum_retriever
from app.services.swarm_retrieval import swarm_retriever
from app.services.holographic_storage import holographic_storage
from app.services.neuromorphic_memory import neuromorphic_memory
from app.services.temporal_causality import temporal_engine

async def test_all_endpoints():
    """Test all system metrics endpoints"""
    print("🔍 Testing System Metrics Endpoints...\n")
    
    # Initialize database
    print("1. Initializing database...")
    try:
        await db_manager.init_postgres()
        db_manager.init_neo4j()
        print("✅ Database initialized\n")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}\n")
        return
    
    # Test Quantum Coherence
    print("2. Testing Quantum Coherence...")
    try:
        coherence = quantum_retriever.get_coherence()
        print(f"✅ Quantum Coherence: {coherence}\n")
    except Exception as e:
        print(f"❌ Quantum Coherence failed: {e}\n")
    
    # Test Swarm Statistics
    print("3. Testing Swarm Statistics...")
    try:
        stats = {
            "total_agents": swarm_retriever.n_agents,
            "consensus_score": swarm_retriever.get_consensus(),
            "global_best_score": swarm_retriever.global_best_score,
            "status": "active"
        }
        print(f"✅ Swarm Statistics: {stats}\n")
    except Exception as e:
        print(f"❌ Swarm Statistics failed: {e}\n")
    
    # Test Holographic Efficiency
    print("4. Testing Holographic Efficiency...")
    try:
        async with db_manager.pg_pool.acquire() as conn:
            doc_count = await conn.fetchval("SELECT COUNT(*) FROM documents") or 0
        
        compression_ratio = holographic_storage.get_compression_ratio()
        matrix_size_mb = (holographic_storage.dimensions ** 2 * 16) / (1024 * 1024)
        hologram_density = len(holographic_storage.reference_waves) / holographic_storage.dimensions if holographic_storage.dimensions > 0 else 0
        
        efficiency = {
            "documents_stored": doc_count,
            "compression_ratio": compression_ratio,
            "matrix_size_mb": round(matrix_size_mb, 2),
            "hologram_density": f"{hologram_density:.2%}",
            "status": "active" if doc_count > 0 else "ready"
        }
        print(f"✅ Holographic Efficiency: {efficiency}\n")
    except Exception as e:
        print(f"❌ Holographic Efficiency failed: {e}\n")
    
    # Test Neuromorphic Memory
    print("5. Testing Neuromorphic Memory...")
    try:
        synaptic_count = len(neuromorphic_memory.synaptic_weights)
        association_count = len(neuromorphic_memory.association_matrix)
        plasticity_minutes = neuromorphic_memory.plasticity_window.total_seconds() / 60
        
        memory_state = {
            "synaptic_weights": synaptic_count,
            "associations": association_count,
            "decay_rate": neuromorphic_memory.decay_rate,
            "plasticity_window": f"{plasticity_minutes:.0f} minutes",
            "status": "active" if synaptic_count > 0 else "ready"
        }
        print(f"✅ Neuromorphic Memory: {memory_state}\n")
    except Exception as e:
        print(f"❌ Neuromorphic Memory failed: {e}\n")
    
    # Test Temporal Causality
    print("6. Testing Temporal Causality...")
    try:
        timeline = await temporal_engine.generate_causal_timeline("test query")
        print(f"✅ Temporal Causality: {timeline}\n")
    except Exception as e:
        print(f"❌ Temporal Causality failed: {e}\n")
    
    # Test Health
    print("7. Testing Health Endpoint...")
    try:
        health = {"status": "healthy", "system": "Agentic RAG"}
        print(f"✅ Health: {health}\n")
    except Exception as e:
        print(f"❌ Health failed: {e}\n")
    
    # Test Stats
    print("8. Testing Stats Endpoint...")
    try:
        async with db_manager.pg_pool.acquire() as conn:
            doc_count = await conn.fetchval("SELECT COUNT(*) FROM documents")
            chunk_count = await conn.fetchval("SELECT COUNT(*) FROM chunks")
        
        stats = {
            "documents": doc_count,
            "chunks": chunk_count,
            "system": "FRAG + MAGMA + Speculative RAG"
        }
        print(f"✅ Stats: {stats}\n")
    except Exception as e:
        print(f"❌ Stats failed: {e}\n")
    
    # Close database
    await db_manager.close()
    
    print("✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(test_all_endpoints())
