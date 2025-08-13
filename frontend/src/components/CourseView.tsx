import React, { useState, useEffect } from 'react'
import ConceptSelector from './ConceptSelector'
import AbsorbStage from './AbsorbStage'
import TeachBackStage from './TeachBackStage'
import { buildApiUrl } from '../config/api'
import type { CourseConcept } from '../types/course'

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
  const [loadingRelatedTopics, setLoadingRelatedTopics] = useState(false);
  const [relatedTopicsError, setRelatedTopicsError] = useState<string | null>(null);
  const [loadingOriginalTopics, setLoadingOriginalTopics] = useState(false);
  const [originalTopicsError, setOriginalTopicsError] = useState<string | null>(null);
  const [creatingCourse, setCreatingCourse] = useState(false);

  useEffect(() => {
    fetchCourseOrCreateFromCluster();
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

  // Fetch related topics asynchronously after course loads
  useEffect(() => {
    if (course && !loadingRelatedTopics) {
      fetchRelatedTopics();
    }
  }, [course?.id]); // Only trigger when course ID changes

  const fetchCourseOrCreateFromCluster = async () => {
    // Prevent multiple concurrent requests
    if (creatingCourse) {
      console.log('Course creation already in progress, skipping duplicate request');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      // First, try to fetch as a course
      const courseResponse = await fetch(buildApiUrl(`/api/courses/${courseId}`));
      
      if (courseResponse.ok) {
        // It's an existing course
        const data = await courseResponse.json();
        setCourse(data.course);
        return;
      }
      
      // If course fetch failed, it might be a cluster ID
      // Try to create a course from the cluster
      setCreatingCourse(true);
      setLoadingOriginalTopics(true);
      setOriginalTopicsError(null);
      
      const createResponse = await fetch(buildApiUrl(`/api/study-guides/${courseId}/start`), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'cluster' })
      });

      if (createResponse.ok) {
        const createData = await createResponse.json();
        setCourse(createData.course);
        setLoadingOriginalTopics(false);
      } else {
        const errorData = await createResponse.json();
        setOriginalTopicsError(errorData.error || 'Failed to create course from cluster');
        setLoadingOriginalTopics(false);
        setError('Failed to load course or create from cluster');
      }
    } catch (err) {
      setError('Failed to load course. Make sure the backend server is running.');
      setLoadingOriginalTopics(false);
      console.error('Error fetching course or creating from cluster:', err);
    } finally {
      setLoading(false);
      setCreatingCourse(false);
    }
  };

  const fetchRelatedTopics = async () => {
    if (!course) return;

    try {
      setLoadingRelatedTopics(true);
      setRelatedTopicsError(null);
      
      const response = await fetch(buildApiUrl(`/api/courses/${course.id}/related-topics`), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (response.ok) {
        const data = await response.json();
        setCourse(data.course);
        setRelatedTopicsError(null);
      } else {
        const errorData = await response.json();
        setRelatedTopicsError(errorData.error || 'Failed to load related topics');
      }
    } catch (err) {
      setRelatedTopicsError('Failed to load related topics');
      console.error('Error fetching related topics:', err);
    } finally {
      setLoadingRelatedTopics(false);
    }
  };

  const getStageDisplayName = (stage: string) => {
    switch (stage) {
      case 'explore': return 'Explore';
      case 'absorb': return 'Absorb';
      case 'teach_back': return 'Teach back';
      default: return stage;
    }
  };

  const handleStageChange = async (newStage: 'explore' | 'absorb' | 'teach_back') => {
    if (!course) return;

    try {
      // Update local state immediately for responsive UI
      setCurrentStage(newStage);

      // Update course stage in backend
      const response = await fetch(buildApiUrl(`/api/courses/${course.id}/stage`), {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          stage: newStage
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setCourse(data.course);
        setError(null);
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to update course stage');
        // Revert local state on error
        setCurrentStage(course.current_stage);
      }
    } catch (err) {
      setError('Failed to update course stage. Please try again.');
      // Revert local state on error
      setCurrentStage(course.current_stage);
      console.error('Error updating course stage:', err);
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
    if (!course) return;

    try {
      setStartingReview(true);
      
      // First, update the concept selection (allows deselection)
      const updateResponse = await fetch(buildApiUrl(`/api/courses/${courseId}/update-selection`), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          selected_concept_titles: Array.from(selectedConcepts)
        }),
      });

      if (updateResponse.ok) {
        const updateData = await updateResponse.json();
        setCourse(updateData.course);
        
        // If there are selected concepts, start the review process
        if (selectedConcepts.size > 0) {
          const reviewResponse = await fetch(buildApiUrl(`/api/courses/${courseId}/start-review`), {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              selected_concept_titles: Array.from(selectedConcepts)
            }),
          });

          if (reviewResponse.ok) {
            const reviewData = await reviewResponse.json();
            setCourse(reviewData.course);
          } else {
            const errorData = await reviewResponse.json();
            setError(errorData.error || 'Failed to start review');
            return;
          }
        }
        
        setSelectedConcepts(new Set());
        setError(null);
      } else {
        const errorData = await updateResponse.json();
        setError(errorData.error || 'Failed to update selection');
      }
    } catch (err) {
      setError('Failed to start review. Please try again.');
      console.error('Error starting review:', err);
    } finally {
      setStartingReview(false);
    }
  };

  const isInExploreStage = currentStage === 'explore';
  const hasSelectableConcepts = (course?.concepts?.length ?? 0) > 0;
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
              onClick={fetchCourseOrCreateFromCluster}
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
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto">
        {/* Universal Course Header Section */}
        <div className="p-6 pb-0">
          <div className="max-w-4xl mx-auto">
            <div className="p-8 mb-3">
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
              <div className="pt-6">
                <div className="flex items-center w-full">
                  {['explore', 'absorb', 'teach_back'].map((stage, index) => {
                    const isCurrentStage = currentStage === stage;
                    
                    return (
                      <React.Fragment key={stage}>
                        <div className="flex items-center flex-1">
                          <div className="flex flex-col items-center w-full">
                            <button
                              onClick={() => handleStageChange(stage as 'explore' | 'absorb' | 'teach_back')}
                              className={`w-8 h-8 rounded-full flex items-center justify-center border transition-all duration-300 hover:scale-105 ${
                                isCurrentStage
                                  ? 'bg-orange-500 border-orange-500 text-white shadow-md'
                                  : 'bg-gray-100 border-gray-300 text-gray-500 hover:bg-gray-200'
                              }`}
                            >
                              <span className="text-xs font-medium">
                                {index + 1}
                              </span>
                            </button>
                            <button
                              onClick={() => handleStageChange(stage as 'explore' | 'absorb' | 'teach_back')}
                              className={`mt-2 text-xs font-medium transition-colors duration-200 ${
                                isCurrentStage
                                  ? 'text-orange-600'
                                  : 'text-gray-500 hover:text-gray-600'
                              }`}
                            >
                              {getStageDisplayName(stage)}
                            </button>
                          </div>
                        </div>
                        {index < 2 && (
                          <div className="w-16 flex flex-col items-center justify-center relative">
                            {/* Horizontal border */}
                            <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-gray-300 transition-all duration-300" style={{ zIndex: 0 }}></div>
                          </div>
                        )}
                      </React.Fragment>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Stage Content */}
        {currentStage === 'absorb' ? (
          // Full width layout for AbsorbStage
          <div className="flex-1">
            <AbsorbStage 
              concepts={course.concepts} 
              courseId={course.id}
              courseTitle={course.label}
            />
          </div>
        ) : currentStage === 'teach_back' ? (
          // Full width layout for TeachBackStage
          <div className="flex-1">
            <TeachBackStage 
              concepts={course.concepts}
              courseId={course.id}
              courseTitle={course.label}
            />
          </div>
        ) : (
          // Constrained width layout for Explore stage
          <div className="p-6">
            <div className="max-w-4xl mx-auto">
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-6">
                  Choose topics to master
                </h2>
                
                <ConceptSelector
                  concepts={course.concepts}
                  selectedConcepts={selectedConcepts}
                  onToggleConceptSelection={toggleConceptSelection}
                  onStartReview={handleStartReview}
                  canSelectConcepts={canSelectConcepts}
                  startingReview={startingReview}
                  loadingRelatedTopics={loadingRelatedTopics}
                  relatedTopicsError={relatedTopicsError}
                  loadingOriginalTopics={loadingOriginalTopics}
                  originalTopicsError={originalTopicsError}
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default CourseView;
