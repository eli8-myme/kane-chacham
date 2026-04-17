"""
Database layer - SQLite
מאגר מוצרים + מחירים מקומי
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, List, Dict

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "products.db")


class Database:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self._init_db()

    def _conn(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._conn() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS products (
                    barcode      TEXT PRIMARY KEY,
                    name         TEXT NOT NULL,
                    brand        TEXT,
                    size         TEXT,
                    size_unit    TEXT,
                    size_value   REAL,
                    category     TEXT,
                    image_url    TEXT,
                    updated_at   TEXT
                );

                CREATE TABLE IF NOT EXISTS prices (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    barcode      TEXT,
                    store_name   TEXT NOT NULL,
                    store_chain  TEXT,
                    branch_id    TEXT,
                    price        REAL NOT NULL,
                    price_per_unit REAL,
                    size         TEXT,
                    size_value   REAL,
                    size_unit    TEXT,
                    updated_at   TEXT,
                    UNIQUE(barcode, store_chain, branch_id, size)
                );

                CREATE INDEX IF NOT EXISTS idx_prices_barcode ON prices(barcode);
                CREATE INDEX IF NOT EXISTS idx_products_name   ON products(name);
            """)

    # ===== PRODUCTS =====

    def get_product_by_barcode(self, barcode: str) -> Optional[Dict]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM products WHERE barcode = ?", (barcode,)
            ).fetchone()
            return dict(row) if row else None

    def search_product_by_name(self, name: str) -> Optional[Dict]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM products WHERE name LIKE ? LIMIT 1",
                (f"%{name}%",)
            ).fetchone()
            return dict(row) if row else None

    def save_product(self, product: Dict):
        with self._conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO products
                  (barcode, name, brand, size, category, image_url, updated_at)
                VALUES (?,?,?,?,?,?,?)
            """, (
                product.get("barcode"),
                product.get("name", ""),
                product.get("brand", ""),
                product.get("size", ""),
                product.get("category", ""),
                product.get("image_url", ""),
                datetime.utcnow().isoformat(),
            ))

    def count_products(self) -> int:
        with self._conn() as conn:
            return conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]

    # ===== PRICES =====

    def get_prices(self, barcode: str) -> List[Dict]:
        with self._conn() as conn:
            rows = conn.execute("""
                SELECT * FROM prices
                WHERE barcode = ?
                  AND updated_at >= datetime('now', '-7 days')
                ORDER BY price ASC
            """, (barcode,)).fetchall()
            return [dict(r) for r in rows]

    def save_prices(self, prices: List[Dict]):
        with self._conn() as conn:
            for p in prices:
                conn.execute("""
                    INSERT OR REPLACE INTO prices
                      (barcode, store_name, store_chain, branch_id, price,
                       price_per_unit, size, size_value, size_unit, updated_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?)
                """, (
                    p.get("barcode"),
                    p.get("store_name"),
                    p.get("store_chain"),
                    p.get("branch_id", ""),
                    p.get("price"),
                    p.get("price_per_unit"),
                    p.get("size"),
                    p.get("size_value"),
                    p.get("size_unit"),
                    datetime.utcnow().isoformat(),
                ))

    def get_prices_by_name(self, name: str) -> List[Dict]:
        """חיפוש מחירים לפי שם מוצר (למקרה שאין ברקוד)"""
        with self._conn() as conn:
            rows = conn.execute("""
                SELECT pr.* FROM prices pr
                JOIN products pd ON pr.barcode = pd.barcode
                WHERE pd.name LIKE ?
                ORDER BY pr.price_per_unit ASC
                LIMIT 20
            """, (f"%{name}%",)).fetchall()
            return [dict(r) for r in rows]

    # ===== BULK IMPORT (from Israeli XML files) =====

    def bulk_import_prices(self, prices: List[Dict]):
        """יבוא מסיבי מקבצי XML של הרשתות"""
        with self._conn() as conn:
            conn.executemany("""
                INSERT OR REPLACE INTO prices
                  (barcode, store_name, store_chain, branch_id, price,
                   price_per_unit, size, size_value, size_unit, updated_at)
                VALUES (:barcode,:store_name,:store_chain,:branch_id,:price,
                        :price_per_unit,:size,:size_value,:size_unit,:updated_at)
            """, prices)


db = Database()
