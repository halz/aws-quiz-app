#!/usr/bin/env python3
"""Scrape multiple Cloud License exam sections via CDP"""
import json, time, re, sys, websocket, urllib.request

EXAM_PAGES = {
    'dea': 'https://cloud-license.com/exam/dea/',
    'mla': 'https://cloud-license.com/exam/mla/',
    'sap': 'https://cloud-license.com/exam/sap/',
    'dop': 'https://cloud-license.com/exam/dop/',
    'ans': 'https://cloud-license.com/exam/ans/',
    'scs': 'https://cloud-license.com/exam/scs/',
    'cdl': 'https://cloud-license.com/exam/cdl/',
    'ace': 'https://cloud-license.com/exam/ace/',
    'pca': 'https://cloud-license.com/exam/pca/',
}

EXTRACT_JS = r"""
(() => {
  const questions = [];
  const qDivs = document.querySelectorAll('.mtq_question');
  qDivs.forEach((q, idx) => {
    const qText = q.querySelector('.mtq_question_text')?.textContent.trim() || '';
    const choices = [];
    const answerTable = q.querySelector('.mtq_answer_table');
    if (answerTable) {
      answerTable.querySelectorAll('tr').forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 2) {
          const label = cells[0].textContent.trim();
          const text = cells[1].textContent.trim();
          if (['A','B','C','D','E','F'].includes(label) && text) choices.push({label, text});
        }
      });
    }
    const explDiv = q.querySelector('.mtq_explanation');
    let explanation = '', answer = [];
    if (explDiv) {
      const fullText = explDiv.textContent.trim();
      const ansMatch = fullText.match(/正解\s*([A-F](?:\s*,?\s*[A-F])*)/);
      if (ansMatch) answer = ansMatch[1].replace(/\s/g,'').split(',').filter(a => a && a.length===1);
      const parts = fullText.split(/正解/);
      explanation = parts[0].replace(/問題\s*\d+\s*の説明および補足/, '').trim();
    }
    if (qText && choices.length >= 2) questions.push({qNum: idx+1, question: qText, choices, answer, explanation});
  });
  return JSON.stringify(questions);
})()
"""

EXTRACT_LINKS_JS = r"""
(() => {
  const links = [];
  document.querySelectorAll('.textwidget a, .widget_text a').forEach(a => {
    const href = a.href;
    const text = a.textContent.trim();
    if (href && text) links.push({href, text});
  });
  return JSON.stringify(links);
})()
"""

def get_ws_url():
    resp = urllib.request.urlopen("http://localhost:9222/json/list")
    for tab in json.loads(resp.read()):
        if 'webSocketDebuggerUrl' in tab:
            return tab['webSocketDebuggerUrl']
    return None

def cdp_send(ws, method, params=None):
    import random
    msg_id = random.randint(1, 999999)
    msg = {"id": msg_id, "method": method}
    if params: msg["params"] = params
    ws.send(json.dumps(msg))
    ws.settimeout(30)
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == msg_id: return r

def navigate_extract_questions(ws, url, exam_code, section_num):
    cdp_send(ws, "Page.navigate", {"url": url})
    time.sleep(4)
    r = cdp_send(ws, "Runtime.evaluate", {"expression": EXTRACT_JS, "returnByValue": True})
    try:
        raw = json.loads(r["result"]["result"]["value"])
    except:
        return []
    qs = []
    for q in raw:
        answer = list(dict.fromkeys(q.get('answer', [])))
        qs.append({
            "id": f"{exam_code}{section_num:02d}-{q['qNum']}",
            "question": q["question"],
            "choices": q["choices"],
            "answer": answer,
            "multiSelect": len(answer) > 1,
            "explanation": q.get("explanation", "")
        })
    return qs

def get_section_links(ws, exam_page_url, exam_code):
    """Navigate to exam index page and extract section links"""
    cdp_send(ws, "Page.navigate", {"url": exam_page_url})
    time.sleep(3)
    r = cdp_send(ws, "Runtime.evaluate", {"expression": EXTRACT_LINKS_JS, "returnByValue": True})
    try:
        links = json.loads(r["result"]["result"]["value"])
    except:
        return {}
    
    sections = {}
    pattern = re.compile(rf'{exam_code.upper()}#(\d+)', re.IGNORECASE)
    for link in links:
        m = pattern.search(link['text'])
        if m:
            num = int(m.group(1))
            sections[num] = link['href']
    return sections

def main():
    exams_to_scrape = sys.argv[1:] if len(sys.argv) > 1 else list(EXAM_PAGES.keys())
    
    ws_url = get_ws_url()
    if not ws_url:
        print("ERROR: Chrome not connected")
        sys.exit(1)
    
    ws = websocket.create_connection(ws_url)
    cdp_send(ws, "Page.enable")
    
    path = "/Users/yoshi/aws-quiz-app/lib/questions.json"
    with open(path, 'r') as f:
        existing = json.load(f)
    
    grand_total_new = 0
    
    for exam_code in exams_to_scrape:
        if exam_code not in EXAM_PAGES:
            print(f"Unknown exam: {exam_code}")
            continue
        
        print(f"\n{'='*50}")
        print(f"  {exam_code.upper()} - Getting section list...")
        print(f"{'='*50}")
        
        sections = get_section_links(ws, EXAM_PAGES[exam_code], exam_code)
        if not sections:
            print(f"  No sections found for {exam_code.upper()}")
            continue
        
        print(f"  Found {len(sections)} sections")
        
        exam_questions = []
        for num, url in sorted(sections.items()):
            qs = navigate_extract_questions(ws, url, exam_code, num)
            print(f"  {exam_code.upper()}#{num:02d}: {len(qs)}問")
            exam_questions.extend(qs)
            time.sleep(0.5)
        
        # Remove old questions for this exam and add new
        existing = [q for q in existing if not q['id'].startswith(exam_code)]
        existing.extend(exam_questions)
        grand_total_new += len(exam_questions)
        
        print(f"  {exam_code.upper()} total: {len(exam_questions)}問")
    
    ws.close()
    
    # Sort and save
    existing.sort(key=lambda q: q['id'])
    with open(path, 'w') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    
    # Stats
    exams = {}
    for q in existing:
        e = q['id'][:3]
        exams[e] = exams.get(e, 0) + 1
    
    print(f"\n{'='*50}")
    print(f"  GRAND TOTAL: {len(existing)} questions")
    print(f"  New this run: {grand_total_new}")
    print(f"{'='*50}")
    for k, v in sorted(exams.items()):
        print(f"  {k.upper()}: {v}")

if __name__ == '__main__':
    main()
