from requests_html import HTMLSession
import pandas as pd
from datetime import datetime
import time
from translator import ProductTranslator
import os
from config import OPENAI_API_KEY

class ProductHuntScraper:
    def __init__(self):
        self.session = HTMLSession()
        self.base_url = "https://www.producthunt.com/"
        
    def get_products(self):
        try:
            print("Starting to scrape Product Hunt...")
            r = self.session.get(self.base_url)
            print("Page accessed successfully")
            
            print("Starting JavaScript render...")
            r.html.render(timeout=30, sleep=5)
            print("JavaScript render completed")
            
            products = []
            sections = r.html.find('section')
            
            for section in sections:
                try:
                    text = section.text
                    if not text:
                        continue
                        
                    lines = text.split('\n')
                    if not lines:
                        continue
                        
                    first_line = lines[0].strip()
                    if not (first_line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.'))):
                        continue
                        
                    # 提取产品信息
                    title = first_line.split('. ', 1)[1] if '. ' in first_line else first_line
                    description = lines[1] if len(lines) > 1 else ''
                    
                    # 修复产品链接格式
                    link = section.find('a', first=True)
                    if link and 'href' in link.attrs:
                        # 从标题生成 URL 友好的 slug
                        slug = title.lower().replace(' ', '-')
                        product_link = f"https://www.producthunt.com/posts/{slug}"
                    else:
                        product_link = ''
                    
                    # 获取图片 - 尝试不同的选择器
                    img = None
                    # 首先尝试找到主图片
                    img = section.find('img[alt*="' + title + '"]', first=True)
                    if not img:
                        # 尝试找到任何图片
                        img = section.find('img[loading="lazy"]', first=True)
                    if not img:
                        # 最后尝试任何图片
                        img = section.find('img', first=True)
                    
                    image_url = img.attrs.get('src', '') if img else ''
                    # 确保图片 URL 是完整的
                    if image_url and not image_url.startswith('http'):
                        image_url = 'https:' + image_url if image_url.startswith('//') else 'https://' + image_url
                    
                    # 获取分类标签
                    categories = lines[2] if len(lines) > 2 else ''
                    
                    products.append({
                        'title': title,
                        'description': description,
                        'categories': categories,
                        'product_link': product_link,
                        'image_url': image_url,
                        'crawl_date': datetime.now().strftime('%Y-%m-%d')
                    })
                    
                    print(f"Found product: {title}")
                    print(f"Link: {product_link}")
                    print(f"Image: {image_url}")
                    
                    if len(products) >= 10:
                        break
                        
                except Exception as e:
                    print(f"Error processing section: {str(e)}")
                    continue
            
            print(f"\nTotal products found: {len(products)}")
            return products
            
        except Exception as e:
            print(f"Error scraping Product Hunt: {str(e)}")
            print("Full error details:", e)
            return []
    
    def get_products_with_retry(self, max_retries=3):
        for attempt in range(max_retries):
            print(f"\nAttempt {attempt + 1} of {max_retries}")
            try:
                products = self.get_products()
                if products:
                    return products
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                time.sleep(5 * (attempt + 1))
        return []
    
    def save_to_csv(self, products):
        if products:
            # 使用 config 中的 API key
            if not OPENAI_API_KEY:
                print("Error: OPENAI_API_KEY not found in config")
                return
                
            translator = ProductTranslator(OPENAI_API_KEY)
            
            # 翻译产品信息
            print("\nStarting translation...")
            translated_products = translator.translate_products_sync(products)
            
            # 验证翻译结果
            for product in translated_products:
                if 'title_cn' not in product or 'description_cn' not in product:
                    print(f"Warning: Missing translation for product {product['title']}")
            
            # 保存到CSV
            df = pd.DataFrame(translated_products)
            
            # 确保所有列都存在
            expected_columns = ['title', 'title_cn', 'description', 'description_cn', 
                              'categories', 'product_link', 'image_url', 'crawl_date']
            for col in expected_columns:
                if col not in df.columns:
                    print(f"Warning: Missing column {col}")
                    df[col] = ''
            
            filename = f"products_{datetime.now().strftime('%Y%m%d')}.csv"
            df.to_csv(filename, index=False, encoding='utf-8')
            print(f"\nSaved {len(translated_products)} products to {filename}")
            print("\nColumns in CSV:", df.columns.tolist())
            
            # 打印预览
            print("\nSaved products preview:")
            for i, product in enumerate(translated_products, 1):
                print(f"\n{i}. {product['title']}")
                print(f"标题(中文): {product.get('title_cn', 'Translation missing')}")
                print(f"Description: {product['description']}")
                print(f"描述(中文): {product.get('description_cn', 'Translation missing')}")
                print(f"Categories: {product['categories']}")
                print(f"Link: {product['product_link']}")
                print(f"Image: {product['image_url']}")
        else:
            print("No products to save")

def main():
    scraper = ProductHuntScraper()
    products = scraper.get_products_with_retry()
    scraper.save_to_csv(products)

if __name__ == "__main__":
    main() 