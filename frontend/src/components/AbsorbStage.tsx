import React, { useState, useEffect } from 'react';
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

  // Set first concept as active by default
  useEffect(() => {
    if (concepts.length > 0 && !activeConcept) {
      setActiveConcept(concepts[0].title);
    }
  }, [concepts, activeConcept]);

  const handleConceptClick = (conceptTitle: string) => {
    setActiveConcept(conceptTitle);
    setScrollToConcept(conceptTitle);
    // Clear scroll trigger after a short delay
    setTimeout(() => setScrollToConcept(undefined), 100);
  };

  const handleActiveConceptChange = (conceptTitle: string) => {
    setActiveConcept(conceptTitle);
  };

  if (concepts.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">📖</span>
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No Concepts Selected</h3>
          <p className="text-gray-600 max-w-md mx-auto">
            Please select some concepts from the previous stage to begin studying.
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
          concepts={concepts}
          activeConcept={activeConcept}
          onConceptClick={handleConceptClick}
        />
      </div>

      {/* Column 2: Study Content */}
      <div className="flex-1 bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
        <StudyContent
          concepts={concepts}
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
