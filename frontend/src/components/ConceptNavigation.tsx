import type { CourseConcept } from '../types/course';

interface ConceptNavigationProps {
  concepts: CourseConcept[];
  activeConcept: string | null;
  onConceptClick: (conceptTitle: string) => void;
}

function ConceptNavigation({ concepts, activeConcept, onConceptClick }: ConceptNavigationProps) {
  const getDifficultyColor = (level: string) => {
    switch (level) {
      case 'beginner':
        return 'text-green-600';
      case 'medium':
        return 'text-yellow-600';
      case 'advanced':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getDifficultyDot = (level: string) => {
    switch (level) {
      case 'beginner':
        return 'bg-green-500';
      case 'medium':
        return 'bg-yellow-500';
      case 'advanced':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="h-full overflow-y-auto p-1">
      {concepts.map((concept, index) => (
        <button
          key={index}
          onClick={() => onConceptClick(concept.title)}
          className={`w-full text-left p-1 rounded-lg mb-1 transition-colors ${
            activeConcept === concept.title
              ? 'bg-blue-50 border border-blue-200'
              : 'hover:bg-gray-50'
          }`}
        >
          <div className="flex items-start gap-2">
            <div className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${getDifficultyDot(concept.difficulty_level)}`} />
            <div className="flex-1 min-w-0">
              <p className={`text-sm font-medium truncate ${
                activeConcept === concept.title ? 'text-black' : 'text-gray-500'
              }`}>
                {concept.title}
              </p>
              <div className="flex items-center gap-2 mt-1">
                <span className={`text-xs capitalize ${
                  activeConcept === concept.title 
                    ? getDifficultyColor(concept.difficulty_level)
                    : 'text-gray-400'
                }`}>
                  {concept.difficulty_level}
                </span>
                {concept.type === 'related' && (
                  <span className={`text-xs px-1.5 py-0.5 rounded ${
                    activeConcept === concept.title
                      ? 'text-gray-600 bg-gray-100'
                      : 'text-gray-400 bg-gray-100'
                  }`}>
                    Related
                  </span>
                )}
              </div>
            </div>
          </div>
        </button>
      ))}
    </div>
  );
}

export default ConceptNavigation;
