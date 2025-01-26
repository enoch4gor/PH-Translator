from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
from datetime import datetime
from typing import List
from pydantic import BaseModel
import os
import database as db
from models import init_db

app = FastAPI()

# 更新 CORS 设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源
    allow_credentials=False,  # 改为 False
    allow_methods=["GET", "POST", "OPTIONS"],  # 明确指定允许的方法
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # 缓存预检请求结果1小时
)

# 添加一个中间件来处理 CORS 预检请求
@app.middleware("http")
async def add_cors_headers(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

# 添加错误处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    print(f"Global error handler caught: {str(exc)}")  # 调试日志
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

class Product(BaseModel):
    title: str
    title_cn: str = ""  # 设置默认值
    description: str
    description_cn: str = ""  # 设置默认值
    image_url: str = ""  # 设置默认值
    product_link: str
    categories: str = ""  # 设置默认值
    crawl_date: str

@app.get("/")
async def root():
    return {"message": "Product Hunt Translator API"}

@app.get("/api/products", response_model=List[Product])
async def get_products():
    try:
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(current_dir)
        
        print(f"Current directory: {current_dir}")  # 调试日志
        print(f"Root directory: {root_dir}")  # 调试日志
        
        # 列出所有 CSV 文件
        csv_files = [f for f in os.listdir(root_dir) if f.startswith('products_') and f.endswith('.csv')]
        print(f"Found CSV files: {csv_files}")  # 调试日志
        
        if not csv_files:
            return []  # 返回空列表而不是抛出错误
        
        latest_file = max(csv_files)
        file_path = os.path.join(root_dir, latest_file)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")  # 调试日志
            return []
        
        # 读取 CSV 文件
        df = pd.read_csv(file_path)
        df = df.fillna('')  # 处理空值
        
        # 转换为 JSON 格式
        products = df.to_dict('records')
        print(f"Returning {len(products)} products")  # 调试日志
        
        return products
        
    except Exception as e:
        print(f"Error in get_products: {str(e)}")  # 调试日志
        return []  # 返回空列表而不是抛出错误

@app.get("/api/products/latest")
async def get_latest_crawl_date():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(current_dir)
        csv_files = [f for f in os.listdir(root_dir) if f.startswith('products_') and f.endswith('.csv')]
        
        if not csv_files:
            return {"latest_date": None}
            
        latest_file = max(csv_files)
        date_str = latest_file.replace('products_', '').replace('.csv', '')
        return {"latest_date": date_str}
        
    except Exception as e:
        print(f"Error getting latest date: {str(e)}")  # 调试信息
        raise HTTPException(status_code=500, detail=str(e)) 

@app.get("/api/dates")
async def get_available_dates():
    """获取所有可用的历史数据日期"""
    try:
        dates = db.get_available_dates()
        return {"dates": dates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/{date}")
async def get_products_by_date(date: str):
    """获取指定日期的产品数据"""
    try:
        products = db.get_products_by_date(date)
        if not products:
            raise HTTPException(status_code=404, detail="No data found for this date")
        return products
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 