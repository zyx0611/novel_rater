import allure
import pytest
import chardet
from pages import novel_script

import re


def split_by_chapter(text):
    chapter_pattern = r"(第[一二三四五六七八九十百千万\d]+章.*)"
    parts = re.split(chapter_pattern, text)

    chapters = []
    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        content = parts[i + 1].strip() if i + 1 < len(parts) else ''
        chapters.append((title, content))
    return chapters


def split_chapter_into_chunks(chapter_title, content, max_length=3000):
    chunks = []
    start = 0
    while start < len(content):
        end = start + max_length
        chunk = content[start:end]
        chunks.append({
            'chapter': chapter_title,
            'text': chunk,
            'start_idx': start,
            'end_idx': min(end, len(content))
        })
        start = end
    return chunks


def load_article_chunks(path, max_length=3000):
    with open(path, "rb") as f:
        text = f.read()
        result = chardet.detect(text)
        encoding = result['encoding']
        try:
            text = text.decode(encoding)
        except UnicodeDecodeError:
            text = text.decode('gb18030', errors='ignore')
    chunks = []
    for title, content in split_by_chapter(text):
        chunks.extend(split_chapter_into_chunks(title, content, max_length))
    return chunks


# 用 fixture 参数化文章段落
@pytest.fixture(params=load_article_chunks("../斗破苍穹.txt"))
def article_chunk(request):
    return request.param

class TestNovel:

    @allure.title("测试文章评分")
    def test_article_rating(self, article_chunk):
        try:
            bool, message = novel_script.check_rating(article_chunk)
            assert bool, f"{message}";
        except Exception as e:
            allure.attach(message, name="报错信息", attachment_type=allure.attachment_type.TEXT)
            raise


    #
    # @allure.suite("AI SEO 合规检测")
    # @allure.title("测试图片")
    # def testCheckImage(self, url):
    #
    #     def checkImage(soup):  # 参数名改为 chrome
    #         if not soup:
    #             return False, '无法获取页面 soup'
    #
    #         image = soup.find('img')
    #         if image:
    #             return True, ''
    #         return False, '该文章内没有引用图片'
    #
    #     print("测试图片")
    #     soup = url["soup"]
    #     message = ""
    #     try:
    #         bool, message = checkImage(soup)
    #         assert bool, f"{message}"
    #     except Exception as e:
    #         allure.attach(message, name="报错信息", attachment_type=allure.attachment_type.TEXT)
    #         raise  # 最后记得继续抛出，让pytest知道是失败