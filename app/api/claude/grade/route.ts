import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest) {
  try {
    const { question, correctAnswer, userAnswer } = await request.json();

    if (!question || !correctAnswer || !userAnswer) {
      return NextResponse.json({ success: false, error: 'Missing fields' }, { status: 400 });
    }

    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) {
      // Fallback: simple keyword matching if no API key
      return NextResponse.json({
        success: true,
        result: {
          grade: 'unknown',
          score: 0,
          feedback: 'API key not configured. 模範解答と比較して自己採点してください。',
          modelAnswer: correctAnswer
        }
      });
    }

    const systemPrompt = `あなたは学習コンテンツの採点AIです。
ユーザーの回答を模範解答と比較して採点してください。

採点基準:
- "correct": 模範解答の核心的なポイントをカバーしている（完全一致は不要、要点が合っていればOK）
- "partial": 一部正しいが重要なポイントが欠けている
- "incorrect": 根本的に間違っている、または的外れ

JSON形式で返してください:
{
  "grade": "correct" | "partial" | "incorrect",
  "score": 0-100,
  "feedback": "日本語でのフィードバック（良かった点・足りない点）"
}`;

    const userMessage = `## 問題
${question}

## 模範解答
${correctAnswer}

## ユーザーの回答
${userAnswer}

上記を採点してJSON形式で返してください。`;

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 1024,
        system: systemPrompt,
        messages: [{ role: 'user', content: userMessage }],
      }),
    });

    if (!response.ok) {
      const errText = await response.text();
      console.error('Anthropic API error:', errText);
      return NextResponse.json({
        success: true,
        result: {
          grade: 'unknown',
          score: 0,
          feedback: 'AI採点でエラーが発生しました。模範解答と比較して自己採点してください。',
          modelAnswer: correctAnswer
        }
      });
    }

    const data = await response.json();
    const aiText = data.content?.[0]?.text || '';

    // Parse JSON from response
    const jsonMatch = aiText.match(/\{[\s\S]*?\}/);
    if (jsonMatch) {
      try {
        const result = JSON.parse(jsonMatch[0]);
        return NextResponse.json({
          success: true,
          result: {
            grade: result.grade || 'unknown',
            score: result.score || 0,
            feedback: result.feedback || '',
            modelAnswer: correctAnswer
          }
        });
      } catch {
        // If JSON parse fails, return raw text as feedback
      }
    }

    return NextResponse.json({
      success: true,
      result: {
        grade: 'unknown',
        score: 0,
        feedback: aiText || '採点結果を解析できませんでした。',
        modelAnswer: correctAnswer
      }
    });

  } catch (error) {
    console.error('Grade API error:', error);
    return NextResponse.json({ success: false, error: 'Server error' }, { status: 500 });
  }
}
