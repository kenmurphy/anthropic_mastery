import type { CourseConcept } from '../types/course';

interface ConceptCardProps {
  concept: CourseConcept;
  isRelated?: boolean;
  isSelectable?: boolean;
  isSelected?: boolean;
  onToggleSelect?: () => void;
}

function ConceptCard({ concept, isRelated = false, isSelectable = false, isSelected = false, onToggleSelect }: ConceptCardProps) {
  const getDifficultyColor = (level: string) => {
    switch (level) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'reviewing': return 'bg-yellow-100 text-yellow-800';
      case 'not_started': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'reviewing': return 'Reviewing';
      case 'not_started': return 'Not Started';
      default: return status;
    }
  };

  // Show status for both valid statuses
  const shouldShowStatus = true;

  return (
    <div 
      className={`border rounded-lg p-4 transition-all duration-200 ${
        isSelectable 
          ? 'cursor-pointer hover:shadow-md hover:border-blue-300' 
          : 'hover:shadow-md'
      } ${
        isSelected 
          ? 'border-blue-500 bg-blue-50 shadow-md' 
          : isRelated 
            ? 'border-purple-200 bg-purple-50/30' 
            : 'border-gray-200 bg-white'
      }`}
      onClick={isSelectable ? onToggleSelect : undefined}
    >
      <div className="flex items-start justify-between mb-3">
        <h4 className="font-medium text-gray-900 text-sm leading-tight">
          {concept.title}
        </h4>
        <div className="flex items-center gap-2 ml-2 flex-shrink-0">
          {isRelated && (
            <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">
              AI
            </span>
          )}
          {isSelectable && (
            <div className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
              isSelected 
                ? 'bg-blue-500 border-blue-500' 
                : 'border-gray-300 bg-white'
            }`}>
              {isSelected && (
                <span className="text-white text-xs">✓</span>
              )}
            </div>
          )}
        </div>
      </div>
      
      <div className="flex items-center gap-2 mt-3">
        <span className={`text-xs px-2 py-1 rounded-full font-medium ${getDifficultyColor(concept.difficulty_level)}`}>
          {concept.difficulty_level.charAt(0).toUpperCase() + concept.difficulty_level.slice(1)}
        </span>
        {shouldShowStatus && (
          <span className={`text-xs px-2 py-1 rounded-full font-medium ${getStatusColor(concept.status)}`}>
            {getStatusText(concept.status)}
          </span>
        )}
      </div>
    </div>
  );
}

interface ConceptSelectorProps {
  concepts: CourseConcept[];
  selectedConcepts: Set<string>;
  onToggleConceptSelection: (conceptTitle: string) => void;
  onStartReview: () => void;
  canSelectConcepts: boolean;
  startingReview: boolean;
  loadingRelatedTopics?: boolean;
  relatedTopicsError?: string | null;
  loadingOriginalTopics?: boolean;
  originalTopicsError?: string | null;
}

function ConceptSelector({ 
  concepts, 
  selectedConcepts, 
  onToggleConceptSelection, 
  onStartReview, 
  canSelectConcepts, 
  startingReview,
  loadingRelatedTopics = false,
  relatedTopicsError = null,
  loadingOriginalTopics = false,
  originalTopicsError = null
}: ConceptSelectorProps) {
  if (concepts.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
          <span className="text-xl">📝</span>
        </div>
        <p>No concepts available for this course</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Original Concepts */}
      <div>
        <h3 className="text-lg font-medium text-gray-800 mb-4 flex items-center gap-2">
          <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
          Topics from Your Recent Activity
          {loadingOriginalTopics && (
            <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin ml-2"></div>
          )}
        </h3>
        
        {loadingOriginalTopics && concepts.filter(concept => concept.type === 'original').length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
            <p className="text-sm">Refining topics from your conversations...</p>
          </div>
        )}
        
        {originalTopicsError && (
          <div className="text-center py-6 text-red-600 bg-red-50 rounded-lg border border-red-200">
            <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-2">
              <span className="text-red-600">⚠️</span>
            </div>
            <p className="text-sm font-medium">Failed to load original topics</p>
            <p className="text-xs text-red-500 mt-1">{originalTopicsError}</p>
          </div>
        )}
        
        {concepts.filter(concept => concept.type === 'original').length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {concepts
              .filter(concept => concept.type === 'original')
              .map((concept, index) => (
                <ConceptCard 
                  key={`original-${index}`} 
                  concept={concept}
                  isSelectable={canSelectConcepts}
                  isSelected={selectedConcepts.has(concept.title)}
                  onToggleSelect={() => onToggleConceptSelection(concept.title)}
                />
              ))}
          </div>
        )}
        
        {!loadingOriginalTopics && !originalTopicsError && concepts.filter(concept => concept.type === 'original').length === 0 && (
          <div className="text-center py-6 text-gray-400 bg-gray-50 rounded-lg border border-gray-200">
            <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-2">
              <span className="text-gray-400">📝</span>
            </div>
            <p className="text-sm">No original topics available</p>
          </div>
        )}
      </div>

      {/* Related Concepts - Only show after they've been fetched or are loading */}
      {(loadingRelatedTopics || relatedTopicsError || concepts.some(concept => concept.type === 'related')) && (
        <div>
          <h3 className="text-lg font-medium text-gray-800 mb-4 flex items-center gap-2">
            <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
            Related Concepts
            <span className="text-sm font-normal text-gray-500 ml-2">
              (AI Suggested)
            </span>
          </h3>
          
          {loadingRelatedTopics && (
            <div className="text-center py-8 text-gray-500">
              <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
              <p className="text-sm">Generating related topics...</p>
            </div>
          )}
          
          {relatedTopicsError && (
            <div className="text-center py-6 text-red-600 bg-red-50 rounded-lg border border-red-200">
              <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-2">
                <span className="text-red-600">⚠️</span>
              </div>
              <p className="text-sm font-medium">Failed to load related topics</p>
              <p className="text-xs text-red-500 mt-1">{relatedTopicsError}</p>
            </div>
          )}
          
          {!loadingRelatedTopics && concepts.filter(concept => concept.type === 'related').length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {concepts
                .filter(concept => concept.type === 'related')
                .map((concept, index) => (
                  <ConceptCard
                    key={`related-${index}`} 
                    concept={concept}
                    isRelated={true}
                    isSelectable={canSelectConcepts}
                    isSelected={selectedConcepts.has(concept.title)}
                    onToggleSelect={() => onToggleConceptSelection(concept.title)}
                  />
                ))}
            </div>
          )}
          
          {!loadingRelatedTopics && !relatedTopicsError && concepts.filter(concept => concept.type === 'related').length === 0 && (
            <div className="text-center py-6 text-gray-400 bg-gray-50 rounded-lg border border-gray-200">
              <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-2">
                <span className="text-gray-400">🔍</span>
              </div>
              <p className="text-sm">No related topics available</p>
            </div>
          )}
        </div>
      )}

      {/* Update Selection Button */}
      {canSelectConcepts && (
        <div className="mt-6 pt-6 border-t border-gray-100">
          <div className="flex items-center justify-end">
            <button
              onClick={onStartReview}
              disabled={startingReview}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {startingReview ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Updating...
                </>
              ) : selectedConcepts.size > 0 ? (
                'Start Review'
              ) : (
                'Update Selection'
              )}
            </button>
          </div>
        </div>
      )}

      {/* Selection Instructions */}
      {canSelectConcepts && (
        <div className="mt-6 pt-6 border-t border-gray-100">
          <div className="text-center text-gray-500">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2">
              <span className="text-blue-600">👆</span>
            </div>
            <p className="text-sm">
              {selectedConcepts.size > 0 ? (
                'Click concepts to select/deselect them, then click "Start Review" to begin learning.'
              ) : (
                'Click on concepts above to select them for review. You can also deselect previously selected concepts.'
              )}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default ConceptSelector;
