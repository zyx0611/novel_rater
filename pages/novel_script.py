import requests
import re
from scorer.log import logger

def query_deepseek(prompt):
    url = "http://115.190.111.233:11434/api/generate"  # 这里的地址换成容器暴露出来的地址和端口
    payload = {
        "model": "deepseek-r1:32b",
        "prompt": f'''{prompt.get('chapter')},根据这个评分标准"GPT评分": {{
    "语言流畅性": 20,
    "情节合理性": 20,
    "角色塑造": 10,
    "结构完整性": 20,
    "创造力与新颖性": 10,
    "合规与伦理性": 20
  }}百分制评分''',
        "stream": False
    }
    try:
        response = requests.post(url, json=payload, timeout=1000)
        if response.status_code == 200:
            print(response.json()['response'])
            return True,response.json()['response']
        else:
            print(f"deepseek接口调用错误,错误码{response.status_code},信息:{response.text}")
            return False , f"deepseek接口调用错误,错误码{response.status_code},信息:{response.text}"
    except Exception as e:
        return False, f"deepseek接口调用失败, {e}"

def check_rating(prompt):
    bool, result = query_deepseek(prompt)
    if bool:
        # 正则提取每个评分项及其得分（支持中英文冒号）
        pattern = r'[-–•*]+\s*(.*?)[:：]?\s*(\d+)\s*/\s*(\d+)'
        matches = re.findall(pattern, result)

        scores = []
        for item, score, full in matches:
            scores.append({
                "项": item.strip(),
                "得分": int(score),
                "满分": int(full)
            })
        return bool, result
    else:
        return bool, result

# 加载外部违规词库
def load_banned_words(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        banned_words = f.read().splitlines()
    return banned_words

# 使用结巴进行分词检测
def detect_banned_words(text, banned_words):
    # words = jieba.lcut(text)
    found_words = [word.replace(',', '') for word in banned_words if word.replace(',', '') in text]

    if found_words:
        return False, found_words
    else:
        return True, ''

def JudgeLllegalWords(text):
    # 加载违规词库
    # banned_words = load_banned_words('../色情类.txt')
    banned_words = load_banned_words('色情类.txt')
    # 检测是否有违禁词
    is_banned, banned_found = detect_banned_words(text, banned_words)
    logger.info("违规词：%s", banned_found)
    return is_banned, f'违规词:{banned_found}'