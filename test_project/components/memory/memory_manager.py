"""
Memory Management Component for Autonomous Agents
Provides persistent memory, context management, and knowledge retention
"""

import json
import sqlite3
import hashlib
import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

class MemoryType(Enum):
    CONVERSATION = "conversation"
    KNOWLEDGE = "knowledge"
    EXPERIENCE = "experience"
    CONTEXT = "context"
    REFLECTION = "reflection"

@dataclass
class MemoryEntry:
    """Represents a single memory entry"""
    id: str
    type: MemoryType
    content: str
    metadata: Dict[str, Any]
    timestamp: datetime.datetime
    importance: float
    tags: List[str]
    embedding: Optional[List[float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['type'] = self.type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        """Create from dictionary"""
        data['timestamp'] = datetime.datetime.fromisoformat(data['timestamp'])
        data['type'] = MemoryType(data['type'])
        return cls(**data)

class MemoryManager:
    """Manages persistent memory for autonomous agents"""
    
    def __init__(self, db_path: str = "agent_memory.db", max_entries: int = 10000):
        self.db_path = Path(db_path)
        self.max_entries = max_entries
        self._init_database()
    
    def _init_database(self):
        """Initialize the memory database"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    timestamp TEXT NOT NULL,
                    importance REAL NOT NULL,
                    tags TEXT,
                    embedding TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_type ON memories(type)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_importance ON memories(importance)
            """)
    
    def store_memory(self, 
                    content: str, 
                    memory_type: MemoryType,
                    metadata: Dict[str, Any] = None,
                    importance: float = 0.5,
                    tags: List[str] = None) -> str:
        """Store a new memory entry"""
        
        # Generate unique ID
        memory_id = hashlib.sha256(
            f"{content}{datetime.datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        # Create memory entry
        memory = MemoryEntry(
            id=memory_id,
            type=memory_type,
            content=content,
            metadata=metadata or {},
            timestamp=datetime.datetime.now(),
            importance=importance,
            tags=tags or []
        )
        
        # Store in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO memories 
                (id, type, content, metadata, timestamp, importance, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                memory.id,
                memory.type.value,
                memory.content,
                json.dumps(memory.metadata),
                memory.timestamp.isoformat(),
                memory.importance,
                json.dumps(memory.tags)
            ))
        
        # Cleanup old memories if needed
        self._cleanup_old_memories()
        
        return memory_id
    
    def retrieve_memories(self, 
                         memory_type: Optional[MemoryType] = None,
                         tags: List[str] = None,
                         min_importance: float = 0.0,
                         limit: int = 100) -> List[MemoryEntry]:
        """Retrieve memories based on criteria"""
        
        query = "SELECT * FROM memories WHERE importance >= ?"
        params = [min_importance]
        
        if memory_type:
            query += " AND type = ?"
            params.append(memory_type.value)
        
        if tags:
            # Simple tag matching - could be improved with better search
            tag_conditions = " OR ".join(["tags LIKE ?" for _ in tags])
            query += f" AND ({tag_conditions})"
            params.extend([f"%{tag}%" for tag in tags])
        
        query += " ORDER BY importance DESC, timestamp DESC LIMIT ?"
        params.append(limit)
        
        memories = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            for row in cursor.fetchall():
                memory_data = {
                    'id': row[0],
                    'type': row[1],
                    'content': row[2],
                    'metadata': json.loads(row[3]) if row[3] else {},
                    'timestamp': row[4],
                    'importance': row[5],
                    'tags': json.loads(row[6]) if row[6] else []
                }
                memories.append(MemoryEntry.from_dict(memory_data))
        
        return memories
    
    def search_memories(self, query: str, limit: int = 50) -> List[MemoryEntry]:
        """Search memories by content"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM memories 
                WHERE content LIKE ? 
                ORDER BY importance DESC, timestamp DESC 
                LIMIT ?
            """, (f"%{query}%", limit))
            
            memories = []
            for row in cursor.fetchall():
                memory_data = {
                    'id': row[0],
                    'type': row[1],
                    'content': row[2],
                    'metadata': json.loads(row[3]) if row[3] else {},
                    'timestamp': row[4],
                    'importance': row[5],
                    'tags': json.loads(row[6]) if row[6] else []
                }
                memories.append(MemoryEntry.from_dict(memory_data))
        
        return memories
    
    def update_memory_importance(self, memory_id: str, importance: float):
        """Update the importance of a memory"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE memories SET importance = ? WHERE id = ?
            """, (importance, memory_id))
    
    def delete_memory(self, memory_id: str):
        """Delete a specific memory"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about stored memories"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total,
                    AVG(importance) as avg_importance,
                    type,
                    COUNT(*) as count_by_type
                FROM memories 
                GROUP BY type
            """)
            
            stats = {
                'total_memories': 0,
                'average_importance': 0.0,
                'by_type': {}
            }
            
            for row in cursor.fetchall():
                if stats['total_memories'] == 0:
                    stats['total_memories'] = row[0]
                    stats['average_importance'] = row[1]
                
                stats['by_type'][row[2]] = row[3]
        
        return stats
    
    def _cleanup_old_memories(self):
        """Remove old memories if we exceed max_entries"""
        with sqlite3.connect(self.db_path) as conn:
            # Count current memories
            cursor = conn.execute("SELECT COUNT(*) FROM memories")
            count = cursor.fetchone()[0]
            
            if count > self.max_entries:
                # Delete oldest, least important memories
                excess = count - self.max_entries
                conn.execute("""
                    DELETE FROM memories 
                    WHERE id IN (
                        SELECT id FROM memories 
                        ORDER BY importance ASC, timestamp ASC 
                        LIMIT ?
                    )
                """, (excess,))
    
    def export_memories(self, file_path: str):
        """Export memories to JSON file"""
        memories = self.retrieve_memories(limit=self.max_entries)
        memory_data = [memory.to_dict() for memory in memories]
        
        with open(file_path, 'w') as f:
            json.dump(memory_data, f, indent=2, default=str)
    
    def import_memories(self, file_path: str):
        """Import memories from JSON file"""
        with open(file_path, 'r') as f:
            memory_data = json.load(f)
        
        for data in memory_data:
            memory = MemoryEntry.from_dict(data)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO memories 
                    (id, type, content, metadata, timestamp, importance, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    memory.id,
                    memory.type.value,
                    memory.content,
                    json.dumps(memory.metadata),
                    memory.timestamp.isoformat(),
                    memory.importance,
                    json.dumps(memory.tags)
                ))
