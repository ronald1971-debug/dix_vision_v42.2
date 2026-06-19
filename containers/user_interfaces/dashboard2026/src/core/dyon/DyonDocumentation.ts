/**
 * DYON Documentation and Training Materials
 * DIX VISION v42.2 - Phase 11: DYON Dashboard Integration & Advanced Features (Weeks 33-36)
 */

export interface Documentation {
  docId: string;
  title: string;
  type: 'guide' | 'reference' | 'tutorial' | 'api' | 'troubleshooting';
  category: string;
  content: string;
  sections: DocumentationSection[];
  lastUpdated: number;
  version: string;
}

export interface DocumentationSection {
  id: string;
  title: string;
  content: string;
  order: number;
}

export interface TrainingModule {
  moduleId: string;
  title: string;
  type: 'video' | 'interactive' | 'reading' | 'exercise';
  category: string;
  duration: number; // minutes
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  content: TrainingContent;
  progress?: TrainingProgress;
}

export interface TrainingContent {
  sections: TrainingSection[];
  exercises: Exercise[];
  quizzes: Quiz[];
}

export interface TrainingSection {
  id: string;
  title: string;
  content: string;
  order: number;
}

export interface Exercise {
  exerciseId: string;
  title: string;
  description: string;
  steps: string[];
  expectedOutput: string;
}

export interface Quiz {
  quizId: string;
  title: string;
  questions: QuizQuestion[];
}

export interface QuizQuestion {
  questionId: string;
  question: string;
  options: string[];
  correctAnswer: number;
  explanation: string;
}

export interface TrainingProgress {
  completedSections: string[];
  completedExercises: string[];
  completedQuizzes: string[];
  quizScores: Map<string, number>;
  lastAccessed: number;
  completionPercentage: number;
}

class DyonDocumentation {
  private documentation: Map<string, Documentation> = new Map();
  private trainingModules: Map<string, TrainingModule> = new Map();
  private userProgress: Map<string, Map<string, TrainingProgress>> = new Map();

  initialize(): void {
    this.loadDefaultDocumentation();
    this.loadDefaultTrainingModules();
  }

  private loadDefaultDocumentation(): void {
    const docs: Documentation[] = [
      {
        docId: 'doc_introduction',
        title: 'DYON Engineering Intelligence - Introduction',
        type: 'guide',
        category: 'getting-started',
        content: 'DYON is a production-grade engineering intelligence system...',
        sections: [
          {
            id: 'sec_01',
            title: 'Overview',
            content: 'DYON provides comprehensive engineering intelligence capabilities...',
            order: 1
          },
          {
            id: 'sec_02',
            title: 'Architecture',
            content: 'The DYON architecture consists of multiple intelligent domains...',
            order: 2
          }
        ],
        lastUpdated: Date.now(),
        version: '1.0.0'
      },
      {
        docId: 'doc_repository_intelligence',
        title: 'Repository Intelligence Guide',
        type: 'guide',
        category: 'intelligence',
        content: 'Repository Intelligence provides real-time tracking and health prediction...',
        sections: [],
        lastUpdated: Date.now(),
        version: '1.0.0'
      }
    ];

    docs.forEach(doc => {
      this.documentation.set(doc.docId, doc);
    });
  }

  private loadDefaultTrainingModules(): void {
    const modules: TrainingModule[] = [
      {
        moduleId: 'module_basics',
        title: 'DYON Basics',
        type: 'interactive',
        category: 'getting-started',
        duration: 45,
        difficulty: 'beginner',
        content: {
          sections: [
            {
              id: 'tr_sec_01',
              title: 'Introduction to DYON',
              content: 'Learn the fundamentals of DYON engineering intelligence...',
              order: 1
            },
            {
              id: 'tr_sec_02',
              title: 'Navigation',
              content: 'Understand the DYON workspace and tab structure...',
              order: 2
            }
          ],
          exercises: [
            {
              exerciseId: 'ex_001',
              title: 'Navigate the Workspace',
              description: 'Practice switching between workspace tabs',
              steps: ['Open the DYON workspace', 'Navigate to Monitoring tab', 'Switch to Patches tab'],
              expectedOutput: 'Successfully navigate between tabs'
            }
          ],
          quizzes: [
            {
              quizId: 'quiz_001',
              title: 'DYON Basics Quiz',
              questions: [
                {
                  questionId: 'q_001',
                  question: 'What is the primary purpose of DYON?',
                  options: ['File management', 'Engineering intelligence', 'Code editing', 'Version control'],
                  correctAnswer: 1,
                  explanation: 'DYON is designed for engineering intelligence'
                }
              ]
            }
          ]
        }
      },
      {
        moduleId: 'module_advanced',
        title: 'Advanced DYON Features',
        type: 'interactive',
        category: 'advanced',
        duration: 90,
        difficulty: 'advanced',
        content: {
          sections: [
            {
              id: 'tr_adv_01',
              title: 'Patch Generation',
              content: 'Learn to generate and validate patches...',
              order: 1
            },
            {
              id: 'tr_adv_02',
              title: 'Testing and Validation',
              content: 'Understand the testing suite and validation processes...',
              order: 2
            }
          ],
          exercises: [],
          quizzes: []
        }
      }
    ];

    modules.forEach(module => {
      this.trainingModules.set(module.moduleId, module);
    });
  }

  getDocumentation(docId: string): Documentation | undefined {
    return this.documentation.get(docId);
  }

  getAllDocumentation(): Documentation[] {
    return Array.from(this.documentation.values());
  }

  getDocumentationByCategory(category: string): Documentation[] {
    return Array.from(this.documentation.values()).filter(doc => doc.category === category);
  }

  getTrainingModule(moduleId: string): TrainingModule | undefined {
    return this.trainingModules.get(moduleId);
  }

  getAllTrainingModules(): TrainingModule[] {
    return Array.from(this.trainingModules.values());
  }

  getTrainingModuleByCategory(category: string): TrainingModule[] {
    return Array.from(this.trainingModules.values()).filter(mod => mod.category === category);
  }

  startTraining(userId: string, moduleId: string): void {
    const progress: TrainingProgress = {
      completedSections: [],
      completedExercises: [],
      completedQuizzes: [],
      quizScores: new Map(),
      lastAccessed: Date.now(),
      completionPercentage: 0
    };

    if (!this.userProgress.has(userId)) {
      this.userProgress.set(userId, new Map());
    }

    this.userProgress.get(userId)!.set(moduleId, progress);
  }

  updateProgress(userId: string, moduleId: string, progress: Partial<TrainingProgress>): void {
    const userProgress = this.userProgress.get(userId);
    if (!userProgress) return;

    const moduleProgress = userProgress.get(moduleId);
    if (!moduleProgress) return;

    Object.assign(moduleProgress, progress);
    moduleProgress.lastAccessed = Date.now();

    // Calculate completion percentage
    const module = this.trainingModules.get(moduleId);
    if (module) {
      const total = module.content.sections.length + module.content.exercises.length + module.content.quizzes.length;
      const completed = moduleProgress.completedSections.length + 
                      moduleProgress.completedExercises.length + 
                      moduleProgress.completedQuizzes.length;
      moduleProgress.completionPercentage = total > 0 ? (completed / total) * 100 : 0;
    }
  }

  getProgress(userId: string, moduleId: string): TrainingProgress | undefined {
    return this.userProgress.get(userId)?.get(moduleId);
  }

  getAllProgress(userId: string): Map<string, TrainingProgress> | undefined {
    return this.userProgress.get(userId);
  }
}

export const dyonDocumentation = new DyonDocumentation();
export default DyonDocumentation;