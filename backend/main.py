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
    allow_origins=["http://localhost:3000"],  # 明确指定允许的源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        
        # 调试信息
        print(f"Current directory: {current_dir}")
        print(f"Root directory: {root_dir}")
        
        # 列出所有 CSV 文件
        csv_files = [f for f in os.listdir(root_dir) if f.startswith('products_') and f.endswith('.csv')]
        print(f"Found CSV files: {csv_files}")  # 调试信息
        
        if not csv_files:
            raise HTTPException(status_code=404, detail="No product data found")
        
        latest_file = max(csv_files)
        file_path = os.path.join(root_dir, latest_file)
        print(f"Reading file: {file_path}")  # 调试信息
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
            
        # 检查文件权限
        if not os.access(file_path, os.R_OK):
            raise HTTPException(status_code=500, detail=f"Cannot read file: {file_path}")
        
        # 读取 CSV 文件
        df = pd.read_csv(file_path)
        print(f"CSV columns: {df.columns.tolist()}")  # 调试信息
        
        # 处理 NaN 值
        df = df.fillna('')  # 将所有 NaN 值替换为空字符串
        
        # 确保所有必需的列都存在
        required_columns = ['title', 'description', 'product_link']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=500,
                detail=f"Missing required columns: {missing_columns}"
            )
        
        # 为可选列设置默认值
        optional_columns = {
            'title_cn': '',
            'description_cn': '',
            'image_url': '',
            'categories': '',
            'crawl_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        for col, default_value in optional_columns.items():
            if col not in df.columns:
                df[col] = default_value
        
        # 确保所有字符串列中的 NaN 值被替换为空字符串
        string_columns = ['title', 'title_cn', 'description', 'description_cn', 
                         'image_url', 'product_link', 'categories', 'crawl_date']
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].fillna('')
        
        # 转换为 JSON 格式
        products = df.to_dict('records')
        print(f"Returning {len(products)} products")  # 调试信息
        
        return products
        
    except Exception as e:
        print(f"Error in get_products: {str(e)}")  # 调试信息
        raise HTTPException(status_code=500, detail=str(e))

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