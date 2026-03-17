#!/usr/bin/env python3
"""Scrape a single Cloud License exam via CDP. Usage: python3 -u scrape_exam.py <exam_code>"""
import json, time, re, sys, websocket, urllib.request

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
  document.querySelectorAll('a').forEach(a => {
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

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 -u scrape_exam.py <exam_code>")
        sys.exit(1)
    
    exam_code = sys.argv[1].lower()
    exam_url = f"https://cloud-license.com/exam/{exam_code}/"
    
    ws_url = get_ws_url()
    if not ws_url:
        print("ERROR: Chrome not connected"); sys.exit(1)
    
    ws = websocket.create_connection(ws_url)
    cdp_send(ws, "Page.enable")
    
    # Get section links
    print(f"=== {exam_code.upper()} ===")
    cdp_send(ws, "Page.navigate", {"url": exam_url})
    time.sleep(3)
    r = cdp_send(ws, "Runtime.evaluate", {"expression": EXTRACT_LINKS_JS, "returnByValue": True})
    try:
        links = json.loads(r["result"]["result"]["value"])
    except:
        print("ERROR: Could not get links"); ws.close(); sys.exit(1)
    
    pattern = re.compile(rf'{exam_code.upper()}#(\d+)', re.IGNORECASE)
    sections = {}
    for link in links:
        m = pattern.search(link['text'])
        if m:
            num = int(m.group(1))
            sections[num] = link['href']
    
    if not sections:
        # Try alternate pattern
        pattern2 = re.compile(rf'/exam/{exam_code}/[^/]+/', re.IGNORECASE)
        for link in links:
            m2 = pattern2.search(link['href'])
            if m2:
                text = link['text'].strip()
                num_match = re.search(r'#(\d+)', text)
                if num_match:
                    num = int(num_match.group(1))
                    sections[num] = link['href']
    
    print(f"Found {len(sections)} sections")
    if not sections:
        print("No sections found!"); ws.close(); sys.exit(1)
    
    # Scrape each section
    all_qs = []
    for num, url in sorted(sections.items()):
        cdp_send(ws, "Page.navigate", {"url": url})
        time.sleep(4)
        r = cdp_send(ws, "Runtime.evaluate", {"expression": EXTRACT_JS, "returnByValue": True})
        try:
            raw = json.loads(r["result"]["result"]["value"])
        except:
            raw = []
        qs = []
        for q in raw:
            answer = list(dict.fromkeys(q.get('answer', [])))
            qs.append({
                "id": f"{exam_code}{num:02d}-{q['qNum']}",
                "question": q["question"],
                "choices": q["choices"],
                "answer": answer,
                "multiSelect": len(answer) > 1,
                "explanation": q.get("explanation", "")
            })
        print(f"  {exam_code.upper()}#{num:02d}: {len(qs)}問")
        all_qs.extend(qs)
        time.sleep(0.5)
    
    ws.close()
    
    print(f"\n{exam_code.upper()} total: {len(all_qs)}問")
    
    # Save to questions.json
    path = "/Users/yoshi/aws-quiz-app/lib/questions.json"
    with open(path, 'r') as f: existing = json.load(f)
    
    existing = [q for q in existing if not q['id'].startswith(exam_code)]
    existing.extend(all_qs)
    existing.sort(key=lambda q: q['id'])
    
    with open(path, 'w') as f: json.dump(existing, f, ensure_ascii=False, indent=2)
    
    exams = {}
    for q in existing:
        e = q['id'][:3]
        exams[e] = exams.get(e, 0) + 1
    
    print(f"\nSaved! Total: {len(existing)}")
    for k, v in sorted(exams.items()): print(f"  {k.upper()}: {v}")

if __name__ == '__main__':
    main()
