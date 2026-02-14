'use client';

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
  { code: 'clf', name: 'AWS Cloud Practitioner (CLF-C02)', icon: 'âï¸', chapters: 35 },
  { code: 'aif', name: 'AWS AI Practitioner (AIF-C01)', icon: 'ð¤', chapters: 45 },
  { code: 'saa', name: 'AWS Solutions Architect Associate (SAA-C03)', icon: 'ðï¸', chapters: 105 },
  { code: 'soa', name: 'AWS SysOps Administrator (SOA-C02)', icon: 'âï¸', chapters: 100 },
];