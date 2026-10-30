import json
import re
import time
import requests
from bs4 import BeautifulSoup

LEVEL_URLS = {
    1: "https://tinyurl.com/bdw3w88u",
    2: "https://tinyurl.com/mvznuf9z",
    3: "https://tinyurl.com/4cm8pjf3",
    4: "https://tinyurl.com/hwatnkbr",
    5: "https://tinyurl.com/2atzu3yx",
    6: "https://tinyurl.com/mry8kncr",
    7: "https://tinyurl.com/yjf4cd4u",
    8: "https://tinyurl.com/bddcjrcf",
    9: "https://tinyurl.com/5ambn5py",
    10: "https://tinyurl.com/5d4afebb",
    11: "https://tinyurl.com/2s3usxu9",
    12: "https://tinyurl.com/2maa6zh4",
    13: "https://tinyurl.com/3rmjd87x",
    14: "https://tinyurl.com/p42cnsn2",
    15: "https://tinyurl.com/3dd4zecx",
    16: "https://tinyurl.com/3w6k5amm",
    17: "https://tinyurl.com/6as9ncck",
    18: "https://tinyurl.com/2zyawvwt",
    19: "https://tinyurl.com/y29bb3fn",
    20: "https://tinyurl.com/y4vhz364",
    21: "https://tinyurl.com/2nx79npe",
    22: "https://tinyurl.com/4v48akfe",
    23: "https://tinyurl.com/mry5bt48",
    24: "https://tinyurl.com/4jjymkcr",
    25: "https://tinyurl.com/mv2n5nrr",
    26: "https://tinyurl.com/96ar39at",
    27: "https://tinyurl.com/34nh8n7p",
    28: "https://tinyurl.com/36waa7tc",
    29: "https://tinyurl.com/m9zsmntj",
    30: "https://tinyurl.com/5cj84y5b",
    31: "https://tinyurl.com/2bxw9mep",
    32: "https://tinyurl.com/zpxwcvha",
    33: "https://tinyurl.com/3n3an452",
    34: "https://tinyurl.com/27hwk7p2",
    35: "https://tinyurl.com/2vy5rc7b",
    36: "https://tinyurl.com/ycxnz97b",
    37: "https://tinyurl.com/4nxr9rwk",
    38: "https://tinyurl.com/yck23c66",
    39: "https://tinyurl.com/mtsbya7h",
    40: "https://tinyurl.com/4afj8kvb",
    41: "https://tinyurl.com/3aytyfxt",
    42: "https://tinyurl.com/4k5adw63"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

def is_code_line(line: str) -> bool:
    arabic_chars = re.findall(r'[\u0600-\u06FF]', line)
    return not bool(arabic_chars)

def parse_level_html(html_content: str):
    soup = BeautifulSoup(html_content, "html.parser")
    post_body = soup.find("div", class_=re.compile(r"post-body|entry-content")) or soup.body
    lines = [line.strip() for line in post_body.get_text(separator="\n").split("\n")]

    tasks = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if "نضغط علي تشغيل الكود فقط" in line or "انقر على \"تشغيل الكود\" دون تعديل" in line:
            tasks.append({"type": "RUN_ONLY", "value": ""})
            i += 1
            continue

        if any(marker in line for marker in ["شكل الكود النهائي", "شكل الكود بالكامل", "شكل الكود كامل", "ليكون هكذا"]):
            code_lines = []
            empty_line_2 = "السطر الثاني فارغ" in line
            empty_line_3 = "السطر الثالث فارغ" in line
            i += 1
            while i < len(lines):
                curr = lines[i]
                if not curr:
                    i += 1
                    continue
                if is_code_line(curr):
                    code_lines.append(curr)
                    i += 1
                else:
                    break
            if code_lines:
                if empty_line_2 and len(code_lines) >= 2:
                    code_lines.insert(1, "")
                elif empty_line_3 and len(code_lines) >= 3:
                    code_lines.insert(2, "")
                tasks.append({"type": "CODE", "value": "\n".join(code_lines)})
            continue

        if line.startswith("الاجابة") or line.startswith("الإجابة"):
            remainder = re.sub(r"^(الاجابة|الإجابة)\s*:?\s*", "", line).strip()
            if remainder and not any(w in remainder for w in ["نكتب", "مسح", "كتابة", "تعديل"]):
                tasks.append({"type": "MCQ_OR_INLINE", "value": remainder.rstrip(".")})
                i += 1
                continue
            else:
                i += 1
                code_lines = []
                while i < len(lines):
                    curr = lines[i]
                    if not curr:
                        i += 1
                        continue
                    if is_code_line(curr):
                        code_lines.append(curr)
                        i += 1
                    else:
                        break
                if code_lines:
                    tasks.append({"type": "CODE", "value": "\n".join(code_lines)})
                continue
        i += 1
    return tasks

def main():
    all_answers = {}
    session = requests.Session()
    session.headers.update(HEADERS)

    for level, short_url in LEVEL_URLS.items():
        print(f"📥 Fetching Level {level}/42...")
        try:
            resp = session.get(short_url, allow_redirects=True, timeout=20)
            resp.raise_for_status()
            tasks = parse_level_html(resp.text)
            all_answers[str(level)] = {"resolved_url": resp.url, "tasks": tasks}
        except Exception as e:
            print(f"❌ Error at level {level}: {e}")
        time.sleep(0.3)

    with open("qureo_answers.json", "w", encoding="utf-8") as f:
        json.dump(all_answers, f, ensure_ascii=False, indent=2)
    print("\n🎉 Saved qureo_answers.json successfully!")

if __name__ == "__main__":
    main()
