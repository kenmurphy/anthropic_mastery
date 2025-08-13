import { useState, useCallback } from 'react'
import './App.css'
import Sidebar from './components/Sidebar'
import Conversation from './components/Conversation'
import ClaudeMastery from './components/ClaudeMastery'
import CourseView from './components/CourseView'

function App() {
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null)
  const [refreshConversations, setRefreshConversations] = useState<(() => void) | null>(null)
  const [currentTab, setCurrentTab] = useState<'conversation' | 'mastery' | 'course'>('conversation')
  const [currentCourseId, setCurrentCourseId] = useState<string | null>(null)
  const [currentClusterId, setCurrentClusterId] = useState<string | null>(null)

  const handleStartNewChat = () => {
    setCurrentConversationId(null)
    setCurrentTab('conversation')
  }

  const handleSelectConversation = (conversationId: string) => {
    setCurrentConversationId(conversationId)
    setCurrentTab('conversation')
  }

  const handleClaudeMasteryClick = () => {
    setCurrentTab('mastery')
  }

  const handleViewCourse = (courseId: string, clusterId?: string) => {
    console.log('App.handleViewCourse called with:', { courseId, clusterId });
    setCurrentCourseId(courseId)
    setCurrentClusterId(clusterId || null)
    setCurrentTab('course')
    console.log('App state updated:', { currentTab: 'course', currentCourseId: courseId, currentClusterId: clusterId });
  }

  const handleBackToMastery = () => {
    setCurrentTab('mastery')
    setCurrentCourseId(null)
    setCurrentClusterId(null)
  }

  const handleRefreshReady = useCallback((refreshFn: () => void) => {
    setRefreshConversations(() => () => refreshFn())
  }, [])

  const handleNewConversationCreated = (conversationId: string) => {
    setCurrentConversationId(conversationId)
    if (refreshConversations) {
      refreshConversations()
    }
  }

  return (
    <div className="h-screen flex">
      {/* Left Sidebar */}
      <Sidebar 
        onStartNewChat={handleStartNewChat}
        onSelectConversation={handleSelectConversation}
        currentConversationId={currentConversationId}
        onRefreshReady={handleRefreshReady}
        onClaudeMasteryClick={handleClaudeMasteryClick}
      />
      {currentTab === 'conversation' ? (
        <Conversation 
          conversationId={currentConversationId}
          onNewConversationCreated={handleNewConversationCreated}
        />
      ) : currentTab === 'course' && currentCourseId !== null ? (
        <CourseView 
          courseId={currentCourseId}
          clusterId={currentClusterId || undefined}
          onBack={handleBackToMastery}
        />
      ) : (
        <ClaudeMastery 
          onViewCourse={handleViewCourse}
        />
      )}
    </div>
  )
}

export default App
