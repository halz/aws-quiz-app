'use client';

export const dynamic = 'force-dynamic';

import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

interface Course {
  id: string;
  slug: string;
  title: string;
  titleJa: string;
  description: string;
  order: number;
}

interface Lesson {
  id: string;
  title: string;
  content: string;
  course: string;
}

interface Choice {
  label: string;
  text: string;
}

interface Question {
  id: string;
  question: string;
  choices: Choice[];
  answer: string[];
  multiSelect: boolean;
  explanation: string;
  type?: string;
}

type Screen = 'home' | 'course-list' | 'lesson' | 'quiz-select' | 'quiz' | 'completion';

const CHOICE_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  A: { bg: '#1e3a8a', text: '#60a5fa', border: '#3b82f6' },
  B: { bg: '#78350f', text: '#f59e0b', border: '#f59e0b' },
  C: { bg: '#064e3b', text: '#10b981', border: '#10b981' },
  D: { bg: '#4c1d95', text: '#c084fc', border: '#8b5cf6' },
  E: { bg: '#831843', text: '#f472b6', border: '#ec4899' },
};

const SECTIONS = [
  { id: 'courses', label: '📚 コース学習', desc: 'Anthropic Academy 全13コースのカリキュラム', icon: '📚' },
  { id: 'architect', label: '🏛️ Architect試験対策', desc: 'Claude Certified Architect ガイド（5ドメイン）', icon: '🏛️' },
  { id: 'quiz', label: '✍️ 問題集', desc: 'コース理解確認問題 + Architect試験問題', icon: '✍️' },
];

export default function ClaudePage() {
  const [screen, setScreen] = useState<Screen>('home');
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [quizState, setQuizState] = useState({
    currentQuestion: 0,
    answers: {} as Record<number, string[]>,
    submitted: {} as Record<number, boolean>,
    startTime: 0,
  });
  const [elapsedTime, setElapsedTime] = useState(0);
  const [loading, setLoading] = useState(false);
  const [activeSection, setActiveSection] = useState<string | null>(null);
  const [arcLessons, setArcLessons] = useState<Lesson[]>([]);

  useEffect(() => {
    if (screen !== 'quiz' || quizState.startTime === 0) return;
    const timer = setInterval(() => {
      setElapsedTime(Math.floor((Date.now() - quizState.startTime) / 1000));
    }, 1000);
    return () => clearInterval(timer);
  }, [screen, quizState.startTime]);

  const loadCourses = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/claude?type=courses');
      const data = await res.json();
      if (data.success) setCourses(data.data);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const loadLesson = async (courseId: string) => {
    setLoading(true);
    try {
      const res = await fetch(`/api/claude?type=lesson&course=${courseId}`);
      const data = await res.json();
      if (data.success && data.data) {
        setLesson(data.data);
        setScreen('lesson');
      }
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const loadQuiz = async (courseId: string) => {
    setLoading(true);
    try {
      const url = courseId === 'all' ? '/api/claude?type=all-quiz' : `/api/claude?type=quiz&course=${courseId}`;
      const res = await fetch(url);
      const data = await res.json();
      if (data.success && data.data.length > 0) {
        setQuestions(data.data);
        setQuizState({ currentQuestion: 0, answers: {}, submitted: {}, startTime: Date.now() });
        setElapsedTime(0);
        setScreen('quiz');
      }
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const handleAnswerSelect = (label: string) => {
    if (quizState.submitted[quizState.currentQuestion]) return;
    const current = questions[quizState.currentQuestion];
    if (!current.multiSelect) {
      setQuizState(prev => ({ ...prev, answers: { ...prev.answers, [prev.currentQuestion]: [label] } }));
    } else {
      const curr = quizState.answers[quizState.currentQuestion] || [];
      const next = curr.includes(label) ? curr.filter(a => a !== label) : [...curr, label].sort();
      setQuizState(prev => ({ ...prev, answers: { ...prev.answers, [prev.currentQuestion]: next } }));
    }
  };

  const handleSubmit = () => {
    if ((quizState.answers[quizState.currentQuestion] || []).length === 0) return;
    setQuizState(prev => ({ ...prev, submitted: { ...prev.submitted, [prev.currentQuestion]: true } }));
  };

  const isCorrect = (idx: number) => {
    const q = questions[idx];
    const user = quizState.answers[idx] || [];
    const correct = [...q.answer].sort();
    return user.length === correct.length && user.every(a => correct.includes(a));
  };

  const formatTime = (s: number) => {
    const m = Math.floor(s / 60); const sec = s % 60;
    return `${m}分${sec}秒`;
  };

  // Home screen
  if (screen === 'home') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-950 via-slate-900 to-slate-950 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="mb-4">
            <a href="/" className="text-orange-400 hover:text-orange-300 transition-colors">← AWS認定試験に戻る</a>
          </div>
          <div className="text-center mb-12">
            <h1 className="text-5xl font-bold mb-4" style={{ background: 'linear-gradient(135deg, #f97316, #fb923c, #fbbf24)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              Claude 学習センター
            </h1>
            <p className="text-gray-400 text-lg">Anthropic Academy & Claude Certified Architect</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
            {SECTIONS.map(sec => (
              <button
                key={sec.id}
                onClick={() => {
                  setActiveSection(sec.id);
                  if (sec.id === 'courses') {
                    loadCourses();
                    setScreen('course-list');
                  } else if (sec.id === 'architect') {
                    // Load architect lessons list
                    loadArchitectLessons();
                  } else if (sec.id === 'quiz') {
                    loadCourses();
                    setScreen('quiz-select');
                  }
                }}
                className="group p-8 rounded-xl border border-orange-900/50 bg-slate-800/80 hover:bg-slate-700/80 hover:border-orange-500/50 transition-all duration-300 text-left"
              >
                <div className="text-5xl mb-4">{sec.icon}</div>
                <h2 className="text-2xl font-bold text-white mb-2 group-hover:text-orange-400">{sec.label}</h2>
                <p className="text-gray-400">{sec.desc}</p>
              </button>
            ))}
          </div>

          <div className="bg-slate-800/60 border border-slate-700 rounded-xl p-8">
            <h3 className="text-xl font-bold text-white mb-4">📋 コンテンツ概要</h3>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div className="bg-slate-700/50 rounded-lg p-4">
                <div className="text-3xl font-bold text-orange-400">13</div>
                <div className="text-gray-400 text-sm">Academyコース</div>
              </div>
              <div className="bg-slate-700/50 rounded-lg p-4">
                <div className="text-3xl font-bold text-orange-400">5</div>
                <div className="text-gray-400 text-sm">Architectドメイン</div>
              </div>
              <div className="bg-slate-700/50 rounded-lg p-4">
                <div className="text-3xl font-bold text-orange-400">52</div>
                <div className="text-gray-400 text-sm">問題数</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Course list
  if (screen === 'course-list') {
    const academyCourses = courses.filter(c => c.id !== 'claude-arc');
    const arcCourse = courses.find(c => c.id === 'claude-arc');
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-950 via-slate-900 to-slate-950 p-8">
        <div className="max-w-6xl mx-auto">
          <button onClick={() => setScreen('home')} className="mb-8 text-orange-400 hover:text-orange-300 transition-colors">← 戻る</button>
          <h1 className="text-4xl font-bold mb-2" style={{ background: 'linear-gradient(135deg, #f97316, #fb923c)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            📚 Anthropic Academy コース
          </h1>
          <p className="text-gray-400 mb-8">コースを選んでカリキュラムを閲覧</p>

          {loading ? (
            <div className="text-center py-12"><div className="text-2xl text-gray-400">読み込み中...</div></div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                {academyCourses.map(course => (
                  <button
                    key={course.id}
                    onClick={() => { setSelectedCourse(course); loadLesson(course.id); }}
                    className="p-6 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 hover:border-orange-500/50 transition-all text-left"
                  >
                    <div className="flex items-start gap-4">
                      <div className="text-2xl font-bold text-orange-400 opacity-50">{course.order}</div>
                      <div>
                        <h3 className="text-lg font-semibold text-white mb-1">{course.titleJa}</h3>
                        <p className="text-sm text-gray-500">{course.title}</p>
                        {course.description && <p className="text-sm text-gray-400 mt-2">{course.description.substring(0, 100)}...</p>}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
              {arcCourse && (
                <div className="border-t border-slate-700 pt-6">
                  <button
                    onClick={() => { setSelectedCourse(arcCourse); loadLesson('claude-arc'); }}
                    className="w-full p-6 rounded-lg border-2 border-orange-600/30 bg-gradient-to-r from-orange-950/50 to-slate-800 hover:border-orange-500/50 transition-all text-left"
                  >
                    <div className="flex items-start gap-4">
                      <div className="text-3xl">🏛️</div>
                      <div>
                        <h3 className="text-xl font-bold text-orange-400 mb-1">{arcCourse.titleJa}</h3>
                        <p className="text-gray-400">{arcCourse.description}</p>
                      </div>
                    </div>
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    );
  }

  // Lesson view
  if (screen === 'lesson' && lesson) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-950 via-slate-900 to-slate-950 p-8">
        <div className="max-w-4xl mx-auto">
          <button onClick={() => { setActiveSection === 'architect' ? setScreen('home') : setScreen('course-list'); }} className="mb-8 text-orange-400 hover:text-orange-300 transition-colors">← 戻る</button>
          <h1 className="text-3xl font-bold text-white mb-8">{lesson.title}</h1>
          <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-8 prose prose-invert max-w-none
            prose-headings:text-orange-400 prose-strong:text-orange-300
            prose-h2:text-2xl prose-h2:mt-8 prose-h2:mb-4 prose-h2:border-b prose-h2:border-slate-700 prose-h2:pb-2
            prose-h3:text-xl prose-h3:mt-6 prose-h3:mb-3
            prose-p:text-gray-300 prose-p:leading-relaxed
            prose-li:text-gray-300
            prose-code:text-orange-300 prose-code:bg-slate-900 prose-code:px-1 prose-code:rounded
            prose-pre:bg-slate-900 prose-pre:border prose-pre:border-slate-700
            prose-table:border-collapse
            prose-th:bg-slate-700 prose-th:p-2 prose-th:text-left prose-th:border prose-th:border-slate-600
            prose-td:p-2 prose-td:border prose-td:border-slate-700 prose-td:text-gray-300
            prose-a:text-orange-400 prose-a:no-underline hover:prose-a:underline
            prose-blockquote:border-orange-500 prose-blockquote:text-gray-400
          ">
            <ReactMarkdown>{lesson.content}</ReactMarkdown>
          </div>
          <div className="mt-8 flex gap-4 justify-center">
            <button onClick={() => setScreen('course-list')} className="px-6 py-3 rounded-lg bg-slate-700 hover:bg-slate-600 text-white font-semibold transition-colors">コース一覧に戻る</button>
            {selectedCourse && (
              <button onClick={() => loadQuiz(selectedCourse.id)} className="px-6 py-3 rounded-lg bg-orange-600 hover:bg-orange-500 text-white font-semibold transition-colors">
                このコースの問題を解く ✍️
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Quiz select
  if (screen === 'quiz-select') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-950 via-slate-900 to-slate-950 p-8">
        <div className="max-w-4xl mx-auto">
          <button onClick={() => setScreen('home')} className="mb-8 text-orange-400 hover:text-orange-300 transition-colors">← 戻る</button>
          <h1 className="text-4xl font-bold mb-2" style={{ background: 'linear-gradient(135deg, #f97316, #fb923c)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            ✍️ 問題集
          </h1>
          <p className="text-gray-400 mb-8">コースまたはカテゴリを選んで問題を解く</p>

          <button
            onClick={() => loadQuiz('all')}
            className="w-full mb-6 p-6 rounded-lg border-2 border-orange-600/30 bg-gradient-to-r from-orange-950/50 to-slate-800 hover:border-orange-500/50 transition-all text-left"
          >
            <h3 className="text-xl font-bold text-orange-400">🔥 全問チャレンジ（52問）</h3>
            <p className="text-gray-400 mt-1">全コース + Architect試験の問題をまとめて解く</p>
          </button>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            {courses.filter(c => c.id !== 'claude-arc').map(course => (
              <button
                key={course.id}
                onClick={() => loadQuiz(course.id)}
                className="p-5 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 hover:border-orange-500/50 transition-all text-left"
              >
                <h3 className="font-semibold text-white">{course.titleJa}</h3>
                <p className="text-sm text-gray-500 mt-1">コース{course.order}の問題</p>
              </button>
            ))}
          </div>

          <button
            onClick={() => loadQuiz('claude-arc')}
            className="w-full p-6 rounded-lg border-2 border-orange-600/30 bg-gradient-to-r from-orange-950/50 to-slate-800 hover:border-orange-500/50 transition-all text-left"
          >
            <h3 className="text-xl font-bold text-orange-400">🏛️ Architect試験問題</h3>
            <p className="text-gray-400 mt-1">5ドメインのシナリオベース問題</p>
          </button>
        </div>
      </div>
    );
  }

  // Quiz
  if (screen === 'quiz' && questions.length > 0) {
    const current = questions[quizState.currentQuestion];
    const userAnswers = quizState.answers[quizState.currentQuestion] || [];
    const isSubmitted = quizState.submitted[quizState.currentQuestion];
    const correct = isCorrect(quizState.currentQuestion);
    const progress = ((quizState.currentQuestion + 1) / questions.length) * 100;

    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-950 via-slate-900 to-slate-950 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <div className="flex justify-between items-center mb-4">
              <div className="flex items-center gap-4">
                <button onClick={() => setScreen('quiz-select')} className="text-gray-400 hover:text-gray-300">← 戻る</button>
                <span className="text-gray-400">問題 {quizState.currentQuestion + 1} / {questions.length}</span>
              </div>
              <div className="text-right">
                <div className="text-gray-400 text-sm">経過時間</div>
                <div className="text-xl font-semibold text-white">{formatTime(elapsedTime)}</div>
              </div>
            </div>
            <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-orange-500 to-amber-400 transition-all duration-300" style={{ width: `${progress}%` }} />
            </div>
          </div>

          <div className="bg-slate-800 border border-slate-700 rounded-lg p-8 mb-8">
            {current.type === 'knowledge-check' && (
              <div className="mb-4 px-3 py-1 bg-orange-900/30 border border-orange-700/50 rounded-full inline-block text-orange-400 text-sm">💡 知識チェック</div>
            )}
            <h2 className="text-2xl font-semibold text-white mb-6 leading-relaxed">{current.question}</h2>
            
            {current.type !== 'knowledge-check' ? (
              <div className="space-y-4">
                {current.choices.map(choice => {
                  const colors = CHOICE_COLORS[choice.label] || CHOICE_COLORS.A;
                  const isSelected = userAnswers.includes(choice.label);
                  const isCorrectChoice = current.answer.includes(choice.label);
                  return (
                    <button
                      key={choice.label}
                      onClick={() => handleAnswerSelect(choice.label)}
                      disabled={isSubmitted}
                      className={`w-full p-6 rounded-lg border-2 text-left transition-all ${
                        isSubmitted
                          ? isCorrectChoice ? 'border-green-500 bg-slate-700' : isSelected ? 'border-red-500 bg-slate-700' : 'border-slate-600 bg-slate-800'
                          : isSelected ? 'ring-2 ring-offset-2 ring-orange-400 border-orange-400' : 'border-slate-600 hover:border-orange-400/50'
                      } disabled:opacity-75`}
                    >
                      <div className="flex items-start gap-4">
                        <div className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center font-bold text-white" style={{ backgroundColor: colors.border }}>{choice.label}</div>
                        <div className="flex-grow">
                          <p className="text-white">{choice.text}</p>
                          {isSubmitted && isCorrectChoice && <p className="text-green-400 text-sm mt-2">✅ 正解</p>}
                          {isSubmitted && isSelected && !isCorrectChoice && <p className="text-red-400 text-sm mt-2">❌ 不正解</p>}
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            ) : (
              <button
                onClick={() => {
                  setQuizState(prev => ({
                    ...prev,
                    answers: { ...prev.answers, [prev.currentQuestion]: ['A'] },
                    submitted: { ...prev.submitted, [prev.currentQuestion]: true }
                  }));
                }}
                disabled={isSubmitted}
                className="px-8 py-4 rounded-lg bg-orange-600 hover:bg-orange-500 disabled:bg-slate-600 text-white font-semibold transition-all"
              >
                {isSubmitted ? '👇 解説を確認' : '答えを見る 👀'}
              </button>
            )}

            {isSubmitted && current.explanation && (
              <div className={`mt-8 p-6 rounded-lg border-l-4 ${
                current.type === 'knowledge-check' ? 'bg-slate-700 border-orange-500' :
                correct ? 'bg-slate-700 border-green-500' : 'bg-slate-700 border-red-500'
              }`}>
                <div className={`font-semibold mb-2 ${
                  current.type === 'knowledge-check' ? 'text-orange-400' :
                  correct ? 'text-green-400' : 'text-red-400'
                }`}>
                  {current.type === 'knowledge-check' ? '📖 解説' : correct ? '🎉 正解です！' : '💡 解説'}
                </div>
                <div className="text-gray-200 whitespace-pre-wrap">{current.explanation}</div>
              </div>
            )}
          </div>

          <div className="flex gap-4 justify-between items-center">
            <button
              onClick={() => quizState.currentQuestion > 0 && setQuizState(prev => ({ ...prev, currentQuestion: prev.currentQuestion - 1 }))}
              disabled={quizState.currentQuestion === 0}
              className="px-6 py-3 rounded-lg bg-slate-700 hover:bg-slate-600 disabled:opacity-50 text-white font-semibold transition-colors"
            >← 前の問題</button>

            {!isSubmitted && current.type !== 'knowledge-check' ? (
              <button onClick={handleSubmit} disabled={userAnswers.length === 0} className="px-8 py-3 rounded-lg bg-orange-600 hover:bg-orange-500 disabled:opacity-50 text-white font-semibold transition-all">
                回答する
              </button>
            ) : quizState.currentQuestion === questions.length - 1 ? (
              <button onClick={() => setScreen('completion')} className="px-8 py-3 rounded-lg bg-orange-600 hover:bg-orange-500 text-white font-semibold transition-all">
                完了
              </button>
            ) : (
              <button
                onClick={() => setQuizState(prev => ({ ...prev, currentQuestion: prev.currentQuestion + 1 }))}
                className="px-6 py-3 rounded-lg bg-orange-600 hover:bg-orange-500 text-white font-semibold transition-all"
              >次の問題 →</button>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Completion
  if (screen === 'completion') {
    let correct = 0;
    questions.forEach((_, idx) => { if (isCorrect(idx)) correct++; });
    const pct = Math.round((correct / questions.length) * 100);

    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-950 via-slate-900 to-slate-950 p-8">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl font-bold mb-8" style={{ background: 'linear-gradient(135deg, #f97316, #fb923c)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            クイズ完了！ 🎉
          </h1>
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-8 mb-8">
            <div className="text-6xl font-bold text-orange-400 mb-4">{pct}%</div>
            <div className="text-2xl font-semibold text-white mb-4">{correct} / {questions.length} 問正解</div>
            <div className="text-gray-400">経過時間: {formatTime(elapsedTime)}</div>
            <div className="mt-6 w-full h-3 bg-slate-900 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-orange-500 to-amber-400" style={{ width: `${pct}%` }} />
            </div>
          </div>
          <div className="flex gap-4 justify-center">
            <button onClick={() => setScreen('quiz-select')} className="px-8 py-3 rounded-lg bg-slate-700 hover:bg-slate-600 text-white font-semibold transition-colors">問題一覧に戻る</button>
            <button onClick={() => setScreen('home')} className="px-8 py-3 rounded-lg bg-orange-600 hover:bg-orange-500 text-white font-semibold transition-colors">ホームに戻る</button>
          </div>
        </div>
      </div>
    );
  }

  // Fallback
  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-950 via-slate-900 to-slate-950 p-8 flex items-center justify-center">
      <div className="text-gray-400 text-xl">読み込み中...</div>
    </div>
  );

  // Helper function (hoisted)
  function loadArchitectLessons() {
    setLoading(true);
    fetch('/api/claude?type=lesson&course=claude-arc')
      .then(r => r.json())
      .then(data => {
        if (data.success && data.data) {
          setLesson(data.data);
          setScreen('lesson');
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }
}
