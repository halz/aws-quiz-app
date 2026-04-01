#!/usr/bin/env python3
"""Update claude-lessons.json and claude-courses.json from new lesson files"""
import json, os, re, glob

LESSONS_DIR = "/tmp/claude-update/lessons_ja"
DST = "/Users/yoshi/aws-quiz-app/lib"

# Map filename -> course metadata
COURSE_MAP = {
    "02_claude_cowork.md": {
        "id": "claude-c02",
        "slug": "introduction-to-claude-cowork",
        "title": "Introduction to Claude Cowork",
        "titleJa": "Claude Coworkの紹介",
        "order": 2,
    },
    "03_ai_fluency_framework.md": {
        "id": "claude-c03",
        "slug": "ai-fluency-framework-foundations",
        "title": "AI Fluency: Framework & Foundations",
        "titleJa": "AIリテラシー：フレームワークと基礎",
        "order": 3,
    },
    "04_ai_fluency_educators.md": {
        "id": "claude-c04",
        "slug": "ai-fluency-for-educators",
        "title": "AI Fluency for Educators",
        "titleJa": "教育者のためのAIリテラシー",
        "order": 4,
    },
    "05_ai_fluency_students.md": {
        "id": "claude-c05",
        "slug": "ai-fluency-for-students",
        "title": "AI Fluency for Students",
        "titleJa": "学生のためのAIリテラシー",
        "order": 5,
    },
    "06_teaching_ai_fluency.md": {
        "id": "claude-c06",
        "slug": "teaching-ai-fluency",
        "title": "Teaching AI Fluency",
        "titleJa": "AIリテラシーを教える",
        "order": 6,
    },
    "07_claude_101.md": {
        "id": "claude-c07",
        "slug": "claude-101",
        "title": "Claude 101",
        "titleJa": "Claude 101",
        "order": 7,
    },
    "07b_ai_fluency_nonprofits.md": {
        "id": "claude-c07b",
        "slug": "ai-fluency-for-nonprofits",
        "title": "AI Fluency for Nonprofits",
        "titleJa": "非営利団体のためのAIリテラシー",
        "order": 7.5,
    },
    "08_building_with_api.md": {
        "id": "claude-c08",
        "slug": "claude-with-the-anthropic-api",
        "title": "Building with the Claude API",
        "titleJa": "Claude APIで開発する",
        "order": 8,
    },
    "09_claude_with_bedrock.md": {
        "id": "claude-c09",
        "slug": "claude-in-amazon-bedrock",
        "title": "Claude with Amazon Bedrock",
        "titleJa": "Amazon BedrockでClaudeを使う",
        "order": 9,
    },
    "10_claude_with_vertex.md": {
        "id": "claude-c10",
        "slug": "claude-with-google-vertex",
        "title": "Claude with Google Cloud's Vertex AI",
        "titleJa": "Google Cloud Vertex AIでClaudeを使う",
        "order": 10,
    },
    "11_intro_to_mcp.md": {
        "id": "claude-c11",
        "slug": "introduction-to-model-context-protocol",
        "title": "Introduction to Model Context Protocol",
        "titleJa": "Model Context Protocol入門",
        "order": 11,
    },
    "12_mcp_advanced_topics.md": {
        "id": "claude-c12",
        "slug": "model-context-protocol-advanced-topics",
        "title": "Model Context Protocol: Advanced Topics",
        "titleJa": "Model Context Protocol：上級トピック",
        "order": 12,
    },
    "13_claude_code_in_action.md": {
        "id": "claude-c13",
        "slug": "claude-code-in-action",
        "title": "Claude Code in Action",
        "titleJa": "Claude Code 実践",
        "order": 13,
    },
    "14_introduction_to_agent_skills.md": {
        "id": "claude-c14",
        "slug": "introduction-to-agent-skills",
        "title": "Introduction to Agent Skills",
        "titleJa": "エージェントスキル入門",
        "order": 14,
    },
    "15_introduction_to_subagents.md": {
        "id": "claude-c15",
        "slug": "introduction-to-subagents",
        "title": "Introduction to Subagents",
        "titleJa": "サブエージェントの紹介",
        "order": 15,
    },
}


def main():
    # Load existing data
    with open(f"{DST}/claude-courses.json") as f:
        courses = json.load(f)
    with open(f"{DST}/claude-lessons.json") as f:
        lessons = json.load(f)

    existing_course_ids = {c["id"] for c in courses}
    existing_lesson_ids = {l["id"] for l in lessons}

    updated_courses = 0
    updated_lessons = 0
    new_courses = 0
    new_lessons = 0

    for filename, meta in sorted(COURSE_MAP.items()):
        filepath = os.path.join(LESSONS_DIR, filename)
        if not os.path.exists(filepath):
            print(f"⏩ {filename} not found, skipping")
            continue

        with open(filepath, "r") as f:
            content = f.read()

        # Extract description from first paragraph after title
        lines = content.split("\n")
        desc = ""
        for line in lines[2:10]:
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("URL:") and not line.startswith("---"):
                desc = line[:200]
                break

        course_id = meta["id"]

        # Update or add course
        found_course = False
        for c in courses:
            if c["id"] == course_id:
                c["slug"] = meta["slug"]
                c["title"] = meta["title"]
                c["titleJa"] = meta["titleJa"]
                c["order"] = meta["order"]
                if desc:
                    c["description"] = desc
                found_course = True
                updated_courses += 1
                break
        
        if not found_course:
            courses.append({
                "id": course_id,
                "slug": meta["slug"],
                "title": meta["title"],
                "titleJa": meta["titleJa"],
                "description": desc,
                "order": meta["order"],
            })
            new_courses += 1

        # Update or add lesson
        found_lesson = False
        for l in lessons:
            if l["id"] == course_id:
                l["title"] = meta["titleJa"]
                l["content"] = content
                l["course"] = course_id
                found_lesson = True
                updated_lessons += 1
                break
        
        if not found_lesson:
            lessons.append({
                "id": course_id,
                "title": meta["titleJa"],
                "content": content,
                "course": course_id,
            })
            new_lessons += 1

        print(f"{'✅' if found_course else '🆕'} {course_id}: {meta['titleJa']} ({len(content):,} chars)")

    # Sort courses by order
    courses.sort(key=lambda c: c.get("order", 999))
    
    # Save
    with open(f"{DST}/claude-courses.json", "w") as f:
        json.dump(courses, f, ensure_ascii=False, indent=2)
    with open(f"{DST}/claude-lessons.json", "w") as f:
        json.dump(lessons, f, ensure_ascii=False, indent=2)

    print(f"\n=== Summary ===")
    print(f"Courses: {updated_courses} updated, {new_courses} new, {len(courses)} total")
    print(f"Lessons: {updated_lessons} updated, {new_lessons} new, {len(lessons)} total")


if __name__ == "__main__":
    main()
