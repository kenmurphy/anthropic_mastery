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
      className="border-r border-gray-200 flex flex-col px-2 w-[290px] box-content"
    >
      {/* Header */}
      <div className="p-2">
        <h1
          className="text-md font-semibold text-gray-900"
          style={{
            fontFamily: 'copernicus, "copernicus Fallback", Georgia, "Times New Roman", Times, serif',
            fontSize: 18,
            fontWeight: 400,
          }}
        >
          Claude
        </h1>
        
        {/* New Chat Button */}
        <button 
          onClick={onStartNewChat}
          className="w-full flex items-center gap-3 px-2 py-2 text-gray-700 hover:bg-gray-100 rounded-md transition-colors text-left mt-4">
          <div
            className="w-6 h-6 rounded-full flex items-center justify-center"
            style={{ backgroundColor: '#F97316', marginRight: '4px', width: '24px', height: '24px' }}
          >
            <span className="text-md text-white">+</span>
          </div>
          <span className="text-sm font-medium" style={{ color: '#F97316' }}>New chat</span>
        </button>
      </div>

      {/* Navigation */}
      <div className="px-2 py-3">
        <nav className="space-y-1">
          <button className="w-full flex items-center px-2 py-2 text-gray-700 hover:bg-gray-100 rounded-md transition-colors text-left">
            <div className="w-5 h-5 flex items-center justify-center mr-2">
              <span className="text-gray-500">💬</span>
            </div>
            <span className="text-sm">Chats</span>
          </button>
          <button className="w-full flex items-center px-2 py-2 text-gray-700 hover:bg-gray-100 rounded-md transition-colors text-left">
            <div className="w-5 h-5 flex items-center justify-center mr-2">
              <span className="text-gray-500">📁</span>
            </div>
            <span className="text-sm">Projects</span>
          </button>
          <button className="w-full flex items-center px-2 py-2 text-gray-700 hover:bg-gray-100 rounded-md transition-colors text-left">
            <div className="w-5 h-5 flex items-center justify-center mr-2">
              <span className="text-gray-500">🎨</span>
            </div>
            <span className="text-sm">Artifacts</span>
          </button>
          <button 
            onClick={onClaudeMasteryClick}
            className="w-full flex items-center px-2 py-2 text-gray-700 hover:bg-gray-100 rounded-md transition-colors text-left">
            <div className="w-5 h-5 flex items-center justify-center mr-2">
              <span className="text-gray-500">🧠</span>
            </div>
            <span className="text-sm">Claude Mastery</span>
          </button>
        </nav>
      </div>

      {/* Recents Section */}
      <div className="flex-1 px-4 py-3 overflow-y-auto">
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
    </div>
  )
}

export default Sidebar
