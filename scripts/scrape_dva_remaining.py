#!/usr/bin/env python3
"""Scrape remaining DVA#01-#40 via CDP"""
import json, time, websocket, urllib.request

DVA_REMAINING = {
    1: "dva01", 2: "dva02", 3: "dva03", 4: "dva04", 5: "dva05",
    6: "01-06", 7: "01-07", 8: "01-08", 9: "01-09", 10: "02-10",
    11: "02-11", 12: "02-12", 13: "02-13", 14: "02-14", 15: "02-15",
    16: "02-16", 17: "02-17", 18: "02-18", 19: "02-19", 20: "03-20",
    21: "03-21", 22: "03-22", 23: "3-dva23", 24: "3-dva24", 25: "3-dva25",
    26: "03dva26", 27: "33-dva27", 28: "dva04-28", 29: "41-dva29", 30: "04-dva30",
    31: "04-dva31", 32: "05-dva32", 33: "08-dva33", 34: "08-dva34", 35: "28-dva35",
    36: "04-dva36", 37: "04-dva37", 38: "04-dva38", 39: "04-dva39", 40: "04-dva40",
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
          if (['A','B','C','D','E'].includes(label) && text) choices.push({label, text});
        }
      });
    }
    const explDiv = q.querySelector('.mtq_explanation');
    let explanation = '', answer = [];
    if (explDiv) {
      const fullText = explDiv.textContent.trim();
      const ansMatch = fullText.match(/正解\s*([A-E](?:\s*,\s*[A-E])*)/);
      if (ansMatch) answer = ansMatch[1].replace(/\s/g, '').split(',').filter(a => a && a.length === 1);
      const parts = fullText.split(/正解/);
      explanation = parts[0].replace(/問題\s*\d+\s*の説明および補足/, '').trim();
    }
    if (qText && choices.length >= 2) questions.push({qNum: idx+1, question: qText, choices, answer, explanation});
  });
  return JSON.stringify(questions);
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
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == msg_id: return r

def main():
    ws_url = get_ws_url()
    ws = websocket.create_connection(ws_url)
    cdp_send(ws, "Page.enable")
    
    all_new = []
    for num, slug in sorted(DVA_REMAINING.items()):
        url = f"https://cloud-license.com/exam/dva/{slug}/"
        cdp_send(ws, "Page.navigate", {"url": url})
        time.sleep(4)
        r = cdp_send(ws, "Runtime.evaluate", {"expression": EXTRACT_JS, "returnByValue": True})
        raw = json.loads(r["result"]["result"]["value"])
        qs = []
        for q in raw:
            answer = list(dict.fromkeys(q.get('answer', [])))
            qs.append({"id": f"dva{num:02d}-{q['qNum']}", "question": q["question"], "choices": q["choices"], "answer": answer, "multiSelect": len(answer)>1, "explanation": q.get("explanation","")})
        print(f"DVA#{num:02d}: {len(qs)}問")
        all_new.extend(qs)
        time.sleep(1)
    ws.close()
    
    print(f"\nNew: {len(all_new)}")
    
    path = "/Users/yoshi/aws-quiz-app/lib/questions.json"
    with open(path, 'r') as f: existing = json.load(f)
    
    # Remove only dva01-dva40 (keep dva41-dva70)
    existing_ids = {q['id'] for q in all_new}
    existing = [q for q in existing if q['id'] not in existing_ids]
    existing.extend(all_new)
    existing.sort(key=lambda q: q['id'])
    
    with open(path, 'w') as f: json.dump(existing, f, ensure_ascii=False, indent=2)
    
    exams = {}
    for q in existing:
        exams[q['id'][:3]] = exams.get(q['id'][:3], 0) + 1
    print(f"\nTotal: {len(existing)}")
    for k, v in sorted(exams.items()): print(f"  {k.upper()}: {v}")

if __name__ == '__main__':
    main()
