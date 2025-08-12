import TeachBackContent from './TeachBackContent';
import TeachBackAssistant from './TeachBackAssistant';
import type { CourseConcept } from '../types/course';

interface TeachBackStageProps {
  concepts: CourseConcept[];
  courseId?: string;
  courseTitle?: string;
}

function TeachBackStage({ concepts, courseId, courseTitle }: TeachBackStageProps) {
  // Filter concepts to only show those ready for teaching back (status: 'reviewing')
  const reviewingConcepts = concepts.filter(concept => concept.status === 'reviewing');

  if (reviewingConcepts.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">🎓</span>
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No Concepts Ready for Teaching Back</h3>
          <p className="text-gray-600 max-w-md mx-auto">
            Start reviewing some concepts in the Absorb stage first to unlock the TeachBack experience.
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
          concepts={reviewingConcepts}
          courseId={courseId || ''}
        />
      </div>

      {/* Column 2: TeachBack Assistant - Sticky */}
      <div className="w-90 bg-white rounded-lg border border-gray-200 shadow-sm sticky top-2 self-start">
        <TeachBackAssistant
          courseTitle={courseTitle}
        />
      </div>
    </div>
  );
}

export default TeachBackStage;
