import { NextRequest, NextResponse } from 'next/server';
import coursesData from '@/lib/claude-courses.json';
import lessonsData from '@/lib/claude-lessons.json';
import questionsData from '@/lib/claude-questions.json';

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    const type = request.nextUrl.searchParams.get('type');
    const courseId = request.nextUrl.searchParams.get('course');

    if (type === 'courses') {
      return NextResponse.json({ success: true, data: coursesData });
    }

    if (type === 'lesson' && courseId) {
      const lesson = (lessonsData as any[]).find((l: any) => l.id === courseId || l.course === courseId);
      return NextResponse.json({ success: true, data: lesson || null });
    }

    if (type === 'quiz' && courseId) {
      // Map course IDs to question prefixes
      let prefix = courseId;
      if (courseId === 'claude-arc' || courseId === 'architect') {
        prefix = 'claude-arc';
      }
      const questions = (questionsData as any[]).filter((q: any) => q.id.startsWith(prefix));
      return NextResponse.json({ success: true, data: questions, count: questions.length });
    }

    if (type === 'all-quiz') {
      return NextResponse.json({ success: true, data: questionsData, count: (questionsData as any[]).length });
    }

    // Default: return summary
    const quizCount: Record<string, number> = {};
    (questionsData as any[]).forEach((q: any) => {
      const parts = q.id.split('-');
      const prefix = parts.slice(0, -1).join('-');
      const coursePrefix = prefix.replace(/-\w+$/, '');
      quizCount[coursePrefix] = (quizCount[coursePrefix] || 0) + 1;
    });

    return NextResponse.json({
      success: true,
      courses: (coursesData as any[]).length,
      lessons: (lessonsData as any[]).length,
      questions: (questionsData as any[]).length,
      quizCount
    });
  } catch (error) {
    console.error('Claude API error:', error);
    return NextResponse.json({ success: false, error: 'Server error' }, { status: 500 });
  }
}
