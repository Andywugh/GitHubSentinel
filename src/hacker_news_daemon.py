import time
import schedule
from report_generator import ReportGenerator
from llm import LLM
from logger import LOG

class HackerNewsDaemon:
    def __init__(self):
        self.llm = LLM()
        self.report_generator = ReportGenerator(self.llm)

    def run(self):
        LOG.info("Hacker News Daemon started")
        schedule.every().day.at("00:00").do(self.generate_daily_trend_report)
        
        while True:
            schedule.run_pending()
            time.sleep(60)

    def generate_daily_trend_report(self):
        LOG.info("Generating daily Hacker News trend report")
        self.report_generator.generate_hacker_news_trend_report()

if __name__ == "__main__":
    daemon = HackerNewsDaemon()
    daemon.run()
