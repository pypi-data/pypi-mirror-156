from calendar import WEDNESDAY
import datetime as datetime
import sqlalchemy.orm as orm
import bigfastapi.db.database as database
import bigfastapi.schemas.users_schemas as schema
import bigfastapi.schemas.product_schemas as product_schema
from fastapi import Depends
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, Text, Float, BOOLEAN, Integer
from sqlalchemy import ForeignKey, Integer, desc
from uuid import uuid4
from operator import and_, or_


class Product(database.Base):
    __tablename__ = 'products'
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    name = Column(String(255), index=True, nullable=False)
    description = Column(Text, index=True, nullable=True)
    organization_id = Column(String(255), ForeignKey("businesses.id", ondelete="CASCADE"))
    created_by = Column(String(255), ForeignKey("users.id"))
    unique_id = Column(String(255), index=True, nullable=False)
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)
    is_deleted = Column(BOOLEAN, default=False)

#==============================Database Services=============================#
def fetch_product(product_id: str, organization_id: str, db: orm.Session):
    product = db.query(Product).filter(Product.organization_id == organization_id, Product.id == product_id, Product.is_deleted==False).first()
    return product

def fetch_product_by_id(id: str, db: orm.Session):
    return db.query(Product).filter(Product.id == id, Product.is_deleted==False).first()

async def fetch_products(
    organization_id: str,
    offset: int, size: int = 50,
    timestamp: datetime.datetime = None,
    db: orm.Session = Depends(database.get_db)
    ):
    if timestamp:
        total_items = db.query(Product).filter(Product.organization_id == organization_id).filter(
                Product.is_deleted == False, Product.last_updated > timestamp).count()

        products = db.query(Product).filter(
            Product.organization_id == organization_id).filter(
            Product.is_deleted == False, Product.last_updated > timestamp).order_by(Product.date_created.desc()
            ).offset(offset=offset).limit(limit=size).all()
    else:
        total_items = db.query(Product).filter(Product.organization_id == organization_id).filter(
                Product.is_deleted == False).count()

        products = db.query(Product).filter(
            Product.organization_id == organization_id).filter(
            Product.is_deleted == False).order_by(Product.date_created.desc()
            ).offset(offset=offset).limit(limit=size).all()

    return products, total_items

async def fetch_sorted_products(
    organization_id:str,
    sort_key: str,
    offset: int, size:int=50,
    sort_dir: str = "asc",
    db: orm.Session = Depends(database.get_db)
    ):  
    if sort_dir == "desc":
        products = db.query(Product).filter(
            Product.organization_id == organization_id).filter(
            Product.is_deleted == False).order_by(
            desc(getattr(Product, sort_key, "name"))
            ).offset(offset=offset).limit(limit=size).all()
    else:
        products = db.query(Product).filter(
            Product.organization_id == organization_id).filter(
            Product.is_deleted == False).order_by(
            getattr(Product, sort_key, "name")
            ).offset(offset=offset).limit(limit=size).all()

    total_items = db.query(Product).filter(Product.organization_id == organization_id).filter(
            Product.is_deleted == False).count()

    return products, total_items

async def search_products(
    organization_id:str,
    search_value: str,
    offset: int, size:int=50,
    db: orm.Session = Depends(database.get_db)
    ):  
    search_text = f"%{search_value}%"
    total_items =db.query(Product).filter(and_(
        Product.organization_id == organization_id,
        Product.is_deleted == False)).filter(or_(Product.name.like(search_text),
        Product.description.like(search_text))).count()

    results = db.query(Product).filter(and_(
        Product.organization_id == organization_id,
        Product.is_deleted == False)).filter(or_(Product.name.like(search_text),
        Product.description.like(search_text))).order_by(
        Product.date_created.desc()).offset(
        offset=offset).limit(limit=size).all()
    
    return results, total_items

