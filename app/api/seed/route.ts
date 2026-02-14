import { NextRequest, NextResponse } from 'next/server';
import questionsData from '@/lib/questions.json';

export async function GET() {
  const chapters: Record<string, number> = {};
  questionsData.forEach((q: any) => {
    const ch = q.id.split('-')[0];
    chapters[ch] = (chapters[ch] || 0) + 1;
  });
  return NextResponse.json({
    success: true,
    totalQuestions: questionsData.length,
    totalChapters: Object.keys(chapters).length,
    chapters
  });
}

export async function POST() {
  return NextResponse.json({ success: true, message: 'No seeding needed - questions loaded from static data', count: questionsData.length });
}
