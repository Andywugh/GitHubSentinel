import requests
from bs4 import BeautifulSoup
from logger import LOG

class HackerNewsClient:
    def __init__(self):
        self.base_url = 'https://news.ycombinator.com/'

    def fetch_top_stories(self, limit=30):
        try:
            response = requests.get(self.base_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            stories = soup.find_all('tr', class_='athing', limit=limit)

            top_stories = []
            for story in stories:
                title_tag = story.find('span', class_='titleline').find('a')
                if title_tag:
                    title = title_tag.text
                    link = title_tag['href']
                    score_tag = story.find_next_sibling('tr').find('span', class_='score')
                    score = score_tag.text if score_tag else '0 points'
                    top_stories.append({'title': title, 'link': link, 'score': score})

            return top_stories
        except Exception as e:
            LOG.error(f"获取 Hacker News 热门故事时发生错误：{e}")
            return []
