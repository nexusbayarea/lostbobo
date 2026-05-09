class DirtyTracker:
    def __init__(self):
        self.dirty: set[str] = set()

    def mark_dirty(self, node_id: str):
        self.dirty.add(node_id)

    def is_dirty(self, node_id: str) -> bool:
        return node_id in self.dirty

    def clear(self, node_id: str):
        self.dirty.discard(node_id)
