#!/usr/bin/env python3
"""Scrape Cloud License DVA questions using requests + cookies from Chrome debug profile"""
import json
import os
import sys
import time
import http.cookiejar
import sqlite3
import shutil
import re
from urllib.request import Request, urlopen, HTTPCookieProcessor, build_opener

QUESTIONS_PATH = os.path.join(os.path.dirname(__file__), '..', 'lib', 'questions.json')

# DVA section URLs from the sidebar
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


def get_chrome_cookies(domain="cloud-license.com"):
    """Extract cookies from Chrome debug profile"""
    cookie_db = "/tmp/chrome-debug/Default/Cookies"
    if not os.path.exists(cookie_db):
        print("Cookie DB not found!")
        return {}
    
    # Copy to avoid lock issues
    tmp_db = "/tmp/chrome_cookies_copy.db"
    shutil.copy2(cookie_db, tmp_db)
    
    conn = sqlite3.connect(tmp_db)
    cursor = conn.cursor()
    
    # Try different column names for different Chrome versions
    try:
        cursor.execute("""
            SELECT name, value, host_key, path 
            FROM cookies 
            WHERE host_key LIKE ?
        """, (f"%{domain}%",))
    except Exception as e:
        print(f"DB error: {e}")
        conn.close()
        return {}
    
    cookies = {}
    for name, value, host, path in cursor.fetchall():
        if value:  # Some cookies may be encrypted
            cookies[name] = value
    
    conn.close()
    os.remove(tmp_db)
    return cookies


def fetch_page(url, cookies_dict):
    """Fetch a page with cookies"""
    req = Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    req.add_header('Cookie', '; '.join(f'{k}={v}' for k, v in cookies_dict.items()))
    req.add_header('Accept', 'text/html,application/xhtml+xml')
    
    try:
        resp = urlopen(req, timeout=15)
        return resp.read().decode('utf-8')
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return None


def parse_questions_scrapling(html, section_num):
    """Parse questions from HTML using Scrapling"""
    from scrapling import Adaptor
    
    page = Adaptor(html, url=f"https://cloud-license.com/exam/dva/")
    questions = []
    
    # Find all question blocks - they follow the pattern: table (header) + div (question text) + table (choices)
    # Get all text nodes that are question content
    all_tables = page.css('table')
    
    question_num = 0
    i = 0
    while i < len(all_tables):
        table = all_tables[i]
        # Check if this is a question header table (contains "問題N")
        header_text = table.text.strip()
        
        if re.match(r'問題\d+', header_text):
            question_num += 1
            
            # The question text is in the next sibling div/generic after this table
            # And the choices are in the table after that
            # We need to look at the parent container
            parent = table.parent
            if parent is None:
                i += 1
                continue
            
            # Get all children of the grandparent container
            grandparent = parent.parent
            if grandparent is None:
                i += 1
                continue
            
            # Find question text - it's in a div after the header table's parent
            siblings = list(grandparent.children)
            
            q_text = ""
            choices = []
            
            # Look for text content after the header
            for sib in siblings:
                sib_text = sib.text.strip() if sib.text else ""
                
                # Question text (longer text block)
                if len(sib_text) > 50 and not any(label in sib_text[:5] for label in ['A ', 'B ', 'C ', 'D ', 'E ']):
                    if not q_text:
                        q_text = sib_text
                
                # Choices table
                if hasattr(sib, 'css'):
                    choice_rows = sib.css('tr')
                    for row in choice_rows:
                        cells = row.css('td')
                        if len(cells) >= 2:
                            label = cells[0].text.strip()
                            text = cells[1].text.strip()
                            if label in ['A', 'B', 'C', 'D', 'E'] and text:
                                choices.append({"label": label, "text": text})
            
            if q_text and len(choices) >= 2:
                q_id = f"dva{section_num:02d}-{question_num}"
                questions.append({
                    "id": q_id,
                    "question": q_text,
                    "choices": choices,
                    "answer": [],  # No answers visible without clicking
                    "multiSelect": len(choices) > 4,
                    "explanation": ""
                })
        i += 1
    
    return questions


def parse_questions_regex(html, section_num):
    """Fallback parser using regex"""
    from scrapling import Adaptor
    
    page = Adaptor(html, url="https://cloud-license.com/exam/dva/")
    questions = []
    
    # Get the main article content
    article = page.css_first('article')
    if not article:
        return questions
    
    # Get all the question container divs
    # Each question has: header table + question text div + choices table
    containers = article.css('.wp-block-flexible-table-block-table')
    if not containers:
        containers = article.css('table')
    
    # Alternative approach: find question markers
    full_text = article.text
    
    # Split by question markers
    q_pattern = re.compile(r'問題(\d+)')
    q_matches = list(q_pattern.finditer(full_text))
    
    for idx, match in enumerate(q_matches):
        q_num = int(match.group(1))
        start = match.end()
        end = q_matches[idx + 1].start() if idx + 1 < len(q_matches) else len(full_text)
        
        block = full_text[start:end].strip()
        
        # Remove header artifacts
        block = re.sub(r'^本試験モード：.*?\n', '', block)
        block = re.sub(r'^お気に入り[①②③]', '', block, flags=re.MULTILINE)
        block = re.sub(r'^リンクを表示', '', block, flags=re.MULTILINE)
        block = block.strip()
        
        # Split into question text and choices
        # Choices start with a single letter followed by space
        choice_pattern = re.compile(r'\n\s*([A-E])\s+(.+?)(?=\n\s*[A-E]\s|\n\s*学習を記録|\Z)', re.DOTALL)
        choice_matches = list(choice_pattern.finditer(block))
        
        if not choice_matches:
            # Try alternative pattern
            choice_pattern2 = re.compile(r'([A-E])\s(.+?)(?=[A-E]\s|\Z)', re.DOTALL)
            choice_matches = list(choice_pattern2.finditer(block))
        
        if choice_matches:
            q_text = block[:choice_matches[0].start()].strip()
            q_text = re.sub(r'\s+', ' ', q_text).strip()
            
            choices = []
            for cm in choice_matches:
                label = cm.group(1)
                text = cm.group(2).strip()
                text = re.sub(r'\s+', ' ', text).strip()
                if text and label in 'ABCDE':
                    choices.append({"label": label, "text": text})
            
            if q_text and len(choices) >= 2:
                q_id = f"dva{section_num:02d}-{q_num}"
                questions.append({
                    "id": q_id,
                    "question": q_text,
                    "choices": choices,
                    "answer": [],
                    "multiSelect": False,
                    "explanation": ""
                })
    
    return questions


def main():
    print("=== Cloud License DVA Scraper ===\n")
    
    # Get cookies
    cookies = get_chrome_cookies()
    print(f"Got {len(cookies)} cookies")
    
    if not cookies:
        print("No cookies found! Using CDP to get cookies...")
        # Try fetching via the running Chrome's CDP
        import urllib.request
        try:
            resp = urllib.request.urlopen("http://localhost:9222/json/list")
            print("Chrome debug available, but need cookies from browser")
        except:
            pass
    
    all_questions = []
    
    for section_num, slug in sorted(DVA_SECTIONS.items()):
        url = f"https://cloud-license.com/exam/dva/{slug}/"
        print(f"DVA#{section_num:02d} ({slug})... ", end="", flush=True)
        
        html = fetch_page(url, cookies)
        if not html:
            print("FAILED")
            continue
        
        # Check if we're logged in
        if "会員登録" in html and "問題1" not in html:
            print("NOT LOGGED IN - need valid cookies")
            break
        
        questions = parse_questions_regex(html, section_num)
        print(f"{len(questions)} questions")
        all_questions.extend(questions)
        
        time.sleep(0.5)  # Be nice to the server
    
    print(f"\n=== Total: {len(all_questions)} questions ===\n")
    
    if not all_questions:
        print("No questions collected! Check login/cookies.")
        sys.exit(1)
    
    # Load existing questions
    with open(QUESTIONS_PATH, 'r', encoding='utf-8') as f:
        existing = json.load(f)
    
    # Remove old dva questions
    existing = [q for q in existing if not q['id'].startswith('dva')]
    print(f"After removing old DVA: {len(existing)} questions")
    
    # Add new
    existing.extend(all_questions)
    existing.sort(key=lambda q: q['id'])
    
    with open(QUESTIONS_PATH, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    
    # Stats
    exams = {}
    for q in existing:
        exam = q['id'][:3]
        exams[exam] = exams.get(exam, 0) + 1
    
    print(f"\nTotal: {len(existing)} questions")
    for k, v in sorted(exams.items()):
        print(f"  {k.upper()}: {v}")


if __name__ == '__main__':
    main()
