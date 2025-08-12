import { useState, useEffect } from 'react';
import MarkdownRenderer from './MarkdownRenderer';
import type { CourseConcept } from '../types/course';

interface ConceptSummary {
  title: string;
  summary: string;
  isLoading: boolean;
  error?: string;
  cached?: boolean;
  expanded?: boolean;
}

interface StudyContentProps {
  concepts: CourseConcept[];
  courseId: string;
  onActiveConceptChange: (conceptTitle: string) => void;
}

function StudyContent({ concepts, courseId, onActiveConceptChange }: StudyContentProps) {
  const [conceptSummaries, setConceptSummaries] = useState<Map<string, ConceptSummary>>(new Map());

  // Initialize concept summaries with cached data, preserving existing expansion states
  useEffect(() => {
    setConceptSummaries(prev => {
      const updated = new Map<string, ConceptSummary>();
      concepts.forEach(concept => {
        const existing = prev.get(concept.title);
        updated.set(concept.title, {
          title: concept.title,
          summary: concept.summary || existing?.summary || '',
          isLoading: existing?.isLoading || false,
          cached: !!concept.summary || existing?.cached || false,
          expanded: existing?.expanded || false, // Preserve existing expansion state
          error: existing?.error
        });
      });
      return updated;
    });
  }, [concepts]);


  const toggleSummaryExpansion = (conceptTitle: string) => {
    setConceptSummaries(prev => {
      const updated = new Map(prev);
      const existing = updated.get(conceptTitle);
      if (existing) {
        updated.set(conceptTitle, { ...existing, expanded: !existing.expanded });
      }
      return updated;
    });
  };

  const generateConceptSummary = async (conceptTitle: string) => {
    setConceptSummaries(prev => {
      const updated = new Map(prev);
      const existing = updated.get(conceptTitle);
      if (existing) {
        updated.set(conceptTitle, { ...existing, isLoading: true, error: undefined });
      }
      return updated;
    });

    try {
      const response = await fetch('http://localhost:5000/api/concepts/summary', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          concept_title: conceptTitle,
          course_id: courseId
        })
      });

      if (!response.ok) {
        throw new Error('Failed to generate summary');
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      let accumulatedSummary = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = new TextDecoder().decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.cached && data.content) {
                // Handle cached response - return immediately
                setConceptSummaries(prev => {
                  const updated = new Map(prev);
                  const existing = updated.get(conceptTitle);
                  if (existing) {
                    updated.set(conceptTitle, {
                      ...existing,
                      summary: data.content,
                      isLoading: false,
                      cached: true
                    });
                  }
                  return updated;
                });
                return;
              }

              if (data.content) {
                accumulatedSummary += data.content;
                setConceptSummaries(prev => {
                  const updated = new Map(prev);
                  const existing = updated.get(conceptTitle);
                  if (existing) {
                    updated.set(conceptTitle, {
                      ...existing,
                      summary: accumulatedSummary,
                      isLoading: true,
                      cached: false
                    });
                  }
                  return updated;
                });
              }

              if (data.is_complete) {
                setConceptSummaries(prev => {
                  const updated = new Map(prev);
                  const existing = updated.get(conceptTitle);
                  if (existing) {
                    updated.set(conceptTitle, {
                      ...existing,
                      summary: accumulatedSummary,
                      isLoading: false,
                      cached: false
                    });
                  }
                  return updated;
                });
                return;
              }

              if (data.error) {
                throw new Error(data.error);
              }
            } catch {
              // Ignore JSON parse errors for malformed chunks
            }
          }
        }
      }
    } catch (error) {
      setConceptSummaries(prev => {
        const updated = new Map(prev);
        const existing = updated.get(conceptTitle);
        if (existing) {
          updated.set(conceptTitle, {
            ...existing,
            isLoading: false,
            error: error instanceof Error ? error.message : 'Failed to generate summary'
          });
        }
        return updated;
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

  const handleChevronClick = async (conceptTitle: string) => {
    onActiveConceptChange(conceptTitle);

    const summary = conceptSummaries.get(conceptTitle);
    
    // If no summary exists, expand immediately and show loading state
    if (!summary?.summary && !summary?.isLoading) {
      // Immediately expand and show loading state
      setConceptSummaries(prev => {
        const updated = new Map(prev);
        const existing = updated.get(conceptTitle);
        if (existing) {
          updated.set(conceptTitle, { 
            ...existing, 
            expanded: true, 
            isLoading: true 
          });
        }
        return updated;
      });
      
      // Then generate the summary
      await generateConceptSummary(conceptTitle);
    } else {
      // Toggle expansion
      toggleSummaryExpansion(conceptTitle);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto space-y-3">
      {concepts.map((concept, index) => {
        const summary = conceptSummaries.get(concept.title);
        const hasContent = summary?.summary || summary?.isLoading;
        const isExpanded = summary?.expanded;
        
        return (
          <div
            key={index}
            className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow"
          >
            {/* Compact concept card header */}
            <div 
              className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50 transition-colors"
              onClick={() => handleChevronClick(concept.title)}
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
                {summary?.isLoading && (
                  <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
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

            {/* Expandable summary content */}
            {hasContent && isExpanded && (
              <div className="border-t border-gray-100 p-4 bg-gray-50">
                {summary?.error ? (
                  <div className="text-red-600 bg-red-50 p-3 rounded-lg border border-red-200">
                    <p className="font-medium text-sm">Error generating summary</p>
                    <p className="text-sm mt-1">{summary.error}</p>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        generateConceptSummary(concept.title);
                      }}
                      className="mt-2 text-sm text-red-700 hover:text-red-800 underline"
                    >
                      Try again
                    </button>
                  </div>
                ) : (
                  <div className="prose prose-sm max-w-none">
                    <MarkdownRenderer content={summary.summary || 'thinking...'} />
                    {summary.cached && (
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            generateConceptSummary(concept.title);
                          }}
                          className="text-xs text-gray-500 hover:text-gray-700 underline"
                        >
                          Regenerate summary
                        </button>
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

export default StudyContent;
