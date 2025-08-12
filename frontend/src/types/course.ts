export interface CourseConcept {
  title: string;
  difficulty_level: 'beginner' | 'medium' | 'advanced';
  status: 'not_started' | 'reviewing';
  type: 'original' | 'related';
  summary?: string;
  summary_generated_at?: string;
  teaching_questions?: string[];
  teaching_questions_generated_at?: string;
  is_streaming_summary?: boolean;
  is_streaming_questions?: boolean;
}
