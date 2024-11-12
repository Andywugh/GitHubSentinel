import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# 添加 src 目录到模块搜索路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from product_hunt_client import ProductHuntClient

class TestProductHuntClient(unittest.TestCase):
    def setUp(self):
        """在每个测试方法之前运行，初始化测试环境"""
        self.client = ProductHuntClient()
        
        # 模拟的 HTML 响应内容
        self.mock_html = '''
        <div class="styles_item__Dk_nz">
            <a href="/posts/test-product" class="text-14">
                Test Product — A great testing tool
            </a>
        </div>
        <div class="styles_item__Dk_nz">
            <a href="/posts/another-product" class="text-14">
                Another Product — Amazing product description
            </a>
        </div>
        '''

    @patch('product_hunt_client.requests.get')
    def test_fetch_top_products_success(self, mock_get):
        """测试成功获取热门产品列表"""
        # 设置模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = self.mock_html
        mock_get.return_value = mock_response
        
        # 调用方法并验证结果
        products = self.client.fetch_top_products()
        
        self.assertEqual(len(products), 2)
        self.assertEqual(products[0]['title'], 'Test Product')
        self.assertEqual(products[0]['description'], 'A great testing tool')
        self.assertEqual(products[0]['link'], 'https://www.producthunt.com/posts/test-product')

    @patch('product_hunt_client.requests.get')
    def test_fetch_top_products_failure(self, mock_get):
        """测试获取热门产品失败的情况"""
        # 模拟请求失败
        mock_get.side_effect = Exception("Connection error")
        
        # 调用方法并验证结果
        products = self.client.fetch_top_products()
        self.assertEqual(products, [])

    def test_parse_products_success(self):
        """测试成功解析产品信息"""
        products = self.client.parse_products(self.mock_html)
        
        self.assertEqual(len(products), 2)
        self.assertEqual(products[1]['title'], 'Another Product')
        self.assertEqual(products[1]['description'], 'Amazing product description')
        self.assertEqual(products[1]['link'], 'https://www.producthunt.com/posts/another-product')

    def test_parse_products_empty_html(self):
        """测试解析空HTML内容"""
        products = self.client.parse_products("")
        self.assertEqual(products, [])

    @patch('product_hunt_client.requests.get')
    @patch('product_hunt_client.os.makedirs')
    @patch('product_hunt_client.open', new_callable=unittest.mock.mock_open)
    def test_export_top_products(self, mock_open, mock_makedirs, mock_get):
        """测试导出热门产品到文件"""
        # 设置模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = self.mock_html
        mock_get.return_value = mock_response
        
        # 调用导出方法
        file_path = self.client.export_top_products(date="2024-11-12", hour="22")
        
        # 验证目录创建
        mock_makedirs.assert_called_once_with('product_hunt/2024-11-12', exist_ok=True)
        
        # 验证文件创建和写入
        mock_open.assert_called_once_with('product_hunt/2024-11-12/22.md', 'w', encoding='utf-8')
        
        # 验证文件内容写入
        mock_open().write.assert_any_call("# Product Hunt Top Products (2024-11-12 22:00)\n\n")
        mock_open().write.assert_any_call("1. [Test Product](https://www.producthunt.com/posts/test-product)\n")
        mock_open().write.assert_any_call("   - A great testing tool\n")

    @patch('product_hunt_client.requests.get')
    def test_export_top_products_no_products(self, mock_get):
        """测试当没有产品时的导出行为"""
        # 模拟空响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html></html>"
        mock_get.return_value = mock_response
        
        # 调用方法并验证结果
        file_path = self.client.export_top_products()
        self.assertIsNone(file_path)

    def test_parse_products_invalid_html(self):
        """测试解析无效的HTML内容"""
        invalid_html = '''
        <div class="wrong-class">
            <a href="/posts/test">Invalid Structure</a>
        </div>
        '''
        products = self.client.parse_products(invalid_html)
        self.assertEqual(products, [])

if __name__ == '__main__':
    unittest.main() 