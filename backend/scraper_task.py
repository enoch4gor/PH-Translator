from datetime import date
from scraper import ProductHuntScraper
from database import save_products

def run_task():
    try:
        # 爬取数据
        scraper = ProductHuntScraper()
        products = scraper.get_products_with_retry()
        
        if products:
            # 保存到数据库
            save_products(products, date.today())
            print(f"Successfully saved {len(products)} products")
        else:
            print("No products found today")
            
    except Exception as e:
        print(f"Error in task: {e}")

if __name__ == "__main__":
    run_task() 