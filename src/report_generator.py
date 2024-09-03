# src/report_generator.py

import os
from datetime import date, timedelta
from logger import LOG  # 导入日志模块，用于记录日志信息
from hacker_news_client import HackerNewsClient

class ReportGenerator:
    def __init__(self, llm):
        self.llm = llm  # 初始化时接受一个LLM实例，用于后续生成报告
        self.hn_client = HackerNewsClient()

    def generate_daily_report(self, markdown_file_path):
        # 读取Markdown文件并使用LLM生成日报
        with open(markdown_file_path, 'r') as file:
            markdown_content = file.read()

        report = self.llm.generate_daily_report(markdown_content)  # 调用LLM生成报告

        report_file_path = os.path.splitext(markdown_file_path)[0] + "_report.md"
        with open(report_file_path, 'w+') as report_file:
            report_file.write(report)  # 写入生成的报告

        LOG.info(f"GitHub 项目报告已保存到 {report_file_path}")

        return report, report_file_path


    def generate_report_by_date_range(self, markdown_file_path, days):
        # 生成特定日期范围的报告，流程与日报生成类似
        with open(markdown_file_path, 'r') as file:
            markdown_content = file.read()

        report = self.llm.generate_daily_report(markdown_content)

        report_file_path = os.path.splitext(markdown_file_path)[0] + f"_report.md"
        with open(report_file_path, 'w+') as report_file:
            report_file.write(report)
        
        LOG.info(f"GitHub 项目报告已保存到 {report_file_path}")

        return report, report_file_path


    def generate_hacker_news_trend_report(self):
        stories = self.hn_client.fetch_top_stories()
        if not stories:
            LOG.error("无法获取 Hacker News 热门故事")
            return None, None

        markdown_content = self._format_stories_to_markdown(stories)
        report = self.llm.generate_hacker_news_trend_report(markdown_content)

        report_file_path = f"hacker_news_trend_report_{date.today()}.md"
        with open(report_file_path, 'w+') as report_file:
            report_file.write(report)

        LOG.info(f"Hacker News 趋势报告已保存到 {report_file_path}")
        return report, report_file_path

    def _format_stories_to_markdown(self, stories):
        markdown = "# Hacker News 热门故事\n\n"
        for idx, story in enumerate(stories, start=1):
            markdown += f"{idx}. **{story['title']}**\n"
            markdown += f"   Link: {story['link']}\n"
            markdown += f"   Score: {story['score']}\n\n"
        return markdown

