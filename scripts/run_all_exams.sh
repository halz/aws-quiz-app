#!/bin/bash
set -e
cd /Users/yoshi/aws-quiz-app

EXAMS="dea mla sap dop ans scs cdl ace pca"

for exam in $EXAMS; do
  echo ""
  echo "=========================================="
  echo "  Starting $exam..."
  echo "=========================================="
  python3 -u scripts/scrape_exam.py "$exam"
  echo "  $exam DONE ✓"
  echo ""
done

echo ""
echo "=========================================="
echo "  ALL EXAMS COMPLETE!"
echo "=========================================="
python3 -c "
import json
with open('lib/questions.json') as f: data = json.load(f)
exams = {}
for q in data:
    e = q['id'][:3]
    exams[e] = exams.get(e, 0) + 1
print(f'Total: {len(data)}')
for k,v in sorted(exams.items()): print(f'  {k.upper()}: {v}')
"
