import React, { useState, useEffect, useRef } from 'react';
import ConceptNavigation from './ConceptNavigation';
import StudyContent from './StudyContent';
import StudyChat from './StudyChat';

interface CourseConcept {
  title: string;
  difficulty_level: 'beginner' | 'medium' | 'advanced';
  status: 'not_started' | 'reviewing' | 'reviewed' | 'not_interested' | 'already_know';
  type: 'original' | 'related';
}

interface AbsorbStageProps {
  concepts: CourseConcept[];
  courseId?: string;
  courseTitle?: string;
}

function AbsorbStage({ concepts, courseId, courseTitle }: AbsorbStageProps) {
  const [activeConcept, setActiveConcept] = useState<string | null>(null);
  const [scrollToConcept, setScrollToConcept] = useState<string | undefined>(undefined);
  const scrollTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Filter concepts to only show those chosen for review (status: 'reviewing')
  const reviewingConcepts = concepts.filter(concept => concept.status === 'reviewing');

  // Set first reviewing concept as active by default
  useEffect(() => {
    if (reviewingConcepts.length > 0 && !activeConcept) {
      setActiveConcept(reviewingConcepts[0].title);
    }
  }, [reviewingConcepts, activeConcept]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
    };
  }, []);

  const handleConceptClick = (conceptTitle: string) => {
    // Clear any existing scroll timeout to prevent race conditions
    if (scrollTimeoutRef.current) {
      clearTimeout(scrollTimeoutRef.current);
    }
    
    setActiveConcept(conceptTitle);
    setScrollToConcept(conceptTitle);
    
    // Clear scroll trigger after scroll completes
    scrollTimeoutRef.current = setTimeout(() => {
      setScrollToConcept(undefined);
      scrollTimeoutRef.current = null;
    }, 500);
  };

  const handleActiveConceptChange = (conceptTitle: string) => {
    setActiveConcept(conceptTitle);
  };

  if (reviewingConcepts.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">📖</span>
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No Concepts Selected for Review</h3>
          <p className="text-gray-600 max-w-md mx-auto">
            Please select some concepts for review from the previous stage to begin studying.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full gap-3 p-2" style={{ backgroundColor: "#FAF9F5" }}>
      {/* Column 1: Concept Navigation - Sticky */}
      <div className="w-60 sticky top-2 self-start">
        <ConceptNavigation
          concepts={reviewingConcepts}
          activeConcept={activeConcept}
          onConceptClick={handleConceptClick}
        />
      </div>

      {/* Column 2: Study Content */}
      <div className="flex-1 overflow-hidden">
        <StudyContent
          concepts={reviewingConcepts}
          courseId={courseId || ''}
          onActiveConceptChange={handleActiveConceptChange}
          scrollToConcept={scrollToConcept}
        />
      </div>

      {/* Column 3: Study Chat - Sticky */}
      <div className="w-90 bg-white rounded-lg border border-gray-200 shadow-sm sticky top-2 self-start">
        <StudyChat
          courseTitle={courseTitle}
          activeConcept={activeConcept || undefined}
        />
      </div>
    </div>
  );
}

export default AbsorbStage;
