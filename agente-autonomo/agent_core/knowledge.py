from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple
import time


@dataclass
class KnowledgeItem:
    id: int
    question: str
    answer: str
    created_at: float
    last_used_at: float


class KnowledgeBase:
    """Banco de conhecimento local e global para o agente.

    Implementação simples baseada em SQLite, pensada para crescer ao
    longo do tempo. Não depende de serviços externos.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.path)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer   TEXT NOT NULL,
                created_at REAL NOT NULL,
                last_used_at REAL NOT NULL
            )
            """
        )
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_knowledge_created_at ON knowledge(created_at DESC)"
        )
        self._conn.commit()

    def close(self) -> None:
        try:
            self._conn.close()
        except Exception:
            pass

    def add(self, question: str, answer: str) -> None:
        now = time.time()
        self._conn.execute(
            "INSERT INTO knowledge(question, answer, created_at, last_used_at) VALUES (?, ?, ?, ?)",
            (question.strip(), answer.strip(), now, now),
        )
        self._conn.commit()

    def has_question(self, question: str) -> bool:
        cur = self._conn.execute(
            "SELECT 1 FROM knowledge WHERE lower(question) = lower(?) LIMIT 1",
            (question.strip(),),
        )
        return cur.fetchone() is not None

    def get_exact_answer(self, question: str) -> str | None:
        cur = self._conn.execute(
            "SELECT answer FROM knowledge WHERE lower(question) = lower(?) LIMIT 1",
            (question.strip(),),
        )
        row = cur.fetchone()
        return str(row[0]) if row else None

    def ensure_seed(self, items: list[tuple[str, str]]) -> int:
        inserted = 0
        for question, answer in items:
            if self.has_question(question):
                continue
            self.add(question, answer)
            inserted += 1
        return inserted

    def touch(self, row_id: int) -> None:
        now = time.time()
        self._conn.execute(
            "UPDATE knowledge SET last_used_at = ? WHERE id = ?",
            (now, row_id),
        )
        self._conn.commit()

    def _tokenize(self, text: str) -> List[str]:
        return [t for t in text.lower().replace("\n", " ").split() if t]

    def _similarity(self, a: str, b: str) -> float:
        ta = set(self._tokenize(a))
        tb = set(self._tokenize(b))
        if not ta or not tb:
            return 0.0
        inter = len(ta & tb)
        union = len(ta | tb)
        return inter / union if union else 0.0

    def search(self, query: str, limit: int = 5, min_score: float = 0.35) -> List[KnowledgeItem]:
        """Busca aproximada por similaridade de tokens.

        É intencionalmente simples, mas funciona bem como memória
        de longo prazo para perguntas repetidas.
        """

        cur = self._conn.execute(
            "SELECT id, question, answer, created_at, last_used_at FROM knowledge ORDER BY created_at DESC LIMIT ?",
            (500,),
        )
        rows: Iterable[Tuple[int, str, str, float, float]] = cur.fetchall()

        scored: List[Tuple[float, KnowledgeItem]] = []
        for rid, q, a, created_at, last_used_at in rows:
            score = self._similarity(query, q)
            if score >= min_score:
                scored.append(
                    (
                        score,
                        KnowledgeItem(
                            id=rid,
                            question=q,
                            answer=a,
                            created_at=created_at,
                            last_used_at=last_used_at,
                        ),
                    )
                )

        scored.sort(key=lambda x: x[0], reverse=True)
        best = [item for _, item in scored[:limit]]
        for item in best:
            self.touch(item.id)
        return best
