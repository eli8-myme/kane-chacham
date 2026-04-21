"""
Database layer - PostgreSQL with SQLAlchemy
מאגר מוצרים + מחירים עם תמיכה ב-Postgres
"""
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from sqlalchemy import create_engine, Column, String, Float, Integer, Text, Index
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import IntegrityError

# קריאת DATABASE_URL מסביבה
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/products.db")

# Render מחזיר URL שמתחיל ב-postgres:// אבל SQLAlchemy דורש postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# הגדרות חיבור
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=300,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ===== MODELS =====

class Product(Base):
    __tablename__ = "products"
    
    barcode = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    brand = Column(String)
    size = Column(String)
    size_unit = Column(String)
    size_value = Column(Float)
    category = Column(String)
    image_url = Column(Text)
    updated_at = Column(String)
    
    __table_args__ = (
        Index('idx_products_name', 'name'),
    )


class Price(Base):
    __tablename__ = "prices"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    barcode = Column(String)
    store_name = Column(String, nullable=False)
    store_chain = Column(String)
    branch_id = Column(String)
    price = Column(Float, nullable=False)
    price_per_unit = Column(Float)
    size = Column(String)
    size_value = Column(Float)
    size_unit = Column(String)
    updated_at = Column(String)
    
    __table_args__ = (
        Index('idx_prices_barcode', 'barcode'),
    )


# ===== DATABASE CLASS =====

class Database:
    def __init__(self):
        # יצירת טבלאות אם לא קיימות
        Base.metadata.create_all(bind=engine)
    
    def _get_session(self):
        return SessionLocal()
    
    # ===== PRODUCTS =====
    
    def get_product_by_barcode(self, barcode: str) -> Optional[Dict]:
        session = self._get_session()
        try:
            product = session.query(Product).filter(Product.barcode == barcode).first()
            if product:
                return {
                    "barcode": product.barcode,
                    "name": product.name,
                    "brand": product.brand,
                    "size": product.size,
                    "category": product.category,
                    "image_url": product.image_url,
                }
            return None
        finally:
            session.close()
    
    def search_product_by_name(self, name: str) -> Optional[Dict]:
        session = self._get_session()
        try:
            product = session.query(Product).filter(
                Product.name.ilike(f"%{name}%")
            ).first()
            if product:
                return {
                    "barcode": product.barcode,
                    "name": product.name,
                    "brand": product.brand,
                    "size": product.size,
                    "category": product.category,
                    "image_url": product.image_url,
                }
            return None
        finally:
            session.close()
    
    def save_product(self, product: Dict):
        session = self._get_session()
        try:
            db_product = session.query(Product).filter(
                Product.barcode == product.get("barcode")
            ).first()
            
            if db_product:
                # עדכון
                db_product.name = product.get("name", "")
                db_product.brand = product.get("brand", "")
                db_product.size = product.get("size", "")
                db_product.category = product.get("category", "")
                db_product.image_url = product.get("image_url", "")
                db_product.updated_at = datetime.utcnow().isoformat()
            else:
                # יצירה חדשה
                db_product = Product(
                    barcode=product.get("barcode"),
                    name=product.get("name", ""),
                    brand=product.get("brand", ""),
                    size=product.get("size", ""),
                    category=product.get("category", ""),
                    image_url=product.get("image_url", ""),
                    updated_at=datetime.utcnow().isoformat(),
                )
                session.add(db_product)
            
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def count_products(self) -> int:
        session = self._get_session()
        try:
            return session.query(Product).count()
        finally:
            session.close()
    
    # ===== PRICES =====
    
    def get_prices(self, barcode: str) -> List[Dict]:
        session = self._get_session()
        try:
            cutoff = (datetime.utcnow() - timedelta(days=1)).isoformat()
            prices = session.query(Price).filter(
                Price.barcode == barcode,
                Price.updated_at >= cutoff
            ).order_by(Price.price_per_unit).all()
            
            return [{
                "barcode": p.barcode,
                "store_name": p.store_name,
                "store_chain": p.store_chain,
                "branch_id": p.branch_id,
                "price": p.price,
                "price_per_unit": p.price_per_unit,
                "size": p.size,
            } for p in prices]
        finally:
            session.close()
    
    def save_prices(self, prices: List[Dict]):
        session = self._get_session()
        try:
            for p in prices:
                price = Price(
                    barcode=p.get("barcode"),
                    store_name=p.get("store_name"),
                    store_chain=p.get("store_chain"),
                    branch_id=p.get("branch_id", ""),
                    price=p.get("price"),
                    price_per_unit=p.get("price_per_unit"),
                    size=p.get("size"),
                    size_value=p.get("size_value"),
                    size_unit=p.get("size_unit"),
                    updated_at=datetime.utcnow().isoformat(),
                )
                session.add(price)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_prices_by_name(self, name: str) -> List[Dict]:
        session = self._get_session()
        try:
            prices = session.query(Price).join(
                Product, Price.barcode == Product.barcode
            ).filter(
                Product.name.ilike(f"%{name}%")
            ).order_by(Price.price_per_unit).limit(20).all()
            
            return [{
                "barcode": p.barcode,
                "store_name": p.store_name,
                "price": p.price,
                "price_per_unit": p.price_per_unit,
            } for p in prices]
        finally:
            session.close()
    
    def bulk_import_prices(self, prices: List[Dict]):
        """יבוא מסיבי מקבצי XML"""
        session = self._get_session()
        try:
            for p in prices:
                price = Price(
                    barcode=p.get("barcode"),
                    store_name=p.get("store_name"),
                    store_chain=p.get("store_chain"),
                    branch_id=p.get("branch_id", ""),
                    price=p.get("price"),
                    price_per_unit=p.get("price_per_unit"),
                    size=p.get("size"),
                    size_value=p.get("size_value"),
                    size_unit=p.get("size_unit"),
                    updated_at=p.get("updated_at", datetime.utcnow().isoformat()),
                )
                session.add(price)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


# אובייקט גלובלי
db = Database()


# פונקציה לשימוש ב-FastAPI dependency injection
def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
