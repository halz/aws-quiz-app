#!/usr/bin/env python3
"""Scrape Cloud License DVA questions via Chrome DevTools Protocol"""
import json
import time
import sys
import websocket
import urllib.request

CDP_URL = "http://localhost:9222"

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

EXTRACT_JS = """
(() => {
  const questions = [];
  const qDivs = document.querySelectorAll('.mtq_question');
  
  qDivs.forEach((q, idx) => {
    const qText = q.querySelector('.mtq_question_text')?.textContent.trim() || '';
    
    const choices = [];
    const answerTable = q.querySelector('.mtq_answer_table');
    if (answerTable) {
      const rows = answerTable.querySelectorAll('tr');
      rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 2) {
          const label = cells[0].textContent.trim();
          const text = cells[1].textContent.trim();
          if (['A','B','C','D','E'].includes(label) && text) {
            choices.push({label, text});
          }
        }
      });
    }
    
    const explDiv = q.querySelector('.mtq_explanation');
    let explanation = '';
    let answer = [];
    if (explDiv) {
      const fullText = explDiv.textContent.trim();
      const ansMatch = fullText.match(/正解\\s*([A-E][,\\s]*[A-E]?[,\\s]*[A-E]?)/);
      if (ansMatch) {
        answer = ansMatch[1].replace(/\\s/g, '').split(',').filter(a => a && a.length === 1);
      }
      const parts = fullText.split(/正解/);
      explanation = parts[0].replace(/問題\\s*\\d+\\s*の説明および補足\\s*/, '').trim();
    }
    
    if (qText && choices.length >= 2) {
      questions.push({
        qNum: idx + 1,
        question: qText,
        choices,
        answer,
        explanation
      });
    }
  });
  
  return JSON.stringify(questions);
})()
"""


def get_ws_url():
    """Get the WebSocket URL for the first tab"""
    resp = urllib.request.urlopen(f"{CDP_URL}/json/list")
    tabs = json.loads(resp.read())
    for tab in tabs:
        if 'webSocketDebuggerUrl' in tab:
            return tab['webSocketDebuggerUrl'], tab['id']
    return None, None


def cdp_send(ws, method, params=None, timeout=30):
    """Send CDP command and wait for result"""
    import random
    msg_id = random.randint(1, 999999)
    msg = {"id": msg_id, "method": method}
    if params:
        msg["params"] = params
    ws.send(json.dumps(msg))
    
    start = time.time()
    while time.time() - start < timeout:
        try:
            ws.settimeout(timeout)
            response = json.loads(ws.recv())
            if response.get("id") == msg_id:
                return response
        except:
            break
    return None


def navigate_and_extract(ws, url, section_num):
    """Navigate to URL and extract questions"""
    # Navigate
    result = cdp_send(ws, "Page.navigate", {"url": url})
    time.sleep(3)  # Wait for page load
    
    # Execute extraction script
    result = cdp_send(ws, "Runtime.evaluate", {
        "expression": EXTRACT_JS,
        "returnByValue": True
    })
    
    if not result or "result" not in result:
        return []
    
    value = result["result"].get("result", {}).get("value", "[]")
    try:
        raw_questions = json.loads(value)
    except:
        return []
    
    # Format with proper IDs
    questions = []
    for q in raw_questions:
        q_id = f"dva{section_num:02d}-{q['qNum']}"
        # Fix answer parsing - remove duplicates
        answer = list(dict.fromkeys(q.get('answer', [])))
        
        questions.append({
            "id": q_id,
            "question": q["question"],
            "choices": q["choices"],
            "answer": answer,
            "multiSelect": len(answer) > 1,
            "explanation": q.get("explanation", "")
        })
    
    return questions


def main():
    print("=== Cloud License DVA Scraper (via CDP) ===\n")
    
    ws_url, tab_id = get_ws_url()
    if not ws_url:
        print("ERROR: No WebSocket URL found. Is Chrome running with --remote-debugging-port?")
        sys.exit(1)
    
    print(f"Connected to Chrome tab: {tab_id[:12]}")
    
    ws = websocket.create_connection(ws_url)
    
    # Enable Page events
    cdp_send(ws, "Page.enable")
    
    all_questions = []
    
    for section_num, slug in sorted(DVA_SECTIONS.items()):
        url = f"https://cloud-license.com/exam/dva/{slug}/"
        print(f"DVA#{section_num:02d}... ", end="", flush=True)
        
        questions = navigate_and_extract(ws, url, section_num)
        print(f"{len(questions)}問")
        all_questions.extend(questions)
        
        time.sleep(1)
    
    ws.close()
    
    print(f"\n=== Total: {len(all_questions)} questions ===")
    
    # Save
    questions_path = "/Users/yoshi/aws-quiz-app/lib/questions.json"
    with open(questions_path, 'r', encoding='utf-8') as f:
        existing = json.load(f)
    
    # Remove old dva questions
    existing = [q for q in existing if not q['id'].startswith('dva')]
    print(f"After removing old DVA: {len(existing)}")
    
    existing.extend(all_questions)
    existing.sort(key=lambda q: q['id'])
    
    with open(questions_path, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    
    exams = {}
    for q in existing:
        exam = q['id'][:3]
        exams[exam] = exams.get(exam, 0) + 1
    
    print(f"\nTotal: {len(existing)} questions")
    for k, v in sorted(exams.items()):
        print(f"  {k.upper()}: {v}")


if __name__ == '__main__':
    main()
