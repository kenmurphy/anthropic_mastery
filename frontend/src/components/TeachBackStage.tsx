import TeachBackContent from './TeachBackContent';
import StudyAssistant from './StudyAssistant';
import type { CourseConcept } from '../types/course';

interface TeachBackStageProps {
  concepts: CourseConcept[];
  courseId?: string;
  courseTitle?: string;
}

function TeachBackStage({ concepts, courseId, courseTitle }: TeachBackStageProps) {
  // Show only concepts marked for reviewing in the Teach Back stage
  const availableConcepts = concepts.filter(concept => concept.status === 'reviewing');

  if (availableConcepts.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">🎓</span>
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No Concepts Ready for Teaching</h3>
          <p className="text-gray-600 max-w-md mx-auto">
            No concepts are marked for reviewing yet. Select concepts from the course overview to start practicing.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full p-6 w-[90%] mx-auto" style={{ backgroundColor: "#FAF9F5" }}>
      {/* Column 1: TeachBack Content */}
      <div className="flex-1 overflow-hidden">
        <TeachBackContent
          concepts={availableConcepts}
          courseId={courseId || ''}
        />
      </div>

      {/* Column 2: Study Assistant - Sticky */}
      <div className="w-90 bg-white rounded-lg border border-gray-200 shadow-sm sticky top-2 self-start">
        <StudyAssistant
          courseTitle={courseTitle}
        />
      </div>
    </div>
  );
}

export default TeachBackStage;
