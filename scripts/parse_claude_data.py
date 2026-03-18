#!/usr/bin/env python3
"""Parse anthropic-study-ja data into structured JSON for the quiz app"""
import json, re, os

SRC = "/Users/yoshi/anthropic-study-ja"
DST = "/Users/yoshi/aws-quiz-app/lib"

def parse_quiz_md():
    """Parse anthropic-academy-quiz.md into Question format"""
    with open(f"{SRC}/anthropic-academy-quiz.md", "r") as f:
        content = f.read()
    
    questions = []
    
    # Split by course sections (## コースN: ...)
    course_sections = re.split(r'^## (?:コース\d+|総合問題|上級編)', content, flags=re.MULTILINE)
    course_headers = re.findall(r'^## (コース\d+|総合問題|上級編)[^\n]*', content, flags=re.MULTILINE)
    
    for i, section in enumerate(course_sections[1:], 1):
        header = course_headers[i-1] if i-1 < len(course_headers) else f"section{i}"
        
        # Extract course number
        course_match = re.search(r'コース(\d+)', header)
        if course_match:
            course_num = int(course_match.group(1))
            course_prefix = f"claude-c{course_num:02d}"
        elif '総合' in header:
            course_prefix = "claude-gen"
        elif '上級編' in header or 'Architect' in header:
            course_prefix = "claude-arc"
        else:
            course_prefix = f"claude-s{i:02d}"
        
        # Find all questions in this section
        q_blocks = re.split(r'^###+ ', section, flags=re.MULTILINE)
        
        for block in q_blocks[1:]:
            # Extract question number/id
            q_id_match = re.match(r'(?:問題|ドメイン)[\s]*([\w\-]+)', block)
            if not q_id_match:
                continue
            
            q_id_raw = q_id_match.group(1).strip()
            
            # Check if it's a multiple choice question (A/B/C/D format)
            mc_match = re.search(r'\n\s*A\)\s+(.+?)(?:\n\s*B\)\s+(.+?))?(?:\n\s*C\)\s+(.+?))?(?:\n\s*D\)\s+(.+?))?(?:\n\s*E\)\s+(.+?))?\s*\n', block)
            
            if mc_match:
                # Multiple choice question
                q_text_match = re.search(r'[（）\w]+\）?\s*\n(.+?)(?=\n\s*A\))', block, re.DOTALL)
                if not q_text_match:
                    # Try without the difficulty tag
                    lines = block.split('\n')
                    q_text = ''
                    for line in lines[1:]:
                        if line.strip().startswith('A)'):
                            break
                        q_text += line.strip() + ' '
                    q_text = q_text.strip()
                else:
                    q_text = q_text_match.group(1).strip()
                
                choices = []
                for j, label in enumerate(['A', 'B', 'C', 'D', 'E']):
                    if mc_match.group(j+1):
                        choices.append({"label": label, "text": mc_match.group(j+1).strip()})
                
                # Extract answer from details block
                answer_match = re.search(r'<details>.*?<summary>.*?</summary>\s*\n\s*\*?\*?([A-E])\)?', block, re.DOTALL)
                answer = []
                if answer_match:
                    answer = [answer_match.group(1)]
                
                # Extract explanation
                expl_match = re.search(r'<details>.*?<summary>.*?</summary>\s*\n(.+?)</details>', block, re.DOTALL)
                explanation = expl_match.group(1).strip() if expl_match else ""
                # Clean markdown bold
                explanation = re.sub(r'\*\*(.+?)\*\*', r'\1', explanation)
                
                if q_text and choices:
                    questions.append({
                        "id": f"{course_prefix}-{q_id_raw}",
                        "question": q_text,
                        "choices": choices,
                        "answer": answer,
                        "multiSelect": len(answer) > 1,
                        "explanation": explanation
                    })
            else:
                # Open-ended question - convert to flash card style
                lines = block.split('\n')
                # First line after header is the question
                q_text = ''
                for line in lines:
                    line = line.strip()
                    if line.startswith('問題') or line.startswith('ドメイン'):
                        # Skip the header line itself, get rest
                        rest = re.sub(r'^(?:問題|ドメイン)[\s]*[\w\-]+[（\(][^）\)]*[）\)]?\s*', '', line)
                        if rest:
                            q_text = rest
                        continue
                    if line and not line.startswith('<') and not line.startswith('**答え'):
                        if not q_text:
                            q_text = line
                        break
                
                if not q_text:
                    continue
                
                # Get answer from details
                expl_match = re.search(r'<details>.*?<summary>.*?</summary>\s*\n(.+?)</details>', block, re.DOTALL)
                if not expl_match:
                    continue
                explanation = expl_match.group(1).strip()
                explanation = re.sub(r'\*\*(.+?)\*\*', r'\1', explanation)
                
                # Create as "knowledge check" with reveal answer
                questions.append({
                    "id": f"{course_prefix}-{q_id_raw}",
                    "question": q_text,
                    "choices": [
                        {"label": "A", "text": "答えを確認する（下の解説を読む）"}
                    ],
                    "answer": ["A"],
                    "multiSelect": False,
                    "explanation": explanation,
                    "type": "knowledge-check"
                })
    
    return questions


def parse_architect_guide():
    """Parse claude-architect-guide.md into lesson content"""
    with open(f"{SRC}/claude-architect-guide.md", "r") as f:
        content = f.read()
    
    # Split into domain sections
    domains = re.split(r'^## ドメイン', content, flags=re.MULTILINE)
    lessons = []
    
    # Intro section
    intro_end = content.find('## ドメイン')
    if intro_end > 0:
        lessons.append({
            "id": "arc-intro",
            "title": "Claude Certified Architect 概要",
            "content": content[:intro_end].strip(),
            "course": "architect"
        })
    
    for section in domains[1:]:
        # Get domain number and title
        header_match = re.match(r'(\d+):\s*(.+?)(?:\n|（)', section)
        if header_match:
            domain_num = header_match.group(1)
            domain_title = header_match.group(2).strip()
            lessons.append({
                "id": f"arc-d{domain_num}",
                "title": f"ドメイン{domain_num}: {domain_title}",
                "content": f"## ドメイン{section}".strip(),
                "course": "architect"
            })
    
    # Add exam summary
    summary_match = re.search(r'## 試験対策まとめ(.+?)$', content, re.DOTALL)
    if summary_match:
        lessons.append({
            "id": "arc-summary",
            "title": "試験対策まとめ",
            "content": f"## 試験対策まとめ{summary_match.group(1)}".strip(),
            "course": "architect"
        })
    
    return lessons


def parse_courses():
    """Parse anthropic-academy-courses.md into lesson data"""
    with open(f"{SRC}/anthropic-academy-courses.md", "r") as f:
        content = f.read()
    
    # Split by course (## N. ...)
    course_sections = re.split(r'^## \d+\.\s+', content, flags=re.MULTILINE)
    course_headers = re.findall(r'^## \d+\.\s+(.+)$', content, flags=re.MULTILINE)
    
    courses = []
    for i, (header, section) in enumerate(zip(course_headers, course_sections[1:]), 1):
        # Extract metadata
        slug_match = re.search(r'\*\*スラッグ:\*\*\s*(\S+)', section)
        jp_title_match = re.search(r'\*\*日本語タイトル:\*\*\s*(.+)', section)
        desc_match = re.search(r'\*\*説明:\*\*\s*(.+)', section)
        
        slug = slug_match.group(1) if slug_match else f"course-{i}"
        jp_title = jp_title_match.group(1).strip() if jp_title_match else header.strip()
        description = desc_match.group(1).strip() if desc_match else ""
        
        courses.append({
            "id": f"claude-c{i:02d}",
            "slug": slug,
            "title": header.strip(),
            "titleJa": jp_title,
            "description": description,
            "content": section.strip(),
            "order": i
        })
    
    return courses


def main():
    print("=== Parsing Claude study data ===\n")
    
    # 1. Parse quiz questions
    questions = parse_quiz_md()
    print(f"Quiz questions parsed: {len(questions)}")
    
    # Count by prefix
    prefixes = {}
    for q in questions:
        p = q['id'].rsplit('-', 1)[0]
        prefixes[p] = prefixes.get(p, 0) + 1
    for p, c in sorted(prefixes.items()):
        print(f"  {p}: {c}")
    
    # 2. Parse courses
    courses = parse_courses()
    print(f"\nCourses parsed: {len(courses)}")
    for c in courses:
        print(f"  {c['id']}: {c['titleJa']}")
    
    # 3. Parse architect guide into lessons
    arc_lessons = parse_architect_guide()
    print(f"\nArchitect guide lessons: {len(arc_lessons)}")
    for l in arc_lessons:
        print(f"  {l['id']}: {l['title']}")
    
    # 4. Save everything
    # Questions - same format as AWS questions
    with open(f"{DST}/claude-questions.json", "w") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    print(f"\nSaved: {DST}/claude-questions.json ({len(questions)} questions)")
    
    # Courses metadata
    courses_meta = [{
        "id": c["id"],
        "slug": c["slug"],
        "title": c["title"],
        "titleJa": c["titleJa"],
        "description": c["description"],
        "order": c["order"]
    } for c in courses]
    
    # Add architect course
    courses_meta.append({
        "id": "claude-arc",
        "slug": "claude-certified-architect",
        "title": "Claude Certified Architect",
        "titleJa": "Claude Certified Architect 試験対策",
        "description": "5ドメインの知識を網羅したClaude認定アーキテクト試験対策ガイド",
        "order": 14
    })
    
    with open(f"{DST}/claude-courses.json", "w") as f:
        json.dump(courses_meta, f, ensure_ascii=False, indent=2)
    print(f"Saved: {DST}/claude-courses.json ({len(courses_meta)} courses)")
    
    # Lessons content (courses + architect guide)
    all_lessons = []
    for c in courses:
        all_lessons.append({
            "id": c["id"],
            "title": c["titleJa"],
            "content": c["content"],
            "course": c["id"]
        })
    all_lessons.extend(arc_lessons)
    
    with open(f"{DST}/claude-lessons.json", "w") as f:
        json.dump(all_lessons, f, ensure_ascii=False, indent=2)
    print(f"Saved: {DST}/claude-lessons.json ({len(all_lessons)} lessons)")


if __name__ == '__main__':
    main()
