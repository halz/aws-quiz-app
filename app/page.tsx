'use client';

export const dynamic = 'force-dynamic';

import { useState, useEffect } from 'react';
import { Question, ExamInfo, ChapterInfo } from '@/lib/types';

type Screen = 'exam-selection' | 'chapter-selection' | 'quiz' | 'completion';

interface QuizState {
  currentQuestion: number;
  answers: Record<number, string[]>;
  submitted: Record<number, boolean>;
  startTime: number;
}

const EXAMS: ExamInfo[] = [
  { code: 'clf', name: 'AWS Cloud Practitioner (CLF-C02)', icon: '☁️', chapters: 35 },
  { code: 'aif', name: 'AWS AI Practitioner (AIF-C01)', icon: '🤖', chapters: 45 },
  { code: 'saa', name: 'AWS Solutions Architect Associate (SAA-C03)', icon: '🏗️', chapters: 105 },
  { code: 'soa', name: 'AWS SysOps Administrator (SOA-C02)', icon: '⚙️', chapters: 100 },
];

const CHOICE_COLORS: Record<string, { bg: string; text: string; border: string; bgHover: string }> = {
  A: { bg: '#1e3a8a', text: '#60a5fa', border: '#3b82f6', bgHover: '#1e40af' },
  B: { bg: '#78350f', text: '#f59e0b', border: '#f59e0b', bgHover: '#92400e' },
  C: { bg: '#064e3b', text: '#10b981', border: '#10b981', bgHover: '#065f46' },
  D: { bg: '#4c1d95', text: '#c084fc', border: '#8b5cf6', bgHover: '#581c87' },
  E: { bg: '#831843', text: '#f472b6', border: '#ec4899', bgHover: '#9d174d' },
};

export default function QuizApp() {
  const [screen, setScreen] = useState<Screen>('exam-selection');
  const [selectedExam, setSelectedExam] = useState<string | null>(null);
  const [selectedChapter, setSelectedChapter] = useState<string | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [shuffle, setShuffle] = useState(false);
  const [quizState, setQuizState] = useState<QuizState>({
    currentQuestion: 0,
    answers: {},
    submitted: {},
    startTime: 0,
  });
  const [elapsedTime, setElapsedTime] = useState(0);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (screen !== 'quiz' || quizState.startTime === 0) return;
    const timer = setInterval(() => {
      setElapsedTime(Math.floor((Date.now() - quizState.startTime) / 1000));
    }, 1000);
    return () => clearInterval(timer);
  }, [screen, quizState.startTime]);

  const getChapters = (): ChapterInfo[] => {
    if (!selectedExam) return [];
    const exam = EXAMS.find((e) => e.code === selectedExam);
    if (!exam) return [];
    const chapters: ChapterInfo[] = [];
    for (let i = 1; i <= exam.chapters; i++) {
      const code = selectedExam + String(i).padStart(2, '0');
      chapters.push({ id: code, exam: selectedExam, num: i, name: exam.code.toUpperCase() + ' - Chapter ' + i });
    }
    return chapters;
  };

  const handleExamSelect = (examCode: string) => { setSelectedExam(examCode); setScreen('chapter-selection'); };

  const handleChapterSelect = async (chapterCode: string) => {
    setLoading(true);
    try {
      const response = await fetch('/api/questions?chapter=' + chapterCode);
      const result = await response.json();
      let questionsToUse = result.data || [];
      if (shuffle) questionsToUse = [...questionsToUse].sort(() => Math.random() - 0.5);
      setQuestions(questionsToUse);
      setSelectedChapter(chapterCode);
      setQuizState({ currentQuestion: 0, answers: {}, submitted: {}, startTime: Date.now() });
      setElapsedTime(0);
      setScreen('quiz');
    } catch (error) { console.error('Error loading questions:', error); }
    finally { setLoading(false); }
  };

  const handleAnswerSelect = (choiceLabel: string) => {
    if (quizState.submitted[quizState.currentQuestion]) return;
    const current = questions[quizState.currentQuestion];
    if (!current.multiSelect) {
      setQuizState((prev) => ({ ...prev, answers: { ...prev.answers, [prev.currentQuestion]: [choiceLabel] } }));
    } else {
      const currentAnswers = quizState.answers[quizState.currentQuestion] || [];
      const newAnswers = currentAnswers.includes(choiceLabel) ? currentAnswers.filter((a) => a !== choiceLabel) : [...currentAnswers, choiceLabel].sort();
      setQuizState((prev) => ({ ...prev, answers: { ...prev.answers, [prev.currentQuestion]: newAnswers } }));
    }
  };

  const handleSubmitAnswer = () => {
    const answer = quizState.answers[quizState.currentQuestion] || [];
    if (answer.length === 0) return;
    setQuizState((prev) => ({ ...prev, submitted: { ...prev.submitted, [prev.currentQuestion]: true } }));
  };

  const handleNextQuestion = () => { if (quizState.currentQuestion < questions.length - 1) setQuizState((prev) => ({ ...prev, currentQuestion: prev.currentQuestion + 1 })); };
  const handlePreviousQuestion = () => { if (quizState.currentQuestion > 0) setQuizState((prev) => ({ ...prev, currentQuestion: prev.currentQuestion - 1 })); };
  const handleGoToQuestion = (index: number) => { setQuizState((prev) => ({ ...prev, currentQuestion: index })); };
  const handleQuizCompletion = () => { setScreen('completion'); };
  const handleRedoQuiz = () => { if (!selectedChapter) return; handleChapterSelect(selectedChapter); };
  const handleShuffleAndReset = () => { setShuffle(!shuffle); setScreen('chapter-selection'); setSelectedChapter(null); setQuestions([]); setQuizState({ currentQuestion: 0, answers: {}, submitted: {}, startTime: 0 }); };

  const getNextChapter = (): string | null => {
    if (!selectedChapter || !selectedExam) return null;
    const exam = EXAMS.find((e) => e.code === selectedExam);
    if (!exam) return null;
    const currentNum = parseInt(selectedChapter.replace(selectedExam, ''), 10);
    if (currentNum >= exam.chapters) return null;
    return selectedExam + String(currentNum + 1).padStart(2, '0');
  };

  const handleNextChapter = () => {
    const nextChapter = getNextChapter();
    if (nextChapter) handleChapterSelect(nextChapter);
  };

  const isAnswerCorrect = (questionIndex: number): boolean => {
    const question = questions[questionIndex];
    const userAnswer = quizState.answers[questionIndex] || [];
    const correctAnswer = [...question.answer].sort();
    return userAnswer.length === correctAnswer.length && userAnswer.every((a) => correctAnswer.includes(a));
  };

  const formatTime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    if (hours > 0) return hours + '時間' + minutes + '分' + secs + '秒';
    return minutes + '分' + secs + '秒';
  };

  const calculateStats = () => {
    let correct = 0; let incorrect = 0;
    const incorrectQuestions: (Question & { index: number })[] = [];
    questions.forEach((q, idx) => {
      if (isAnswerCorrect(idx)) correct++;
      else { incorrect++; incorrectQuestions.push({ ...q, index: idx }); }
    });
    return { correct, incorrect, incorrectQuestions };
  };

  if (screen === 'exam-selection') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-950 p-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-5xl font-bold text-center gradient-text mb-4">AWS 認定試験対策</h1>
          <p className="text-center text-gray-400 mb-12 text-lg">あなたの認定資格取得をサポートします</p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {EXAMS.map((exam) => (
              <button key={exam.code} onClick={() => handleExamSelect(exam.code)} className="group relative p-6 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 transition-all duration-300 transform hover:scale-105">
                <div className="text-5xl mb-4">{exam.icon}</div>
                <h2 className="text-xl font-semibold mb-2 text-white group-hover:text-blue-400">{exam.code.toUpperCase()}</h2>
                <p className="text-sm text-gray-400 mb-3">{exam.name}</p>
                <p className="text-xs text-gray-500">{exam.chapters} チャプター</p>
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (screen === 'chapter-selection') {
    const chapters = getChapters();
    const exam = EXAMS.find((e) => e.code === selectedExam);
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-950 p-8">
        <div className="max-w-6xl mx-auto">
          <button onClick={() => setScreen('exam-selection')} className="mb-8 flex items-center gap-2 text-blue-400 hover:text-blue-300 transition-colors">← 戻る</button>
          <h1 className="text-4xl font-bold mb-2 gradient-text">{exam?.icon} {exam?.name}</h1>
          <p className="text-gray-400 mb-8">チャプターを選択してください</p>
          <div className="flex items-center gap-4 mb-8">
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" checked={shuffle} onChange={(e) => setShuffle(e.target.checked)} className="w-4 h-4" />
              <span className="text-gray-300">シャッフルモード</span>
            </label>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
            {chapters.map((chapter) => (
              <button key={chapter.id} onClick={() => handleChapterSelect(chapter.id)} disabled={loading} className="p-4 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 hover:border-blue-500 transition-all text-center font-semibold text-white disabled:opacity-50">{chapter.num}</button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (screen === 'quiz' && questions.length > 0) {
    const current = questions[quizState.currentQuestion];
    const userAnswers = quizState.answers[quizState.currentQuestion] || [];
    const isSubmitted = quizState.submitted[quizState.currentQuestion];
    const correct = isAnswerCorrect(quizState.currentQuestion);
    const progressPercent = ((quizState.currentQuestion + 1) / questions.length) * 100;
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-950 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <div className="flex justify-between items-center mb-4">
              <div className="flex items-center gap-4">
                <button onClick={() => setScreen('chapter-selection')} className="text-gray-400 hover:text-gray-300 transition-colors">← 戻る</button>
                <span className="text-gray-400">問題 {quizState.currentQuestion + 1} / {questions.length}</span>
              </div>
              <div className="text-right">
                <div className="text-gray-400 text-sm">経過時間</div>
                <div className="text-xl font-semibold text-white">{formatTime(elapsedTime)}</div>
              </div>
            </div>
            <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden mb-4">
              <div className="h-full gradient-bar transition-all duration-300" style={{ width: progressPercent + '%' }} />
            </div>
            {questions.length <= 20 && (
              <div className="flex flex-wrap gap-2">
                {questions.map((_, idx) => (
                  <button key={idx} onClick={() => handleGoToQuestion(idx)} className={'w-8 h-8 rounded-full font-semibold transition-all ' + (idx === quizState.currentQuestion ? 'bg-blue-500 text-white ring-2 ring-blue-400' : quizState.submitted[idx] ? (isAnswerCorrect(idx) ? 'bg-green-600 text-white' : 'bg-red-600 text-white') : 'bg-slate-700 text-gray-300 hover:bg-slate-600')}>{idx + 1}</button>
                ))}
              </div>
            )}
          </div>
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-8 mb-8">
            <h2 className="text-2xl font-semibold text-white mb-6 leading-relaxed">{current.question}</h2>
            <div className="space-y-4">
              {current.choices.map((choice) => {
                const colors = CHOICE_COLORS[choice.label];
                const isSelected = userAnswers.includes(choice.label);
                const isCorrectChoice = current.answer.includes(choice.label);
                let choiceStyle = 'border ' + colors.border;
                if (isSubmitted) {
                  if (isCorrectChoice) choiceStyle = 'border-green-500 bg-slate-700';
                  else if (isSelected && !isCorrectChoice) choiceStyle = 'border-red-500 bg-slate-700';
                }
                return (
                  <button key={choice.label} onClick={() => handleAnswerSelect(choice.label)} disabled={isSubmitted} className={'w-full p-6 rounded-lg border-2 text-left transition-all ' + choiceStyle + ' ' + (isSelected && !isSubmitted ? 'ring-2 ring-offset-2 ring-blue-400' : '') + ' disabled:opacity-75'}>
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
            {isSubmitted && (
              <div className={'mt-8 p-6 rounded-lg border-l-4 ' + (correct ? 'bg-slate-700 border-green-500' : 'bg-slate-700 border-red-500')}>
                <div className={'font-semibold mb-2 ' + (correct ? 'text-green-400' : 'text-red-400')}>{correct ? '🎉 正解です！' : '💡 解説'}</div>
                <p className="text-gray-200">{current.explanation}</p>
              </div>
            )}
          </div>
          <div className="flex gap-4 justify-between items-center">
            <button onClick={handlePreviousQuestion} disabled={quizState.currentQuestion === 0} className="px-6 py-3 rounded-lg bg-slate-700 hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold transition-colors">← 前の問題</button>
            {!isSubmitted ? (
              <button onClick={handleSubmitAnswer} disabled={userAnswers.length === 0} className="px-8 py-3 rounded-lg gradient-button hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold transition-all">回答する</button>
            ) : quizState.currentQuestion === questions.length - 1 ? (
              <button onClick={handleQuizCompletion} className="px-8 py-3 rounded-lg gradient-button hover:opacity-90 text-white font-semibold transition-all">完了</button>
            ) : (
              <button onClick={handleNextQuestion} className="px-6 py-3 rounded-lg gradient-button hover:opacity-90 text-white font-semibold transition-all">次の問題 →</button>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (screen === 'completion') {
    const stats = calculateStats();
    const percentage = Math.round((stats.correct / questions.length) * 100);
    const exam = EXAMS.find((e) => e.code === selectedExam);
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-950 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold gradient-text mb-4">クイズ完了！</h1>
            <div className="bg-slate-800 border border-slate-700 rounded-lg p-8 mb-8">
              <div className="text-6xl font-bold text-blue-400 mb-4">{percentage}%</div>
              <div className="text-2xl font-semibold text-white mb-6">{stats.correct} / {questions.length} 問正解</div>
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="bg-slate-700 rounded-lg p-4"><div className="text-green-400 text-lg font-semibold">{stats.correct}</div><div className="text-gray-400 text-sm">正解</div></div>
                <div className="bg-slate-700 rounded-lg p-4"><div className="text-red-400 text-lg font-semibold">{stats.incorrect}</div><div className="text-gray-400 text-sm">不正解</div></div>
                <div className="bg-slate-700 rounded-lg p-4"><div className="text-yellow-400 text-lg font-semibold">{formatTime(elapsedTime)}</div><div className="text-gray-400 text-sm">経過時間</div></div>
              </div>
              <div className="w-full h-3 bg-slate-900 rounded-full overflow-hidden"><div className="h-full gradient-bar" style={{ width: percentage + '%' }} /></div>
            </div>
          </div>
          {stats.incorrectQuestions.length > 0 && (
            <div className="bg-slate-800 border border-slate-700 rounded-lg p-8 mb-8">
              <h2 className="text-2xl font-bold text-white mb-6">不正解の問題</h2>
              <div className="space-y-6">
                {stats.incorrectQuestions.map((q) => (
                  <div key={q.id} className="border-l-4 border-red-500 pl-6 pb-6 last:pb-0">
                    <div className="font-semibold text-white mb-3">問題 {q.index + 1}: {q.question}</div>
                    <div className="mb-4 p-4 bg-slate-700 rounded-lg">
                      <div className="text-sm text-gray-400 mb-2">あなたの回答:</div>
                      <div className="flex gap-2 flex-wrap">
                        {(quizState.answers[q.index] || []).map((ans) => (<span key={ans} className="px-3 py-1 bg-red-600 text-white rounded-full text-sm">{ans}</span>))}
                      </div>
                    </div>
                    <div className="mb-4 p-4 bg-slate-700 rounded-lg">
                      <div className="text-sm text-gray-400 mb-2">正解:</div>
                      <div className="flex gap-2 flex-wrap">
                        {q.answer.map((ans) => (<span key={ans} className="px-3 py-1 bg-green-600 text-white rounded-full text-sm">{ans}</span>))}
                      </div>
                    </div>
                    <div className="p-4 bg-slate-900 rounded-lg border border-slate-700">
                      <div className="text-sm text-yellow-400 font-semibold mb-2">💡 解説</div>
                      <p className="text-gray-200">{q.explanation}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          <div className="flex gap-4 justify-center flex-wrap">
            <button onClick={handleRedoQuiz} className="px-8 py-3 rounded-lg bg-slate-700 hover:bg-slate-600 text-white font-semibold transition-colors">やり直す</button>
            <button onClick={handleShuffleAndReset} className="px-8 py-3 rounded-lg bg-slate-700 hover:bg-slate-600 text-white font-semibold transition-colors">シャッフル＆リセット</button>
            {getNextChapter() && (
              <button onClick={handleNextChapter} className="px-8 py-3 rounded-lg gradient-button hover:opacity-90 text-white font-semibold transition-all">次のチャプターへ →</button>
            )}
          </div>
        </div>
      </div>
    );
  }

  return null;
}
