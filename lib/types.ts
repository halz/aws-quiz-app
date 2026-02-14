export interface Choice {
  label: string;
  text: string;
}

export interface Question {
  id: string;
  question: string;
  choices: Choice[];
  answer: string[];
  multiSelect: boolean;
  explanation: string;
}

export interface QuizHistory {
  id?: number;
  exam: string;
  chapter: string;
  title: string;
  total: number;
  correct: number;
  duration: number;
  startedAt: number;
}

export interface ExamInfo {
  code: string;
  name: string;
  icon: string;
  chapters: number;
}

export interface ChapterInfo {
  id: string;
  exam: string;
  num: number;
  name: string;
}
