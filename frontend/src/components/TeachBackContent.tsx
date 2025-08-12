import { useState, useEffect } from 'react';
import type { CourseConcept } from '../types/course';

interface QuestionState {
  userExplanation: string;
  feedback: string;
}

interface ConceptTeachingState {
  title: string;
  expanded: boolean;
  selectedQuestionIndex: number;
  questionStates: Map<number, QuestionState>; // Map question index to its state
  isSubmitting: boolean;
  isStreamingFeedback: boolean;
}

interface TeachBackContentProps {
  concepts: CourseConcept[];
  courseId: string;
}

function TeachBackContent({ 
  concepts, 
  courseId
}: TeachBackContentProps) {
  const [conceptStates, setConceptStates] = useState<Map<string, ConceptTeachingState>>(new Map());

  // Initialize concept states
  useEffect(() => {
    setConceptStates(prev => {
      const updated = new Map<string, ConceptTeachingState>();
      concepts.forEach(concept => {
        const existing = prev.get(concept.title);
        updated.set(concept.title, {
          title: concept.title,
          expanded: existing?.expanded || false,
          selectedQuestionIndex: existing?.selectedQuestionIndex || 0,
          questionStates: existing?.questionStates || new Map<number, QuestionState>(),
          isSubmitting: existing?.isSubmitting || false,
          isStreamingFeedback: existing?.isStreamingFeedback || false
        });
      });
      return updated;
    });
  }, [concepts]);


  const toggleConceptExpansion = (conceptTitle: string) => {
    setConceptStates(prev => {
      const updated = new Map(prev);
      const existing = updated.get(conceptTitle);
      if (existing) {
        updated.set(conceptTitle, { ...existing, expanded: !existing.expanded });
      }
      return updated;
    });
  };

  const updateConceptState = (conceptTitle: string, updates: Partial<ConceptTeachingState>) => {
    setConceptStates(prev => {
      const updated = new Map(prev);
      const existing = updated.get(conceptTitle);
      if (existing) {
        updated.set(conceptTitle, { ...existing, ...updates });
      }
      return updated;
    });
  };

  const updateQuestionState = (conceptTitle: string, questionIndex: number, updates: Partial<QuestionState>) => {
    setConceptStates(prev => {
      const updated = new Map(prev);
      const existing = updated.get(conceptTitle);
      if (existing) {
        const newQuestionStates = new Map(existing.questionStates);
        const existingQuestionState = newQuestionStates.get(questionIndex) || { userExplanation: '', feedback: '' };
        newQuestionStates.set(questionIndex, { ...existingQuestionState, ...updates });
        updated.set(conceptTitle, { ...existing, questionStates: newQuestionStates });
      }
      return updated;
    });
  };

  const getCurrentQuestionState = (conceptTitle: string): QuestionState => {
    const conceptState = conceptStates.get(conceptTitle);
    if (!conceptState) return { userExplanation: '', feedback: '' };
    
    const questionState = conceptState.questionStates.get(conceptState.selectedQuestionIndex);
    return questionState || { userExplanation: '', feedback: '' };
  };

  const handleSubmitExplanation = async (conceptTitle: string) => {
    const conceptState = conceptStates.get(conceptTitle);
    const concept = concepts.find(c => c.title === conceptTitle);
    const currentQuestionState = getCurrentQuestionState(conceptTitle);
    
    if (!conceptState || !concept || !currentQuestionState.userExplanation.trim()) {
      return;
    }

    // Clear old feedback for current question and start streaming new feedback
    updateQuestionState(conceptTitle, conceptState.selectedQuestionIndex, { feedback: '' });
    updateConceptState(conceptTitle, { 
      isSubmitting: true,
      isStreamingFeedback: true
    });

    try {
      const selectedQuestion = concept.teaching_questions?.[conceptState.selectedQuestionIndex];
      
      const response = await fetch('http://localhost:5000/api/teachback/submit-explanation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          concept_title: conceptTitle,
          teaching_question: selectedQuestion,
          user_explanation: currentQuestionState.userExplanation,
          course_id: courseId
        })
      });

      if (!response.ok) {
        throw new Error('Failed to submit explanation');
      }

      // Handle streaming response
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                
                if (data.error) {
                  console.error('Streaming error:', data.error);
                  updateQuestionState(conceptTitle, conceptState.selectedQuestionIndex, {
                    feedback: 'Error getting feedback. Please try again.'
                  });
                  updateConceptState(conceptTitle, {
                    isSubmitting: false,
                    isStreamingFeedback: false
                  });
                  break;
                } else if (data.content) {
                  // Append new content to existing feedback for current question
                  setConceptStates(prev => {
                    const updated = new Map(prev);
                    const existing = updated.get(conceptTitle);
                    if (existing) {
                      const newQuestionStates = new Map(existing.questionStates);
                      const currentQuestionState = newQuestionStates.get(existing.selectedQuestionIndex) || { userExplanation: '', feedback: '' };
                      newQuestionStates.set(existing.selectedQuestionIndex, {
                        ...currentQuestionState,
                        feedback: currentQuestionState.feedback + data.content
                      });
                      updated.set(conceptTitle, { 
                        ...existing, 
                        questionStates: newQuestionStates
                      });
                    }
                    return updated;
                  });
                } else if (data.is_complete) {
                  // Streaming complete - keep the explanation so user can edit it
                  updateConceptState(conceptTitle, {
                    isSubmitting: false,
                    isStreamingFeedback: false
                  });
                  break;
                }
              } catch (parseError) {
                console.error('Error parsing streaming data:', parseError);
              }
            }
          }
        }
      }
      
    } catch (error) {
      console.error('Error submitting explanation:', error);
      updateQuestionState(conceptTitle, conceptState?.selectedQuestionIndex || 0, {
        feedback: 'Error getting feedback. Please try again.'
      });
      updateConceptState(conceptTitle, { 
        isSubmitting: false,
        isStreamingFeedback: false
      });
    }
  };


  const getDifficultyBadgeColor = (level: string) => {
    switch (level) {
      case 'beginner':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'advanced':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="flex-1 overflow-y-auto px-3 space-y-3">
      {concepts.map((concept, index) => {
        const conceptState = conceptStates.get(concept.title);
        const hasQuestions = concept.teaching_questions && concept.teaching_questions.length > 0;
        const isExpanded = conceptState?.expanded;
        
        return (
          <div
            key={index}
            className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow"
          >
            {/* Concept card header */}
            <div 
              className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50 transition-colors"
              onClick={() => toggleConceptExpansion(concept.title)}
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-3">
                  <h3 className="text-lg font-medium text-gray-900 truncate">
                    {concept.title}
                  </h3>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full capitalize ${getDifficultyBadgeColor(concept.difficulty_level)}`}>
                      {concept.difficulty_level}
                    </span>
                    {concept.type === 'related' && (
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                        Related
                      </span>
                    )}
                  </div>
                </div>
              </div>
              
              {/* Chevron icon */}
              <div className="flex items-center gap-2 flex-shrink-0 ml-4">
                {hasQuestions && (
                  <span className="text-xs text-gray-500">
                    {concept.teaching_questions?.length} question{concept.teaching_questions?.length !== 1 ? 's' : ''}
                  </span>
                )}
                <svg
                  className={`w-5 h-5 text-gray-400 transition-transform duration-200 ${
                    isExpanded ? 'rotate-90' : ''
                  }`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>

            {/* Expandable teaching content */}
            {isExpanded && (
              <div className="border-t border-gray-100 p-4 bg-gray-50">
                {!hasQuestions ? (
                  <div className="text-center py-8">
                    <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-3">
                      <span className="text-2xl">❓</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">No teaching questions available</p>
                    <p className="text-xs text-gray-500">
                      Teaching questions are generated when you create a summary for this concept.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {/* Question selector (if multiple questions) */}
                    {concept.teaching_questions!.length > 1 && (
                      <div className="flex flex-wrap gap-2">
                        {concept.teaching_questions!.map((_: string, questionIndex: number) => (
                          <button
                            key={questionIndex}
                            onClick={() => updateConceptState(concept.title, { selectedQuestionIndex: questionIndex })}
                            className={`px-3 py-1 text-sm rounded-full transition-colors ${
                              conceptState?.selectedQuestionIndex === questionIndex
                                ? 'bg-blue-600 text-white'
                                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                            }`}
                          >
                            Question {questionIndex + 1}
                          </button>
                        ))}
                      </div>
                    )}

                    {/* Selected teaching question */}
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <h4 className="font-medium text-blue-900 mb-2">Teaching Challenge:</h4>
                      <p className="text-blue-800">
                        {concept.teaching_questions![conceptState?.selectedQuestionIndex || 0]}
                      </p>
                    </div>

                    {/* Explanation text area */}
                    <div className="space-y-2">
                      <label className="block text-sm font-medium text-gray-700">
                        Your Explanation:
                      </label>
                      <textarea
                        value={getCurrentQuestionState(concept.title).userExplanation}
                        onChange={(e) => updateQuestionState(concept.title, conceptState?.selectedQuestionIndex || 0, { userExplanation: e.target.value })}
                        placeholder="Write your explanation here... Think about how you would teach this concept to someone who has never encountered it before."
                        className="w-full min-h-[120px] max-h-[300px] px-3 py-2 text-sm border border-gray-300 rounded-lg resize-y focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        disabled={conceptState?.isSubmitting}
                      />
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <span>
                          {getCurrentQuestionState(concept.title).userExplanation?.length || 0} characters
                        </span>
                        <span>
                          Tip: Explain it simply and clearly
                        </span>
                      </div>
                    </div>

                    {/* Action buttons */}
                    <div>
                      {/* Submit button */}
                      <button
                        onClick={() => handleSubmitExplanation(concept.title)}
                        disabled={!getCurrentQuestionState(concept.title).userExplanation?.trim() || conceptState?.isSubmitting}
                        className="w-full px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                      >
                        {conceptState?.isSubmitting ? (
                          <div className="flex items-center justify-center gap-2">
                            <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />
                            <span>Getting Feedback...</span>
                          </div>
                        ) : (
                          'Submit for Feedback'
                        )}
                      </button>
                    </div>

                    {/* Feedback section */}
                    {(getCurrentQuestionState(concept.title).feedback || conceptState?.isStreamingFeedback) && (
                      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center">
                            <span className="text-sm">💬</span>
                          </div>
                          <h4 className="font-medium text-green-900">
                            AI Feedback
                            {conceptState?.isStreamingFeedback && (
                              <span className="ml-2 text-xs text-green-600">(streaming...)</span>
                            )}
                          </h4>
                        </div>
                        <div className="text-green-800 text-sm whitespace-pre-wrap">
                          {getCurrentQuestionState(concept.title).feedback || 'Getting feedback...'}
                          {conceptState?.isStreamingFeedback && (
                            <span className="inline-block w-2 h-4 bg-green-600 ml-1 animate-pulse" />
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

export default TeachBackContent;
