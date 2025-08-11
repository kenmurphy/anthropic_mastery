import React, { useState, useEffect, useRef } from 'react';
import MarkdownRenderer from './MarkdownRenderer';

interface CourseConcept {
  title: string;
  difficulty_level: 'beginner' | 'medium' | 'advanced';
  status: 'not_started' | 'reviewing' | 'reviewed' | 'not_interested' | 'already_know';
  type: 'original' | 'related';
}

interface ConceptSummary {
  title: string;
  summary: string;
  isLoading: boolean;
  error?: string;
}

interface StudyContentProps {
  concepts: CourseConcept[];
  courseId: string;
  onActiveConceptChange: (conceptTitle: string) => void;
  scrollToConcept?: string;
}

function StudyContent({ concepts, courseId, onActiveConceptChange, scrollToConcept }: StudyContentProps) {
  const [conceptSummaries, setConceptSummaries] = useState<Map<string, ConceptSummary>>(new Map());
  const conceptRefs = useRef<Map<string, HTMLDivElement>>(new Map());
  const observerRef = useRef<IntersectionObserver | null>(null);

  // Initialize concept summaries
  useEffect(() => {
    const initialSummaries = new Map<string, ConceptSummary>();
    concepts.forEach(concept => {
      initialSummaries.set(concept.title, {
        title: concept.title,
        summary: '',
        isLoading: false
      });
    });
    setConceptSummaries(initialSummaries);
  }, [concepts]);

  // Set up intersection observer for tracking active concept
  useEffect(() => {
    if (observerRef.current) {
      observerRef.current.disconnect();
    }

    observerRef.current = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting && entry.intersectionRatio > 0.1) {
            const conceptTitle = entry.target.getAttribute('data-concept-title');
            if (conceptTitle) {
              onActiveConceptChange(conceptTitle);
            }
          }
        });
      },
      {
        threshold: [0.1],
        rootMargin: '0px 0px -80% 0px'
      }
    );

    // Observe all concept elements
    conceptRefs.current.forEach((element) => {
      if (observerRef.current) {
        observerRef.current.observe(element);
      }
    });

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [concepts, onActiveConceptChange]);

  // Handle scroll to concept
  useEffect(() => {
    if (scrollToConcept) {
      const element = conceptRefs.current.get(scrollToConcept);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  }, [scrollToConcept]);

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
              
              if (data.content) {
                accumulatedSummary += data.content;
                setConceptSummaries(prev => {
                  const updated = new Map(prev);
                  const existing = updated.get(conceptTitle);
                  if (existing) {
                    updated.set(conceptTitle, {
                      ...existing,
                      summary: accumulatedSummary,
                      isLoading: true
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
                      isLoading: false
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

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {concepts.map((concept, index) => {
        const summary = conceptSummaries.get(concept.title);
        
        return (
          <div
            key={index}
            ref={(el) => {
              if (el) {
                conceptRefs.current.set(concept.title, el);
              }
            }}
            data-concept-title={concept.title}
            className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {concept.title}
                </h3>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full capitalize ${getDifficultyBadgeColor(concept.difficulty_level)}`}>
                    {concept.difficulty_level}
                  </span>
                  {concept.type === 'related' && (
                    <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                      Related Topic
                    </span>
                  )}
                </div>
              </div>
              
              {!summary?.summary && !summary?.isLoading && (
                <button
                  onClick={() => generateConceptSummary(concept.title)}
                  className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Generate Summary
                </button>
              )}
            </div>

            <div className="prose prose-sm max-w-none">
              {summary?.isLoading && (
                <div className="flex items-center gap-2 text-gray-600">
                  <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                  <span>Generating summary...</span>
                </div>
              )}
              
              {summary?.error && (
                <div className="text-red-600 bg-red-50 p-3 rounded-lg">
                  <p className="font-medium">Error generating summary</p>
                  <p className="text-sm">{summary.error}</p>
                  <button
                    onClick={() => generateConceptSummary(concept.title)}
                    className="mt-2 text-sm text-red-700 hover:text-red-800 underline"
                  >
                    Try again
                  </button>
                </div>
              )}
              
              {summary?.summary && (
                <MarkdownRenderer content={summary.summary} />
              )}
              
              {!summary?.summary && !summary?.isLoading && !summary?.error && (
                <p className="text-gray-500 italic">
                  Click "Generate Summary" to get an AI-powered explanation of this concept.
                </p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default StudyContent;
