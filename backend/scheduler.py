import schedule
import time
from datetime import datetime, date
from scraper import ProductHuntScraper
from database import save_products

def daily_task():
    """每日爬取任务"""
    print(f"Starting daily task at {datetime.now()}")
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
        print(f"Error in daily task: {e}")

def run_scheduler():
    """运行定时任务"""
    # 设置每天凌晨2点运行
    schedule.every().day.at("02:00").do(daily_task)
    
    # 立即运行一次
    daily_task()
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    run_scheduler() 