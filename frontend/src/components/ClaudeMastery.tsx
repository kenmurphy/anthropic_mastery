import { useState, useEffect } from 'react'
import { buildApiUrl } from '../config/api'

interface StudyGuide {
  id: string;
  type: 'course' | 'cluster';
  label: string;
  description: string;
  conversation_count: number;
  key_concepts: string[];
  created_at: string;
  
  // Course-specific fields (only present when type === 'course')
  progress?: number;
  concepts_detail?: CourseConcept[];
  
  // Cluster-specific fields (only present when type === 'cluster')
  cluster_id?: string;
}

interface CourseConcept {
  title: string;
  difficulty_level: 'beginner' | 'medium' | 'advanced';
  status: 'not_started' | 'reviewed' | 'not_interested' | 'already_know';
}

interface ClusteringStatus {
  total_conversations: number;
  total_messages: number;
  processed_messages: number;
  processing_progress: number;
  total_clusters: number;
}

interface ClaudeMasteryProps {
  onViewCourse: (courseId: string) => void;
}

function ClaudeMastery({ onViewCourse }: ClaudeMasteryProps) {
  const [studyGuides, setStudyGuides] = useState<StudyGuide[]>([]);
  const [status, setStatus] = useState<ClusteringStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStudyData();
  }, []);

  const fetchStudyData = async () => {
    try {
      setLoading(true);
      
      // Fetch study guides and status in parallel
      const [studyGuidesResponse, statusResponse] = await Promise.all([
        fetch(buildApiUrl('/api/study-guides')),
        fetch(buildApiUrl('/api/clustering/status'))
      ]);

      if (studyGuidesResponse.ok) {
        const studyGuidesData = await studyGuidesResponse.json();
        setStudyGuides(studyGuidesData.study_guides || []);
      }

      if (statusResponse.ok) {
        const statusData = await statusResponse.json();
        setStatus(statusData.status);
      }

      setError(null);
    } catch (err) {
      setError('Failed to load study data. Make sure the backend server is running.');
      console.error('Error fetching study data:', err);
    } finally {
      setLoading(false);
    }
  };

  const triggerClustering = async () => {
    try {
      setLoading(true);
      const response = await fetch(buildApiUrl('/api/clustering/run'), {
        method: 'POST'
      });

      if (response.ok) {
        // Refresh data after clustering
        await fetchStudyData();
      } else {
        setError('Failed to run clustering. Check if you have enough conversations.');
      }
    } catch (err) {
      setError('Failed to trigger clustering.');
      console.error('Error triggering clustering:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStartStudy = async (studyGuide: StudyGuide) => {
    try {
      if (studyGuide.type === 'course') {
        // Already a course, navigate directly
        onViewCourse(studyGuide.id);
        return;
      }

      // For clusters, navigate immediately with the cluster ID
      // The CourseView component will handle the course creation in the background
      onViewCourse(studyGuide.id);
    } catch (err) {
      setError('Failed to start study guide');
      console.error('Error starting study guide:', err);
    }
  };
  return (
    <div className="flex-1 flex flex-col" style={{ backgroundColor: "#FAF9F5"}}>
      {/* Header */}
      <div className="border-b border-gray-50 p-4 bg-white">
        <div className="flex items-center justify-between">
          <h1 className="text-lg font-medium text-gray-900">
            Claude Mastery
          </h1>
          <div className="text-sm text-gray-500">
            AI Conversation Analysis & Learning
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto">
          {/* Welcome Section */}
          <div className="text-center mb-8">
            <div className="flex items-center justify-center gap-3 mb-4">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-2xl">🧠</span>
              </div>
              <h2 className="text-2xl font-semibold text-gray-900">
                Build Your AI Mastery
              </h2>
            </div>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Transform your AI interactions into structured learning experiences. 
              Analyze conversation patterns, identify knowledge gaps, and build long-term expertise.
            </p>
          </div>

          {/* Error State */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <div className="flex items-center gap-2">
                <span className="text-red-600">⚠️</span>
                <span className="text-red-800 font-medium">Error</span>
              </div>
              <p className="text-red-700 text-sm mt-1">{error}</p>
              <button 
                onClick={fetchStudyData}
                className="mt-2 text-red-600 text-sm font-medium hover:text-red-700"
              >
                Try Again
              </button>
            </div>
          )}

          {/* Loading State */}
          {loading && (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="text-gray-600 mt-2">Loading semantic clusters...</p>
            </div>
          )}

          {/* Clustering Status */}
          {status && !loading && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-blue-900">Semantic Analysis Status</h3>
                  <p className="text-blue-700 text-sm">
                    {status.processed_messages} of {status.total_messages} messages analyzed 
                    ({Math.round(status.processing_progress * 100)}%)
                  </p>
                </div>
                <button
                  onClick={triggerClustering}
                  disabled={loading}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? 'Processing...' : 'Update Clusters'}
                </button>
              </div>
            </div>
          )}

          {/* Study Guide Topics */}
          {studyGuides.length > 0 && !loading && (
            <div className="mb-8">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-gray-900">Your Study Guide Topics</h3>
                <span className="text-sm text-gray-500">{studyGuides.length} study guides available</span>
              </div>
              
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {studyGuides.map((guide, index) => {
                  const colors = [
                    'bg-blue-100 text-blue-800',
                    'bg-green-100 text-green-800', 
                    'bg-purple-100 text-purple-800',
                    'bg-orange-100 text-orange-800',
                    'bg-red-100 text-red-800'
                  ];
                  const colorClass = colors[index % colors.length];
                  
                  return (
                    <div key={guide.id} className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow flex flex-col h-full">
                      <div className="flex items-center gap-3 mb-3">
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${colorClass}`}>
                          <span className="text-lg font-bold">{index + 1}</span>
                        </div>
                        <h3 className="font-semibold text-gray-900">{guide.label}</h3>
                      </div>
                      
                      <p className="text-gray-600 text-sm mb-4">
                        {guide.description}
                      </p>
                      
                      <div className="mb-4">
                        <div className="text-xs text-gray-500 mb-2">Key Concepts:</div>
                        <div className="flex flex-wrap gap-1">
                          {guide.key_concepts.slice(0, 3).map((concept, i) => (
                            <span key={i} className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">
                              {concept}
                            </span>
                          ))}
                          {guide.key_concepts.length > 3 && (
                            <span className="text-gray-500 text-xs">
                              +{guide.key_concepts.length - 3} more
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <div className="mb-4 flex-grow">
                        <span className="text-sm text-gray-500">
                          {guide.conversation_count} conversation{guide.conversation_count !== 1 ? 's' : ''}
                        </span>
                      </div>
                      
                      <div className="w-full mt-auto">
                        <button 
                          onClick={() => handleStartStudy(guide)}
                          className="w-full text-right text-blue-600 text-sm font-medium hover:text-blue-700"
                        >
                          {guide.type === 'course' ? 'Continue Course →' : 'Study This Topic →'}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Empty State */}
          {studyGuides.length === 0 && !loading && !error && (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">🤖</span>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Study Topics Yet</h3>
              <p className="text-gray-600 mb-4">
                Start having conversations to generate personalized study guides based on your topics.
              </p>
              <button
                onClick={triggerClustering}
                disabled={loading}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50"
              >
                Analyze Conversations
              </button>
            </div>
          )}

          {/* Quick Stats */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-900 mb-4">Your Learning Journey</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {status?.total_conversations || 0}
                </div>
                <div className="text-sm text-gray-600">Conversations Analyzed</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {studyGuides.reduce((sum, guide) => sum + guide.key_concepts.length, 0)}
                </div>
                <div className="text-sm text-gray-600">Technical Concepts</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {studyGuides.length}
                </div>
                <div className="text-sm text-gray-600">Study Topics</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {status ? Math.round(status.processing_progress * 100) : 0}%
                </div>
                <div className="text-sm text-gray-600">Analysis Progress</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ClaudeMastery
