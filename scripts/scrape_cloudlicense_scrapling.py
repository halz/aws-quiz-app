#!/usr/bin/env python3
import json, time, re
import requests
from scrapling import Selector

COOKIE = "_gid=GA1.2.401019017.1773733905; __stripe_mid=edb05b26-75ed-42b3-baf0-e3bd95d973c5bcfa72; __stripe_sid=ec9057c0-137d-410d-88f6-241a6cc5abb456246c; swpm_in_use=swpm_in_use; wp_swpm_in_use=wp_swpm_in_use; swpm_session=db48ac4b6a70a5dd0ff3ca1578cea143; _gat_gtag_UA_23162773_1=1; PHPSESSID=6e7a617d6e7b4abaa9bc5608492a7e45; _ga_00Q2XFSZWB=GS2.1.s1773733905$o1$g1$t1773736163$j60$l0$h0; _ga=GA1.1.276045002.1773733905"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "Cookie": COOKIE,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
}

DVA_SECTIONS = {
    1: "dva01", 2: "dva02", 3: "dva03", 4: "dva04", 5: "dva05",
    6: "01-06", 7: "01-07", 8: "01-08", 9: "01-09", 10: "02-10",
    11: "02-11", 12: "02-12", 13: "02-13", 14: "02-14", 15: "02-15",
    16: "02-16", 17: "02-17", 18: "02-18", 19: "02-19", 20: "03-20",
    21: "03-21", 22: "03-22", 23: "3-dva23", 24: "3-dva24", 25: "3-dva25",
    26: "03dva26", 27: "33-dva27", 28: "dva04-28", 29: "41-dva29", 30: "04-dva30",
    31: "04-dva31", 32: "05-dva32", 33: "08-dva33", 34: "08-dva34", 35: "28-dva35",
    36: "04-dva36", 37: "04-dva37", 38: "04-dva38", 39: "04-dva39", 40: "04-dva40",
    41: "04-dva41", 42: "05-dva42", 43: "dva43", 44: "dva44", 45: "dva45",
    46: "dva46", 47: "dva47", 48: "dva48", 49: "dva49", 50: "dva50",
    51: "dva51", 52: "iiuy8s9", 53: "dva53", 54: "dva54", 55: "dva55",
    56: "dva56", 57: "dva57", 58: "dvd58", 59: "dva59", 60: "dva60",
    61: "dva61", 62: "dva62", 63: "dva63", 64: "dva64", 65: "dva65",
    66: "dva66", 67: "dva67", 68: "dva68", 69: "dva69", 70: "dva70",
}


def extract_questions(html, section_num):
    page = Selector(html)
    result = []
    for idx, q in enumerate(page.css('.mtq_question'), start=1):
        q_text = q.css_first('.mtq_question_text')
        ans_table = q.css_first('.mtq_answer_table')
        expl = q.css_first('.mtq_explanation')
        if not q_text or not ans_table:
            continue
        question = re.sub(r'\s+', ' ', q_text.text).strip()
        choices = []
        for row in ans_table.css('tr'):
            cells = row.css('td')
            if len(cells) >= 2:
                label = cells[0].text.strip()
                text = re.sub(r'\s+', ' ', cells[1].text).strip()
                if label in ['A','B','C','D','E'] and text:
                    choices.append({"label": label, "text": text})
        explanation = ""
        answer = []
        if expl:
            expl_text = re.sub(r'\s+', ' ', expl.text).strip()
            m = re.search(r'正解\s*([A-E](?:\s*,\s*[A-E])*)', expl_text)
            if m:
                answer = [x.strip() for x in m.group(1).split(',')]
            explanation = re.sub(r'^問題\s*\d+\s*の説明および補足', '', expl_text)
            explanation = re.split(r'正解\s*[A-E]', explanation)[0].strip()
        if question and choices:
            result.append({
                "id": f"dva{section_num:02d}-{idx}",
                "question": question,
                "choices": choices,
                "answer": answer,
                "multiSelect": len(answer) > 1,
                "explanation": explanation,
            })
    return result


def fetch(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text


def main():
    all_questions = []
    for num, slug in DVA_SECTIONS.items():
        url = f"https://cloud-license.com/exam/dva/{slug}/"
        html = fetch(url)
        qs = extract_questions(html, num)
        print(f"DVA#{num:02d}: {len(qs)}")
        all_questions.extend(qs)
        time.sleep(0.3)
    print(f"TOTAL={len(all_questions)}")
    with open('/Users/yoshi/aws-quiz-app/lib/questions.json', 'r', encoding='utf-8') as f:
        existing = json.load(f)
    existing = [q for q in existing if not q['id'].startswith('dva')]
    existing.extend(all_questions)
    existing.sort(key=lambda q: q['id'])
    with open('/Users/yoshi/aws-quiz-app/lib/questions.json', 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
