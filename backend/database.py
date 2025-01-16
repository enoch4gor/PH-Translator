from contextlib import contextmanager
from datetime import datetime, date
from typing import List, Optional
from sqlalchemy.orm import Session
from models import SessionLocal, Product

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_products(products: List[dict], crawl_date: date = None):
    """保存产品数据到数据库"""
    if crawl_date is None:
        crawl_date = date.today()
        
    with get_db() as db:
        for product_data in products:
            product = Product(
                title=product_data['title'],
                title_cn=product_data.get('title_cn', ''),
                description=product_data['description'],
                description_cn=product_data.get('description_cn', ''),
                image_url=product_data.get('image_url', ''),
                product_link=product_data['product_link'],
                categories=product_data.get('categories', ''),
                rating=float(product_data.get('rating', 3.0)),
                price=float(product_data.get('price', 0.0)),
                original_price=float(product_data.get('original_price', 0.0)),
                crawl_date=crawl_date
            )
            db.add(product)
        db.commit()

def get_products_by_date(date_str: str) -> List[dict]:
    """获取指定日期的产品数据"""
    try:
        query_date = datetime.strptime(date_str, '%Y%m%d').date()
    except ValueError:
        return []
        
    with get_db() as db:
        products = db.query(Product).filter(
            Product.crawl_date == query_date
        ).all()
        return [p.to_dict() for p in products]

def get_available_dates() -> List[str]:
    """获取所有可用的日期"""
    with get_db() as db:
        dates = db.query(Product.crawl_date).distinct().all()
        return [d[0].strftime('%Y%m%d') for d in dates] 