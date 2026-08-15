"""SQLite database layer with migrations and foreign key support."""
import sqlite3
import logging
from typing import List, Tuple, Optional
from pathlib import Path

from .models import DictionaryEntry, Translation

logger = logging.getLogger(__name__)

DB_VERSION = 2  # Increment when schema changes


class DictionaryDB:
    """Thread-safe SQLite dictionary database with automatic migrations."""

    def __init__(self, db_path: str = "dictionary.db"):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._init_db()

    def _init_db(self):
        self.conn = sqlite3.connect(self.db_path)
        # CRITICAL: Enable foreign keys for ON DELETE CASCADE
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA journal_mode = WAL")
        self._migrate()

    def _migrate(self):
        """Run database migrations safely."""
        c = self.conn.cursor()

        # Create version tracking table
        c.execute("""
            CREATE TABLE IF NOT EXISTS _schema_version (
                version INTEGER PRIMARY KEY
            )
        """)

        c.execute("SELECT version FROM _schema_version LIMIT 1")
        row = c.fetchone()
        current_version = row[0] if row else 0

        if current_version < 1:
            self._migrate_v1(c)
            current_version = 1

        if current_version < 2:
            self._migrate_v2(c)
            current_version = 2

        c.execute(
            "INSERT OR REPLACE INTO _schema_version (version) VALUES (?)",
            (current_version,),
        )
        self.conn.commit()
        logger.info(f"Database at version {current_version}")

    def _migrate_v1(self, c: sqlite3.Cursor):
        """Initial schema."""
        c.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                language_pair TEXT NOT NULL,
                status TEXT DEFAULT 'not_started',
                is_favorite INTEGER DEFAULT 0,
                UNIQUE(word, language_pair)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS translations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id INTEGER NOT NULL,
                part_of_speech TEXT,
                definition TEXT NOT NULL,
                example TEXT,
                FOREIGN KEY(entry_id) REFERENCES entries(id) ON DELETE CASCADE
            )
        """)
        # Performance indexes
        c.execute("CREATE INDEX IF NOT EXISTS idx_entries_word ON entries(word)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_entries_pair ON entries(language_pair)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_entries_status ON entries(status)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_entries_fav ON entries(is_favorite)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_trans_entry ON translations(entry_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_trans_def ON translations(definition)")
        logger.info("Migration v1 applied")

    def _migrate_v2(self, c: sqlite3.Cursor):
        """Add missing columns for backward compatibility."""
        try:
            c.execute('ALTER TABLE entries ADD COLUMN status TEXT DEFAULT "not_started"')
        except sqlite3.OperationalError:
            pass
        try:
            c.execute("ALTER TABLE entries ADD COLUMN is_favorite INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        logger.info("Migration v2 applied")

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    # --- Entry CRUD ---

    def add_entry(self, entry: DictionaryEntry) -> Tuple[bool, str]:
        c = self.conn.cursor()
        c.execute(
            "SELECT id FROM entries WHERE word=? AND language_pair=?",
            (entry.word, entry.language_pair),
        )
        if c.fetchone():
            return False, "Bu kelime zaten sözlükte mevcut."
        try:
            c.execute(
                """
                INSERT INTO entries (word, language_pair, status, is_favorite)
                VALUES (?, ?, ?, ?)
                """,
                (entry.word, entry.language_pair, entry.status, 1 if entry.is_favorite else 0),
            )
            entry_id = c.lastrowid
            for trans in entry.translations:
                c.execute(
                    """
                    INSERT INTO translations (entry_id, part_of_speech, definition, example)
                    VALUES (?, ?, ?, ?)
                    """,
                    (entry_id, trans.part_of_speech, trans.definition, trans.example),
                )
            self.conn.commit()
            return True, "Eklendi."
        except sqlite3.IntegrityError:
            return False, "Veritabanı hatası."

    def update_entry(self, entry: DictionaryEntry) -> bool:
        c = self.conn.cursor()
        c.execute(
            "SELECT id FROM entries WHERE word=? AND language_pair=?",
            (entry.word, entry.language_pair),
        )
        row = c.fetchone()
        if not row:
            return False
        entry_id = row[0]
        c.execute(
            "UPDATE entries SET status=?, is_favorite=? WHERE id=?",
            (entry.status, 1 if entry.is_favorite else 0, entry_id),
        )
        c.execute("DELETE FROM translations WHERE entry_id=?", (entry_id,))
        for trans in entry.translations:
            c.execute(
                """
                INSERT INTO translations (entry_id, part_of_speech, definition, example)
                VALUES (?, ?, ?, ?)
                """,
                (entry_id, trans.part_of_speech, trans.definition, trans.example),
            )
        self.conn.commit()
        return True

    def delete_entry(self, word: str, language_pair: str) -> bool:
        c = self.conn.cursor()
        c.execute("DELETE FROM entries WHERE word=? AND language_pair=?", (word, language_pair))
        self.conn.commit()
        return c.rowcount > 0

    # --- Queries ---

    def get_all_entries(self) -> List[DictionaryEntry]:
        c = self.conn.cursor()
        c.execute("SELECT id, word, language_pair, status, is_favorite FROM entries ORDER BY word")
        return self._fetch_entries(c)

    def search_entries(self, query: str) -> List[DictionaryEntry]:
        c = self.conn.cursor()
        pattern = f"%{query}%"
        c.execute(
            """
            SELECT DISTINCT e.id, e.word, e.language_pair, e.status, e.is_favorite
            FROM entries e
            LEFT JOIN translations t ON e.id = t.entry_id
            WHERE e.word LIKE ? COLLATE NOCASE
               OR t.definition LIKE ? COLLATE NOCASE
               OR t.example LIKE ? COLLATE NOCASE
            ORDER BY e.word
            """,
            (pattern, pattern, pattern),
        )
        return self._fetch_entries(c)

    def get_entries_by_status(self, status: str) -> List[DictionaryEntry]:
        c = self.conn.cursor()
        c.execute(
            "SELECT id, word, language_pair, status, is_favorite FROM entries WHERE status=? ORDER BY word",
            (status,),
        )
        return self._fetch_entries(c)

    def get_favorite_entries(self) -> List[DictionaryEntry]:
        c = self.conn.cursor()
        c.execute(
            "SELECT id, word, language_pair, status, is_favorite FROM entries WHERE is_favorite=1 ORDER BY word"
        )
        return self._fetch_entries(c)

    def _fetch_entries(self, c: sqlite3.Cursor) -> List[DictionaryEntry]:
        entries = []
        for row in c.fetchall():
            entry_id, word, pair, status, is_fav = row
            c2 = self.conn.cursor()
            c2.execute(
                "SELECT part_of_speech, definition, example FROM translations WHERE entry_id=?",
                (entry_id,),
            )
            translations = [
                Translation(pos, definition, example)
                for pos, definition, example in c2.fetchall()
            ]
            entries.append(DictionaryEntry(word, pair, translations, status or "not_started", bool(is_fav)))
        return entries

    def get_all_tags(self) -> List[str]:
        c = self.conn.cursor()
        c.execute("SELECT DISTINCT part_of_speech FROM translations WHERE part_of_speech IS NOT NULL")
        return [row[0] for row in c.fetchall() if row[0]]

    def get_stats(self) -> dict:
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*), SUM(is_favorite) FROM entries")
        total, fav = c.fetchone()
        c.execute("SELECT status, COUNT(*) FROM entries GROUP BY status")
        status_counts = {row[0]: row[1] for row in c.fetchall()}
        return {
            "total": total or 0,
            "favorites": fav or 0,
            "learned": status_counts.get("learned", 0),
            "learning": status_counts.get("learning", 0),
            "not_started": status_counts.get("not_started", 0),
        }

    def clear_all(self):
        c = self.conn.cursor()
        c.execute("DELETE FROM translations")
        c.execute("DELETE FROM entries")
        self.conn.commit()

    def import_entries(self, entries: List[DictionaryEntry]) -> Tuple[int, int]:
        added = 0
        skipped = 0
        for entry in entries:
            c = self.conn.cursor()
            c.execute(
                "SELECT id FROM entries WHERE word=? AND language_pair=?",
                (entry.word, entry.language_pair),
            )
            if c.fetchone():
                skipped += 1
                continue
            c.execute(
                """
                INSERT INTO entries (word, language_pair, status, is_favorite)
                VALUES (?, ?, ?, ?)
                """,
                (entry.word, entry.language_pair, entry.status, 1 if entry.is_favorite else 0),
            )
            entry_id = c.lastrowid
            for trans in entry.translations:
                c.execute(
                    """
                    INSERT INTO translations (entry_id, part_of_speech, definition, example)
                    VALUES (?, ?, ?, ?)
                    """,
                    (entry_id, trans.part_of_speech, trans.definition, trans.example),
                )
            added += 1
        self.conn.commit()
        return added, skipped
