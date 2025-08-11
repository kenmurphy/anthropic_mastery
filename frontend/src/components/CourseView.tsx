import React, { useState, useEffect } from 'react'

interface Course {
  id: string;
  label: string;
  description: string;
  conversation_ids: string[];
  concepts: CourseConcept[];
  source_cluster_id: string;
  progress: number;
  created_at: string;
  updated_at: string;
}

interface CourseConcept {
  title: string;
  difficulty_level: 'beginner' | 'medium' | 'advanced';
  status: 'not_started' | 'reviewed' | 'not_interested' | 'already_know';
  type: 'original' | 'related';
}

interface CourseViewProps {
  courseId: string;
  onBack: () => void;
}

interface ConceptCardProps {
  concept: CourseConcept;
  isRelated?: boolean;
}

function ConceptCard({ concept, isRelated = false }: ConceptCardProps) {
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
      case 'reviewed': return 'bg-blue-100 text-blue-800';
      case 'already_know': return 'bg-purple-100 text-purple-800';
      case 'not_interested': return 'bg-gray-100 text-gray-600';
      case 'not_started': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'reviewed': return 'Reviewed';
      case 'already_know': return 'Already Know';
      case 'not_interested': return 'Not Interested';
      case 'not_started': return 'Not Started';
      default: return status;
    }
  };

  return (
    <div className={`border rounded-lg p-4 hover:shadow-md transition-shadow ${
      isRelated ? 'border-purple-200 bg-purple-50/30' : 'border-gray-200 bg-white'
    }`}>
      <div className="flex items-start justify-between mb-3">
        <h4 className="font-medium text-gray-900 text-sm leading-tight">
          {concept.title}
        </h4>
        {isRelated && (
          <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full ml-2 flex-shrink-0">
            AI
          </span>
        )}
      </div>
      
      <div className="flex items-center gap-2 mt-3">
        <span className={`text-xs px-2 py-1 rounded-full font-medium ${getDifficultyColor(concept.difficulty_level)}`}>
          {concept.difficulty_level.charAt(0).toUpperCase() + concept.difficulty_level.slice(1)}
        </span>
        <span className={`text-xs px-2 py-1 rounded-full font-medium ${getStatusColor(concept.status)}`}>
          {getStatusText(concept.status)}
        </span>
      </div>
    </div>
  );
}

function CourseView({ courseId, onBack }: CourseViewProps) {
  const [course, setCourse] = useState<Course | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchCourse();
  }, [courseId]);

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
      <div className="flex-1 overflow-y-auto p-6">
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

            {/* Course Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6 border-t border-gray-100">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {course.conversation_ids.length}
                </div>
                <div className="text-sm text-gray-600">
                  Related Conversation{course.conversation_ids.length !== 1 ? 's' : ''}
                </div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {course.concepts.length}
                </div>
                <div className="text-sm text-gray-600">
                  Learning Concept{course.concepts.length !== 1 ? 's' : ''}
                </div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {course.progress}%
                </div>
                <div className="text-sm text-gray-600">
                  Progress Complete
                </div>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="mt-6">
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>Overall Progress</span>
                <span>{course.progress}% Complete</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className="bg-blue-600 h-3 rounded-full transition-all duration-300" 
                  style={{ width: `${course.progress}%` }}
                ></div>
              </div>
            </div>
          </div>

          {/* Learning Components */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">
              Learning Components
            </h2>
            
            {course.concepts.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-xl">📝</span>
                </div>
                <p>No concepts available for this course</p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Original Concepts */}
                {course.concepts.filter(concept => concept.type === 'original').length > 0 && (
                  <div>
                    <h3 className="text-lg font-medium text-gray-800 mb-4 flex items-center gap-2">
                      <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                      Core Concepts
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {course.concepts
                        .filter(concept => concept.type === 'original')
                        .map((concept, index) => (
                          <ConceptCard key={`original-${index}`} concept={concept} />
                        ))}
                    </div>
                  </div>
                )}

                {/* Related Concepts */}
                {course.concepts.filter(concept => concept.type === 'related').length > 0 && (
                  <div>
                    <h3 className="text-lg font-medium text-gray-800 mb-4 flex items-center gap-2">
                      <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
                      Related Concepts
                      <span className="text-sm font-normal text-gray-500 ml-2">
                        (AI Suggested)
                      </span>
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {course.concepts
                        .filter(concept => concept.type === 'related')
                        .map((concept, index) => (
                          <ConceptCard key={`related-${index}`} concept={concept} isRelated={true} />
                        ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default CourseView;
