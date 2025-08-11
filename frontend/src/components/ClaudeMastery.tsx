import React, { useState, useEffect } from 'react'

interface Cluster {
  cluster_id: string;
  label: string;
  description: string;
  conversation_count: number;
  key_concepts: string[];
}

interface ClusteringStatus {
  total_conversations: number;
  total_messages: number;
  processed_messages: number;
  processing_progress: number;
  total_clusters: number;
}

function ClaudeMastery() {
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [status, setStatus] = useState<ClusteringStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchClusteringData();
  }, []);

  const fetchClusteringData = async () => {
    try {
      setLoading(true);
      
      // Fetch clusters and status in parallel
      const [clustersResponse, statusResponse] = await Promise.all([
        fetch('http://localhost:5000/api/clusters'),
        fetch('http://localhost:5000/api/clustering/status')
      ]);

      if (clustersResponse.ok) {
        const clustersData = await clustersResponse.json();
        setClusters(clustersData.clusters || []);
      }

      if (statusResponse.ok) {
        const statusData = await statusResponse.json();
        setStatus(statusData.status);
      }

      setError(null);
    } catch (err) {
      setError('Failed to load clustering data. Make sure the backend server is running.');
      console.error('Error fetching clustering data:', err);
    } finally {
      setLoading(false);
    }
  };

  const triggerClustering = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:5000/api/clustering/run', {
        method: 'POST'
      });

      if (response.ok) {
        // Refresh data after clustering
        await fetchClusteringData();
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
                onClick={fetchClusteringData}
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

          {/* Study Guide Clusters */}
          {clusters.length > 0 && !loading && (
            <div className="mb-8">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-gray-900">Your Study Guide Topics</h3>
                <span className="text-sm text-gray-500">{clusters.length} topic clusters found</span>
              </div>
              
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {clusters.map((cluster, index) => {
                  const colors = [
                    'bg-blue-100 text-blue-800',
                    'bg-green-100 text-green-800', 
                    'bg-purple-100 text-purple-800',
                    'bg-orange-100 text-orange-800',
                    'bg-red-100 text-red-800'
                  ];
                  const colorClass = colors[index % colors.length];
                  
                  return (
                    <div key={cluster.cluster_id} className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
                      <div className="flex items-center gap-3 mb-3">
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${colorClass}`}>
                          <span className="text-lg font-bold">{index + 1}</span>
                        </div>
                        <h3 className="font-semibold text-gray-900">{cluster.label}</h3>
                      </div>
                      
                      <p className="text-gray-600 text-sm mb-4">
                        {cluster.description}
                      </p>
                      
                      <div className="mb-4">
                        <div className="text-xs text-gray-500 mb-2">Key Concepts:</div>
                        <div className="flex flex-wrap gap-1">
                          {cluster.key_concepts.slice(0, 3).map((concept, i) => (
                            <span key={i} className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">
                              {concept}
                            </span>
                          ))}
                          {cluster.key_concepts.length > 3 && (
                            <span className="text-gray-500 text-xs">
                              +{cluster.key_concepts.length - 3} more
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-500">
                          {cluster.conversation_count} conversation{cluster.conversation_count !== 1 ? 's' : ''}
                        </span>
                        <button className="text-blue-600 text-sm font-medium hover:text-blue-700">
                          Study This Topic →
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Empty State */}
          {clusters.length === 0 && !loading && !error && (
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
                  {clusters.reduce((sum, cluster) => sum + cluster.key_concepts.length, 0)}
                </div>
                <div className="text-sm text-gray-600">Technical Concepts</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {status?.total_clusters || 0}
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
