import { useState, useEffect } from 'react'

interface Conversation {
  id: string
  title: string
  created_at: string
  updated_at: string
  message_count: number
}

interface SidebarProps {
  onStartNewChat: () => void
  onSelectConversation: (conversationId: string) => void
  currentConversationId: string | null
  onRefreshReady?: (refreshFn: () => void) => void
  onClaudeMasteryClick: () => void
}

function Sidebar({ onStartNewChat, onSelectConversation, currentConversationId, onRefreshReady, onClaudeMasteryClick }: SidebarProps) {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isCollapsed, setIsCollapsed] = useState(() => {
    const saved = localStorage.getItem('sidebarCollapsed')
    return saved ? JSON.parse(saved) : false
  })

  // Fetch conversations function
  const fetchConversations = async () => {
    setIsLoading(true)
    try {
      const response = await fetch('http://localhost:5000/api/conversations?limit=20')
      
      if (response.ok) {
        const data = await response.json()
        setConversations(data.conversations || [])
      } else {
        console.error('Failed to fetch conversations')
      }
    } catch (error) {
      console.error('Error fetching conversations:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // Fetch conversations on component mount
  useEffect(() => {
    fetchConversations()
  }, [])

  // Expose refresh function to parent
  useEffect(() => {
    if (onRefreshReady) {
      onRefreshReady(fetchConversations)
    }
  }, [onRefreshReady])

  // Toggle collapse function
  const toggleCollapse = () => {
    const newCollapsed = !isCollapsed
    setIsCollapsed(newCollapsed)
    localStorage.setItem('sidebarCollapsed', JSON.stringify(newCollapsed))
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60)
    
    if (diffInHours < 24) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    } else if (diffInHours < 24 * 7) {
      return date.toLocaleDateString([], { weekday: 'short' })
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' })
    }
  }

  return (
    <div
      className={`border-r border-gray-200 flex flex-col box-content transition-all duration-300 ${
        isCollapsed ? 'w-[48px]' : 'w-[290px] px-2'
      }`}
    >
      {/* Header */}
      <div className={`${isCollapsed ? ' py-2' : 'p-2'}`}>
        {/* Claude with Hamburger Menu */}
        <div className="flex items-center mb-2">
          <button
            onClick={toggleCollapse}
            className={`flex items-center justify-center text-gray-700 hover:bg-gray-100 rounded-md transition-colors${!isCollapsed ? ' p-2 mr-2' : ' w-full'}`}
            title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            <span className="text-lg">☰</span>
          </button>
          
          {!isCollapsed && (
            <h1
              className="text-md font-semibold text-gray-900 transition-opacity duration-300"
              style={{
                fontFamily: 'copernicus, "copernicus Fallback", Georgia, "Times New Roman", Times, serif',
                fontSize: 18,
                fontWeight: 400,
              }}
            >
              Claude
            </h1>
          )}
        </div>
        
        {/* New Chat Button */}
        <button 
          onClick={onStartNewChat}
          className={`w-full flex items-center${!isCollapsed ? ' px-2' : ''} py-2 text-gray-700 hover:bg-gray-100 rounded-md transition-colors text-left mt-4 ${
            isCollapsed ? 'justify-center' : 'gap-3'
          }`}
          title={isCollapsed ? "New chat" : undefined}
        >
          <div
            className="w-6 h-6 rounded-full flex items-center justify-center"
            style={{ 
              backgroundColor: '#F97316', 
              marginRight: isCollapsed ? '0' : '4px', 
              width: '24px', 
              height: '24px' 
            }}
          >
            <span className="text-md text-white">+</span>
          </div>
          {!isCollapsed && (
            <span className="text-sm font-medium transition-opacity duration-300" style={{ color: '#F97316' }}>
              New chat
            </span>
          )}
        </button>
      </div>

      {/* Navigation */}
      <div className="px-2 py-3">
        <nav className="space-y-1">
          <button 
            className={`w-full flex items-center px-2 py-2 text-gray-700 hover:bg-gray-100 rounded-md transition-colors text-left ${
              isCollapsed ? 'justify-center' : ''
            }`}
            title={isCollapsed ? "Chats" : undefined}
          >
            <div className={`w-5 h-5 flex items-center justify-center ${isCollapsed ? '' : 'mr-2'}`}>
              <span className="text-gray-500">💬</span>
            </div>
            {!isCollapsed && (
              <span className="text-sm transition-opacity duration-300">Chats</span>
            )}
          </button>
          <button 
            className={`w-full flex items-center px-2 py-2 text-gray-700 hover:bg-gray-100 rounded-md transition-colors text-left ${
              isCollapsed ? 'justify-center' : ''
            }`}
            title={isCollapsed ? "Projects" : undefined}
          >
            <div className={`w-5 h-5 flex items-center justify-center ${isCollapsed ? '' : 'mr-2'}`}>
              <span className="text-gray-500">📁</span>
            </div>
            {!isCollapsed && (
              <span className="text-sm transition-opacity duration-300">Projects</span>
            )}
          </button>
          <button 
            className={`w-full flex items-center px-2 py-2 text-gray-700 hover:bg-gray-100 rounded-md transition-colors text-left ${
              isCollapsed ? 'justify-center' : ''
            }`}
            title={isCollapsed ? "Artifacts" : undefined}
          >
            <div className={`w-5 h-5 flex items-center justify-center ${isCollapsed ? '' : 'mr-2'}`}>
              <span className="text-gray-500">🎨</span>
            </div>
            {!isCollapsed && (
              <span className="text-sm transition-opacity duration-300">Artifacts</span>
            )}
          </button>
          <button 
            onClick={onClaudeMasteryClick}
            className={`w-full flex items-center px-2 py-2 text-gray-700 hover:bg-gray-100 rounded-md transition-colors text-left ${
              isCollapsed ? 'justify-center' : ''
            }`}
            title={isCollapsed ? "Claude Mastery" : undefined}
          >
            <div className={`w-5 h-5 flex items-center justify-center ${isCollapsed ? '' : 'mr-2'}`}>
              <span className="text-gray-500">🧠</span>
            </div>
            {!isCollapsed && (
              <span className="text-sm transition-opacity duration-300">Claude Mastery</span>
            )}
          </button>
        </nav>
      </div>

      {/* Recents Section */}
      {!isCollapsed && (
        <div className="flex-1 px-4 py-3 overflow-y-auto transition-opacity duration-300">
          <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">Recents</h3>
          
          {isLoading ? (
            <div className="text-sm text-gray-400 italic">Loading conversations...</div>
          ) : conversations.length === 0 ? (
            <div className="text-sm text-gray-400 italic">No recent conversations</div>
          ) : (
            <div className="space-y-1">
              {conversations.map((conversation) => (
                <button
                  key={conversation.id}
                  onClick={() => onSelectConversation(conversation.id)}
                  className={`w-full text-left px-2 py-2 rounded-md transition-colors hover:bg-gray-100 ${
                    currentConversationId === conversation.id ? 'bg-gray-100' : ''
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-gray-900 truncate">
                        {conversation.title}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {conversation.message_count} message{conversation.message_count !== 1 ? 's' : ''}
                      </div>
                    </div>
                    <div className="text-xs text-gray-400 ml-2 flex-shrink-0">
                      {formatDate(conversation.updated_at)}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default Sidebar
