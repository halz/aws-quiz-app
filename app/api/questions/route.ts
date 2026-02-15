import { NextRequest, NextResponse } from 'next/server';
import questionsData from '@/lib/questions.json';

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    const chapter = request.nextUrl.searchParams.get('chapter');
    const exam = request.nextUrl.searchParams.get('exam');

    if (chapter) {
      const questions = questionsData.filter((q: any) => q.id.split('-')[0] === chapter);
      return NextResponse.json({ success: true, data: questions, count: questions.length });
    }

    if (exam) {
      const questions = questionsData.filter((q: any) => q.id.startsWith(exam));
      return NextResponse.json({ success: true, data: questions, count: questions.length });
    }

    // Return chapter list with counts
    const chapters: Record<string, number> = {};
    questionsData.forEach((q: any) => {
      const ch = q.id.split('-')[0];
      chapters[ch] = (chapters[ch] || 0) + 1;
    });
    return NextResponse.json({ success: true, chapters, totalQuestions: questionsData.length });
  } catch (error) {
    console.error('Questions API error:', error);
    return NextResponse.json({ success: false, error: 'Server error' }, { status: 500 });
  }
}
