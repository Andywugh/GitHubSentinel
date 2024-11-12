import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
from logger import LOG

class ProductHuntClient:
    def __init__(self):
        self.url = 'https://www.producthunt.com/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_top_products(self):
        LOG.debug("准备获取Product Hunt的热门产品。")
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            top_products = self.parse_products(response.text)
            return top_products
        except Exception as e:
            LOG.error(f"获取Product Hunt的热门产品失败：{str(e)}")
            return []

    def parse_products(self, html_content):
        LOG.debug("解析Product Hunt的HTML内容。")
        soup = BeautifulSoup(html_content, 'html.parser')
        products = []
        
        # Find all product items with the new class name
        product_items = soup.find_all('div', {'class': 'styles_item__Dk_nz'})
        
        for item in product_items:
            try:
                # Find title and link - now using different class names and structure
                title_link = item.find('a', {'class': 'text-14'})
                if not title_link:
                    continue
                    
                # Extract title - split by em dash and get first part
                title_text = title_link.get_text(strip=True)
                title_parts = title_text.split('—', 1)
                title = title_parts[0].strip()
                
                # Extract description - get second part after em dash if exists
                description = title_parts[1].strip() if len(title_parts) > 1 else ''
                
                # Get link - need to ensure it's a full URL
                link = title_link.get('href')
                if link:
                    if not link.startswith('http'):
                        link = 'https://www.producthunt.com' + link
                        
                products.append({
                    'title': title,
                    'description': description,
                    'link': link
                })
            except Exception as e:
                LOG.warning(f"解析产品信息时出错：{str(e)}")
                continue
        
        LOG.info(f"成功解析 {len(products)} 个Product Hunt产品。")
        return products

    def export_top_products(self, date=None, hour=None):
        LOG.debug("准备导出Product Hunt的热门产品。")
        top_products = self.fetch_top_products()
        
        if not top_products:
            LOG.warning("未找到任何Product Hunt的产品。")
            return None
        
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        if hour is None:
            hour = datetime.now().strftime('%H')

        dir_path = os.path.join('product_hunt', date)
        os.makedirs(dir_path, exist_ok=True)
        
        file_path = os.path.join(dir_path, f'{hour}.md')
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(f"# Product Hunt Top Products ({date} {hour}:00)\n\n")
            for idx, product in enumerate(top_products, start=1):
                file.write(f"{idx}. [{product['title']}]({product['link']})\n")
                if product['description']:
                    file.write(f"   - {product['description']}\n")
                file.write("\n")
        
        LOG.info(f"Product Hunt热门产品文件生成：{file_path}")
        return file_path


if __name__ == "__main__":
    client = ProductHuntClient()
    client.export_top_products() 