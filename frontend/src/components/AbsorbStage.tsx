import { useState, useEffect } from 'react';
import StudyContent from './StudyContent';
import StudyChat from './StudyChat';
import type { CourseConcept } from '../types/course';

interface AbsorbStageProps {
  concepts: CourseConcept[];
  courseId?: string;
  courseTitle?: string;
}

function AbsorbStage({ concepts, courseId, courseTitle }: AbsorbStageProps) {
  const [activeConcept, setActiveConcept] = useState<string | null>(null);

  // Show only concepts marked for reviewing in the Absorb stage
  const availableConcepts = concepts.filter(concept => concept.status === 'reviewing');

  // Set first reviewing concept as active by default
  useEffect(() => {
    if (availableConcepts.length > 0 && !activeConcept) {
      setActiveConcept(availableConcepts[0].title);
    }
  }, [availableConcepts, activeConcept]);

  const handleActiveConceptChange = (conceptTitle: string) => {
    setActiveConcept(conceptTitle);
  };

  if (availableConcepts.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">📖</span>
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No Concepts Ready for Review</h3>
          <p className="text-gray-600 max-w-md mx-auto">
            No concepts are marked for reviewing yet. Select concepts from the course overview to start studying.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full p-6 w-[90%] mx-auto" style={{ backgroundColor: "#FAF9F5" }}>
      <div className="h-full">
        <div className="flex h-full gap-3">
          {/* Study Content */}
          <div className="flex-1 overflow-hidden">
            <StudyContent
              concepts={availableConcepts}
              courseId={courseId || ''}
              onActiveConceptChange={handleActiveConceptChange}
            />
          </div>

          {/* Study Chat - Sticky */}
          <div className="w-90 bg-white rounded-lg border border-gray-200 shadow-sm sticky top-2 self-start">
            <StudyChat
              courseTitle={courseTitle}
              activeConcept={activeConcept || undefined}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default AbsorbStage;
