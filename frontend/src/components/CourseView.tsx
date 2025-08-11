import React, { useState, useEffect } from 'react'
import ConceptSelector from './ConceptSelector'
import AbsorbStage from './AbsorbStage'
import TeachBackStage from './TeachBackStage'

interface Course {
  id: string;
  label: string;
  description: string;
  conversation_ids: string[];
  concepts: CourseConcept[];
  source_cluster_id: string;
  current_stage: 'explore' | 'absorb' | 'teach_back';
  progress: number;
  created_at: string;
  updated_at: string;
}

interface CourseConcept {
  title: string;
  difficulty_level: 'beginner' | 'medium' | 'advanced';
  status: 'not_started' | 'reviewing' | 'reviewed' | 'not_interested' | 'already_know';
  type: 'original' | 'related';
}

interface CourseViewProps {
  courseId: string;
  onBack: () => void;
}

function CourseView({ courseId, onBack }: CourseViewProps) {
  const [course, setCourse] = useState<Course | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedConcepts, setSelectedConcepts] = useState<Set<string>>(new Set());
  const [startingReview, setStartingReview] = useState(false);
  const [currentStage, setCurrentStage] = useState<'explore' | 'absorb' | 'teach_back'>('explore');

  useEffect(() => {
    fetchCourse();
  }, [courseId]);

  useEffect(() => {
    if (course) {
      setCurrentStage(course.current_stage);
      // Auto-select concepts that are already in "reviewing" status
      const reviewingConcepts = course.concepts
        .filter(concept => concept.status === 'reviewing')
        .map(concept => concept.title);
      setSelectedConcepts(new Set(reviewingConcepts));
    }
  }, [course]);

  const getStageDisplayName = (stage: string) => {
    switch (stage) {
      case 'explore': return 'Explore';
      case 'absorb': return 'Absorb';
      case 'teach_back': return 'Teach back';
      default: return stage;
    }
  };

  const getStageIndex = (stage: string) => {
    switch (stage) {
      case 'explore': return 0;
      case 'absorb': return 1;
      case 'teach_back': return 2;
      default: return 0;
    }
  };

  const fetchCourse = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:5000/api/courses/${courseId}`);
      
      if (response.ok) {
        const data = await response.json();
        setCourse(data.course);
        setError(null);
      } else {
        setError('Failed to load course details');
      }
    } catch (err) {
      setError('Failed to load course. Make sure the backend server is running.');
      console.error('Error fetching course:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleConceptSelection = (conceptTitle: string) => {
    setSelectedConcepts(prev => {
      const newSet = new Set(prev);
      if (newSet.has(conceptTitle)) {
        newSet.delete(conceptTitle);
      } else {
        newSet.add(conceptTitle);
      }
      return newSet;
    });
  };

  const handleStartReview = async () => {
    if (!course || selectedConcepts.size === 0) return;

    try {
      setStartingReview(true);
      const response = await fetch(`http://localhost:5000/api/courses/${courseId}/start-review`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          selected_concept_titles: Array.from(selectedConcepts)
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setCourse(data.course);
        setSelectedConcepts(new Set());
        setError(null);
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to start review');
      }
    } catch (err) {
      setError('Failed to start review. Please try again.');
      console.error('Error starting review:', err);
    } finally {
      setStartingReview(false);
    }
  };

  const isInExploreStage = currentStage === 'explore';
  const hasSelectableConcepts = course?.concepts.some(c => c.status === 'not_started' || c.status === 'reviewing') || false;
  const canSelectConcepts = isInExploreStage && hasSelectableConcepts;

  if (loading) {
    return (
      <div className="flex-1 flex flex-col" style={{ backgroundColor: "#FAF9F5"}}>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="text-gray-600 mt-2">Loading course...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !course) {
    return (
      <div className="flex-1 flex flex-col" style={{ backgroundColor: "#FAF9F5"}}>
        <div className="border-b border-gray-50 p-4 bg-white">
          <button 
            onClick={onBack}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
          >
            <span>←</span>
            <span>Back to Claude Mastery</span>
          </button>
        </div>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">⚠️</span>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Course</h3>
            <p className="text-gray-600 mb-4">{error}</p>
            <button
              onClick={fetchCourse}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col" style={{ backgroundColor: "#FAF9F5"}}>
      {/* Header */}
      <div className="border-b border-gray-50 p-4 bg-white">
        <div className="flex items-center justify-between">
          <button 
            onClick={onBack}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
          >
            <span>←</span>
            <span>Back to Study Guides</span>
          </button>
          <div className="text-sm text-gray-500">
            Course Progress: {course.progress}%
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto">
        {currentStage === 'absorb' ? (
          // Full width layout for AbsorbStage with header
          <div className="flex flex-col h-full">
            {/* Course Header Section */}
            <div className="p-6 pb-0">
              <div className="max-w-4xl mx-auto">
                <div className="bg-white rounded-lg border border-gray-200 p-8 mb-6">
                  <div className="flex items-start gap-4 mb-6">
                    <div className="w-16 h-16 bg-blue-100 rounded-lg flex items-center justify-center">
                      <span className="text-3xl">📚</span>
                    </div>
                    <div className="flex-1">
                      <h1 className="text-2xl font-bold text-gray-900 mb-2">
                        {course.label}
                      </h1>
                      <p className="text-gray-600 text-base leading-relaxed">
                        {course.description}
                      </p>
                    </div>
                  </div>

                  {/* Learning Stages */}
                  <div className="pt-6 border-t border-gray-100">
                    <h3 className="text-lg font-medium text-gray-800 mb-4">Learning Journey</h3>
                    
                    <div className="flex items-center w-full">
                      {['explore', 'absorb', 'teach_back'].map((stage, index) => {
                        const isActive = getStageIndex(course.current_stage) >= index;
                        const isCurrentStage = currentStage === stage;
                        
                        return (
                          <div key={stage} className="flex items-center flex-1">
                            <div className="flex flex-col items-center w-full">
                              <button
                                onClick={() => setCurrentStage(stage as 'explore' | 'absorb' | 'teach_back')}
                                className={`w-8 h-8 rounded-full flex items-center justify-center border transition-all duration-300 hover:scale-105 ${
                                  isCurrentStage
                                    ? 'bg-blue-500 border-blue-500 text-white shadow-md'
                                    : isActive 
                                      ? 'bg-orange-100 border-orange-300 text-orange-700 hover:bg-orange-200' 
                                      : 'bg-gray-100 border-gray-300 text-gray-500 hover:bg-gray-200'
                                }`}
                              >
                                <span className="text-xs font-medium">
                                  {index + 1}
                                </span>
                              </button>
                              <button
                                onClick={() => setCurrentStage(stage as 'explore' | 'absorb' | 'teach_back')}
                                className={`mt-2 text-xs font-medium transition-colors duration-200 ${
                                  isCurrentStage
                                    ? 'text-blue-600'
                                    : isActive 
                                      ? 'text-orange-700 hover:text-orange-800'
                                      : 'text-gray-500 hover:text-gray-600'
                                }`}
                              >
                                {getStageDisplayName(stage)}
                              </button>
                            </div>
                            
                            {index < 2 && (
                              <div className={`flex-1 h-px mx-3 transition-all duration-300 ${
                                getStageIndex(course.current_stage) > index 
                                  ? 'bg-orange-300' 
                                  : 'bg-gray-300'
                              }`}></div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            {/* AbsorbStage Content */}
            <div className="flex-1">
              <AbsorbStage 
                concepts={course.concepts} 
                courseId={course.id}
                courseTitle={course.label}
              />
            </div>
          </div>
        ) : (
          // Constrained width layout for other stages
          <div className="p-6">
            <div className="max-w-4xl mx-auto">
              {/* Course Header Section */}
              <div className="bg-white rounded-lg border border-gray-200 p-8 mb-6">
                <div className="flex items-start gap-4 mb-6">
                  <div className="w-16 h-16 bg-blue-100 rounded-lg flex items-center justify-center">
                    <span className="text-3xl">📚</span>
                  </div>
                  <div className="flex-1">
                    <h1 className="text-2xl font-bold text-gray-900 mb-2">
                      {course.label}
                    </h1>
                    <p className="text-gray-600 text-base leading-relaxed">
                      {course.description}
                    </p>
                  </div>
                </div>

                {/* Learning Stages */}
                <div className="pt-6 border-t border-gray-100">
                  <h3 className="text-lg font-medium text-gray-800 mb-4">Learning Journey</h3>
                  
                  <div className="flex items-center w-full">
                    {['explore', 'absorb', 'teach_back'].map((stage, index) => {
                      const isActive = getStageIndex(course.current_stage) >= index;
                      const isCurrentStage = currentStage === stage;
                      
                      return (
                        <div key={stage} className="flex items-center flex-1">
                          <div className="flex flex-col items-center w-full">
                            <button
                              onClick={() => setCurrentStage(stage as 'explore' | 'absorb' | 'teach_back')}
                              className={`w-8 h-8 rounded-full flex items-center justify-center border transition-all duration-300 hover:scale-105 ${
                                isCurrentStage
                                  ? 'bg-blue-500 border-blue-500 text-white shadow-md'
                                  : isActive 
                                    ? 'bg-orange-100 border-orange-300 text-orange-700 hover:bg-orange-200' 
                                    : 'bg-gray-100 border-gray-300 text-gray-500 hover:bg-gray-200'
                              }`}
                            >
                              <span className="text-xs font-medium">
                                {index + 1}
                              </span>
                            </button>
                            <button
                              onClick={() => setCurrentStage(stage as 'explore' | 'absorb' | 'teach_back')}
                              className={`mt-2 text-xs font-medium transition-colors duration-200 ${
                                isCurrentStage
                                  ? 'text-blue-600'
                                  : isActive 
                                    ? 'text-orange-700 hover:text-orange-800'
                                    : 'text-gray-500 hover:text-gray-600'
                              }`}
                            >
                              {getStageDisplayName(stage)}
                            </button>
                          </div>
                          
                          {index < 2 && (
                            <div className={`flex-1 h-px mx-3 transition-all duration-300 ${
                              getStageIndex(course.current_stage) > index 
                                ? 'bg-orange-300' 
                                : 'bg-gray-300'
                            }`}></div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>

              {/* Stage Content */}
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-6">
                  {currentStage === 'explore' ? 'Choose topics to master' : getStageDisplayName(currentStage)}
                </h2>
                
                {currentStage === 'explore' && (
                  <ConceptSelector
                    concepts={course.concepts}
                    selectedConcepts={selectedConcepts}
                    onToggleConceptSelection={toggleConceptSelection}
                    onStartReview={handleStartReview}
                    canSelectConcepts={canSelectConcepts}
                    startingReview={startingReview}
                  />
                )}

                {currentStage === 'teach_back' && (
                  <TeachBackStage concepts={course.concepts} />
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default CourseView;
