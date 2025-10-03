from collections import deque
from time import time
from typing import List
from .models import Evidence

class EvidenceBus:
    def __init__(self, ttl_seconds: int = 300):
        self.ttl = ttl_seconds
        self.q = deque()

    def add(self, ev: Evidence):
        self.q.append((time(), ev))

    def snapshot(self) -> List[Evidence]:
        cutoff = time() - self.ttl
        while self.q and self.q[0][0] < cutoff:
            self.q.popleft()
        return [ev for _, ev in list(self.q)]
