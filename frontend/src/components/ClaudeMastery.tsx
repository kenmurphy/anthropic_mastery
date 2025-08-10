import React from 'react'

function ClaudeMastery() {
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

          {/* Feature Cards */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {/* Knowledge Map */}
            <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                  <span className="text-lg">🗺️</span>
                </div>
                <h3 className="font-semibold text-gray-900">Knowledge Map</h3>
              </div>
              <p className="text-gray-600 text-sm mb-4">
                Visualize your expertise areas and discover learning pathways based on your conversation history.
              </p>
              <button className="text-blue-600 text-sm font-medium hover:text-blue-700">
                Explore Map →
              </button>
            </div>

            {/* Learning Analytics */}
            <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                  <span className="text-lg">📊</span>
                </div>
                <h3 className="font-semibold text-gray-900">Learning Analytics</h3>
              </div>
              <p className="text-gray-600 text-sm mb-4">
                Track your progress, identify repetitive patterns, and measure your growing independence.
              </p>
              <button className="text-blue-600 text-sm font-medium hover:text-blue-700">
                View Analytics →
              </button>
            </div>

            {/* Flashcards */}
            <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center">
                  <span className="text-lg">🃏</span>
                </div>
                <h3 className="font-semibold text-gray-900">Smart Flashcards</h3>
              </div>
              <p className="text-gray-600 text-sm mb-4">
                AI-generated flashcards based on concepts you frequently ask about.
              </p>
              <button className="text-blue-600 text-sm font-medium hover:text-blue-700">
                Start Learning →
              </button>
            </div>

            {/* Feynman Technique */}
            <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                  <span className="text-lg">🎓</span>
                </div>
                <h3 className="font-semibold text-gray-900">Feynman Technique</h3>
              </div>
              <p className="text-gray-600 text-sm mb-4">
                Practice explaining concepts back to build deeper understanding and retention.
              </p>
              <button className="text-blue-600 text-sm font-medium hover:text-blue-700">
                Practice Explaining →
              </button>
            </div>

            {/* Weekly Summary */}
            <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
                  <span className="text-lg">📅</span>
                </div>
                <h3 className="font-semibold text-gray-900">Weekly Summary</h3>
              </div>
              <p className="text-gray-600 text-sm mb-4">
                Get insights on your learning patterns and suggested focus areas for the week.
              </p>
              <button className="text-blue-600 text-sm font-medium hover:text-blue-700">
                View Summary →
              </button>
            </div>

            {/* Practice Problems */}
            <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
                  <span className="text-lg">🎯</span>
                </div>
                <h3 className="font-semibold text-gray-900">Practice Problems</h3>
              </div>
              <p className="text-gray-600 text-sm mb-4">
                Solve problems with gradually reduced AI assistance to build independence.
              </p>
              <button className="text-blue-600 text-sm font-medium hover:text-blue-700">
                Start Practice →
              </button>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-900 mb-4">Your Learning Journey</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">0</div>
                <div className="text-sm text-gray-600">Conversations Analyzed</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">0</div>
                <div className="text-sm text-gray-600">Concepts Mastered</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">0</div>
                <div className="text-sm text-gray-600">Learning Sessions</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">0%</div>
                <div className="text-sm text-gray-600">Independence Score</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ClaudeMastery
