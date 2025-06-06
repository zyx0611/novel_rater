import requests
import re

def query_deepseek(prompt):
    url = "http://115.190.111.233:11434/api/generate"  # 这里的地址换成容器暴露出来的地址和端口
    payload = {
        "model": "deepseek-r1:32b",
        "prompt": prompt,
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
        return bool, scores
    else:
        return bool, result