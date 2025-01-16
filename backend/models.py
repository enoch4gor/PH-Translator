from sqlalchemy import create_engine, Column, Integer, String, Date, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    title_cn = Column(String)
    description = Column(String)
    description_cn = Column(String)
    image_url = Column(String)
    product_link = Column(String, nullable=False)
    categories = Column(String)
    rating = Column(Float, default=3.0)
    price = Column(Float)
    original_price = Column(Float)
    crawl_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'title_cn': self.title_cn,
            'description': self.description,
            'description_cn': self.description_cn,
            'image_url': self.image_url,
            'product_link': self.product_link,
            'categories': self.categories,
            'rating': self.rating,
            'price': self.price,
            'original_price': self.original_price,
            'crawl_date': self.crawl_date.strftime('%Y%m%d'),
            'created_at': self.created_at.isoformat()
        }

# 创建数据库连接
engine = create_engine('sqlite:///products.db', echo=True)
SessionLocal = sessionmaker(bind=engine)

# 创建表
def init_db():
    Base.metadata.create_all(engine) 