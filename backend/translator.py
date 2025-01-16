import openai
from typing import Dict, List
import json
import os
from datetime import datetime
import time
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()  # 加载 .env 文件

class ProductTranslator:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)  # 使用异步客户端
        self.cache_file = 'translation_cache.json'
        self.load_cache()
        self.max_retries = 3
        self.retry_delay = 1
        
    def load_cache(self):
        """加载翻译缓存"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
            else:
                self.cache = {}
        except Exception as e:
            print(f"Error loading cache: {e}")
            self.cache = {}
            
    def save_cache(self):
        """保存翻译缓存"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")
            
    async def get_translation(self, text: str) -> str:
        """获取文本翻译，优先使用缓存"""
        if not text:
            return ""
            
        print(f"\nTranslating text: {text}")
            
        # 检查缓存
        if text in self.cache:
            print(f"Cache hit for: {text[:30]}...")
            return self.cache[text]
            
        for attempt in range(self.max_retries):
            try:
                print(f"Calling OpenAI API (attempt {attempt + 1}/{self.max_retries})...")
                
                response = await self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": """You are a professional translator specializing in technical and product content. 
                         Translate the following English text to Chinese (Simplified).
                         Requirements:
                         1. Keep technical terms accurate
                         2. Maintain a natural and professional tone
                         3. Preserve any brand names or product names in their original form
                         4. Add appropriate Chinese punctuation
                         """},
                        {"role": "user", "content": text}
                    ],
                    temperature=0.3,
                    presence_penalty=0,
                    frequency_penalty=0
                )
                
                translation = response.choices[0].message.content.strip()
                print(f"Received translation: {translation}")
                
                # 保存到缓存
                self.cache[text] = translation
                self.save_cache()
                
                return translation
                
            except Exception as e:
                print(f"Translation error (attempt {attempt + 1}): {str(e)}")
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (attempt + 1)
                    print(f"Waiting {wait_time} seconds before retrying...")
                    await asyncio.sleep(wait_time)
                else:
                    print("Max retries reached, returning original text")
                    return text
            
    async def translate_product(self, product: Dict) -> Dict:
        """翻译产品信息"""
        translated_product = product.copy()
        
        print(f"\nTranslating product: {product['title']}")
        
        # 并行翻译标题和描述
        title_task = self.get_translation(product['title'])
        desc_task = self.get_translation(product['description'])
        
        # 等待所有翻译完成
        translated_product['title_cn'], translated_product['description_cn'] = await asyncio.gather(
            title_task, desc_task
        )
        
        print(f"Title translated: {translated_product['title_cn']}")
        print(f"Description translated: {translated_product['description_cn']}")
        
        return translated_product
        
    async def translate_products(self, products: List[Dict]) -> List[Dict]:
        """批量翻译产品信息"""
        # 并行翻译所有产品
        tasks = [self.translate_product(product) for product in products]
        return await asyncio.gather(*tasks)
    
    def translate_products_sync(self, products: List[Dict]) -> List[Dict]:
        """同步版本的批量翻译（用于兼容现有代码）"""
        return asyncio.run(self.translate_products(products)) 