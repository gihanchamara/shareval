import json
from pathlib import Path
from typing import Dict, Any, Optional
from backend.app.core.config import KNOWLEDGE_BASE_DIR

class KnowledgeBaseRegistry:
    """Loads and caches the spec-driven knowledge base from disk."""

    def __init__(self, kb_dir: Path = KNOWLEDGE_BASE_DIR):
        self.kb_dir = kb_dir
        self._index: Optional[Dict[str, Any]] = None

    def get_index(self) -> Dict[str, Any]:
        """Returns the parsed master index.json."""
        index_file = self.kb_dir / "index.json"
        if not index_file.exists():
            return {"error": f"index.json not found in {self.kb_dir}"}
        
        with open(index_file, "r", encoding="utf-8") as f:
            self._index = json.load(f)
        return self._index

    def get_spec(self, spec_id: str) -> Optional[Dict[str, Any]]:
        """Returns full markdown spec content along with indexed metadata."""
        index = self.get_index()
        specs = index.get("specs", {})
        if spec_id not in specs:
            return None

        spec_meta = specs[spec_id]
        file_path = self.kb_dir / spec_meta.get("filePath", "")
        
        content = ""
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = f"# Error\nSpecification file not found at: {file_path}"

        return {
            "metadata": spec_meta,
            "content": content
        }

kb_registry = KnowledgeBaseRegistry()
