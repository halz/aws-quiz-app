import { NextRequest, NextResponse } from 'next/server';

const historyStore: Array<{
  id: number;
  exam: string;
  chapter: string;
  title: string;
  total: number;
  correct: number;
  duration: number;
  startedAt: number;
}> = [];

let nextId = 1;

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const entry = {
      id: nextId++,
      exam: body.exam,
      chapter: body.chapter,
      title: body.title || body.chapter,
      total: body.total,
      correct: body.correct,
      duration: body.duration,
      startedAt: Date.now(),
    };

    historyStore.unshift(entry);
    if (historyStore.length > 100) historyStore.pop();

    return NextResponse.json({
      success: true,
      message: 'Quiz history saved',
      data: entry,
    });
  } catch (error) {
    console.error('History save error:', error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  try {
    const limit = request.nextUrl.searchParams.get('limit')
      ? parseInt(request.nextUrl.searchParams.get('limit')!)
      : 10;

    const history = historyStore.slice(0, limit);

    return NextResponse.json({
      success: true,
      data: history,
    });
  } catch (error) {
    console.error('History fetch error:', error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
