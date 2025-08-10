import { useState, useRef, useEffect } from 'react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

interface ConversationData {
  id: string
  title: string
  messages: Message[]
}

interface ConversationProps {
  conversationId: string | null
  onNewConversationCreated?: (conversationId: string) => void
}

function Conversation({ conversationId, onNewConversationCreated }: ConversationProps) {
  const [currentConversation, setCurrentConversation] = useState<ConversationData | null>(null)
  const [message, setMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [streamingContent, setStreamingContent] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!message.trim() || isLoading) return

    const userMessage = message.trim()
    setMessage('')
    setIsLoading(true)
    setStreamingContent('')

    try {
      if (!currentConversation) {
        // Create new conversation
        const response = await fetch('http://localhost:5000/api/conversations', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            initial_message: userMessage
          })
        })

        if (!response.ok) {
          throw new Error('Failed to create conversation')
        }

        const newConversation = await response.json()
        setCurrentConversation(newConversation)

        // Notify parent component about new conversation
        if (onNewConversationCreated) {
          onNewConversationCreated(newConversation.id)
        }

        // Stream the first AI response (don't send message again, it's already in the conversation)
        await streamFirstAIResponse(newConversation.id)
      } else {
        // Add message to existing conversation
        await streamAIResponse(currentConversation.id, userMessage)
      }
    } catch (error) {
      console.error('Error:', error)
      setIsLoading(false)
    }
  }

  const streamFirstAIResponse = async (conversationId: string) => {
    try {
      // For the first AI response, we need to trigger AI response without adding another user message
      // We'll create a special endpoint or modify the existing one to handle this case
      // For now, let's use the conversation service to stream response directly
      const response = await fetch(`http://localhost:5000/api/conversations/${conversationId}/stream-response`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      })

      if (!response.ok) {
        throw new Error('Failed to stream AI response')
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('No response body')
      }

      let accumulatedContent = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = new TextDecoder().decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              
              if (data.content) {
                accumulatedContent += data.content
                setStreamingContent(accumulatedContent)
              }

              if (data.is_complete) {
                // Refresh conversation to get updated messages
                await refreshConversation(conversationId)
                setStreamingContent('')
                setIsLoading(false)
                return
              }

              if (data.error) {
                throw new Error(data.error)
              }
            } catch {
              // Ignore JSON parse errors for malformed chunks
            }
          }
        }
      }
    } catch (error) {
      console.error('Streaming error:', error)
      setIsLoading(false)
      setStreamingContent('')
    }
  }

  const streamAIResponse = async (conversationId: string, userMessage: string) => {
    try {
      const response = await fetch(`http://localhost:5000/api/conversations/${conversationId}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage
        })
      })

      if (!response.ok) {
        throw new Error('Failed to send message')
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('No response body')
      }

      let accumulatedContent = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = new TextDecoder().decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              
              if (data.content) {
                accumulatedContent += data.content
                setStreamingContent(accumulatedContent)
              }

              if (data.is_complete) {
                // Refresh conversation to get updated messages
                await refreshConversation(conversationId)
                setStreamingContent('')
                setIsLoading(false)
                return
              }

              if (data.error) {
                throw new Error(data.error)
              }
            } catch {
              // Ignore JSON parse errors for malformed chunks
            }
          }
        }
      }
    } catch (error) {
      console.error('Streaming error:', error)
      setIsLoading(false)
      setStreamingContent('')
    }
  }

  const refreshConversation = async (conversationId: string) => {
    try {
      const response = await fetch(`http://localhost:5000/api/conversations/${conversationId}`)

      if (response.ok) {
        const updatedConversation = await response.json()
        setCurrentConversation(updatedConversation)
      }
    } catch (error) {
      console.error('Error refreshing conversation:', error)
    }
  }

  const startNewChat = () => {
    setCurrentConversation(null)
    setMessage('')
    setStreamingContent('')
    setIsLoading(false)
  }

  // Load conversation when conversationId changes
  useEffect(() => {
    if (conversationId) {
      // Load existing conversation
      const loadConversation = async () => {
        try {
          const response = await fetch(`http://localhost:5000/api/conversations/${conversationId}`)
          if (response.ok) {
            const conversation = await response.json()
            setCurrentConversation(conversation)
          } else {
            console.error('Failed to load conversation')
            setCurrentConversation(null)
          }
        } catch (error) {
          console.error('Error loading conversation:', error)
          setCurrentConversation(null)
        }
      }
      loadConversation()
    } else {
      // Reset to new conversation state
      setCurrentConversation(null)
      setMessage('')
      setStreamingContent('')
      setIsLoading(false)
    }
  }, [conversationId])

  return (
    <div className="flex-1 flex flex-col" style={{ backgroundColor: "#FAF9F5"}}>
      {currentConversation ? (
        /* Conversation View */
        <div className="flex-1 flex flex-col">
          {/* Conversation Header */}
          <div className="border-b border-gray-50 p-4 bg-white">
            <div className="flex items-center justify-between">
              <h1 className="text-lg font-medium text-gray-900 truncate">
                {currentConversation.title}
              </h1>
              <button
                onClick={startNewChat}
                className="px-3 py-1 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
              >
                New Chat
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {currentConversation.messages?.map((msg) => (
              <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[70%] rounded-lg p-3 ${
                  msg.role === 'user' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-white border border-gray-50 text-gray-900'
                }`}>
                  <div className="whitespace-pre-wrap">{msg.content}</div>
                </div>
              </div>
            ))}
            
            {/* Streaming Response */}
            {streamingContent && (
              <div className="flex justify-start">
                <div className="max-w-[70%] bg-white border border-gray-50 text-gray-900 rounded-lg p-3">
                  <div className="whitespace-pre-wrap">{streamingContent}</div>
                  <div className="mt-2 flex items-center text-gray-400">
                    <div className="animate-pulse">●</div>
                    <span className="ml-1 text-xs">Claude is typing...</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-50 p-4 bg-white">
            <form onSubmit={handleSubmit} className="flex gap-2">
              <textarea
                ref={textareaRef}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Type your message..."
                className="flex-1 min-h-[40px] max-h-[120px] px-3 py-2 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={isLoading}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleSubmit(e)
                  }
                }}
              />
              <button
                type="submit"
                disabled={!message.trim() || isLoading}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  'Send'
                )}
              </button>
            </form>
          </div>
        </div>
      ) : (
        /* Welcome View */
        <div className="flex-1 flex items-center justify-center px-8">
          <div className="max-w-2xl w-full">
            {/* Greeting */}
            <div className="text-center mb-8">
              <div className="flex items-center justify-center gap-3 mb-4">
                <div className="inline-block align-middle md:mr-3" style={{ paddingTop: "0.2rem", transform: "none" }}>
                  <div
                    className="transition-colors text-[#D97757] inline-block"
                    style={{ position: "relative", height: "auto", minHeight: "32px", width: "32px" }}
                  >
                    <svg
                      overflow="visible"
                      width="32"
                      height="32"
                      viewBox="0 0 100 101"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                      role="presentation"
                    >
                      <path d="M96.0000 40.0000 L99.5002 42.0000 L99.5002 43.5000 L98.5000 47.0000 L56.0000 57.0000 L52.0040 47.0708 L96.0000 40.0000 M96.0000 40.0000 " fill="currentColor" style={{ transformOrigin: "50px 50px", transform: "rotate(330deg) scaleY(1.11809) rotate(-330deg)" }} />
                      <path d="M80.1032 10.5903 L84.9968 11.6171 L86.2958 13.2179 L87.5346 17.0540 L87.0213 19.5007 L58.5000 58.5000 L49.0000 49.0000 L75.3008 14.4873 L80.1032 10.5903 M80.1032 10.5903 " fill="currentColor" style={{ transformOrigin: "50px 50px", transform: "rotate(300deg) scaleY(1.17142) rotate(-300deg)" }} />
                      <path d="M55.5002 4.5000 L58.5005 2.5000 L61.0002 3.5000 L63.5002 7.0000 L56.6511 48.1620 L52.0005 45.0000 L50.0005 39.5000 L53.5003 8.5000 L55.5002 4.5000 M55.5002 4.5000 " fill="currentColor" style={{ transformOrigin: "50px 50px", transform: "rotate(270deg) scaleY(1.01476) rotate(-270deg)" }} />
                      <path d="M23.4253 5.1588 L26.5075 1.2217 L28.5175 0.7632 L32.5063 1.3458 L34.4748 2.8868 L48.8202 34.6902 L54.0089 49.8008 L47.9378 53.1760 L24.8009 11.1886 L23.4253 5.1588 M23.4253 5.1588 " fill="currentColor" style={{ transformOrigin: "50px 50px", transform: "rotate(240deg) scaleY(0.94) rotate(-240deg)" }} />
                      <path d="M8.4990 27.0019 L7.4999 23.0001 L10.5003 19.5001 L14.0003 20.0001 L15.0003 20.0001 L36.0000 35.5000 L42.5000 40.5000 L51.5000 47.5000 L46.5000 56.0000 L42.0002 52.5000 L39.0001 49.5000 L10.0000 29.0001 L8.4990 27.0019 M8.4990 27.0019 " fill="currentColor" style={{ transformOrigin: "50px 50px", transform: "rotate(210deg) scaleY(1.03) rotate(-210deg)" }} />
                      <path d="M2.5003 53.0000 L0.2370 50.5000 L0.2373 48.2759 L2.5003 47.5000 L28.0000 49.0000 L53.0000 51.0000 L52.1885 55.9782 L4.5000 53.5000 L2.5003 53.0000 M2.5003 53.0000 " fill="currentColor" style={{ transformOrigin: "50px 50px", transform: "rotate(180deg) scaleY(0.97) rotate(-180deg)" }} />
                      <path d="M17.5002 79.0264 L12.5005 79.0264 L10.5124 76.7369 L10.5124 74.0000 L19.0005 68.0000 L53.5082 46.0337 L57.0005 52.0000 L17.5002 79.0264 M17.5002 79.0264 " fill="currentColor" style={{ transformOrigin: "50px 50px", transform: "rotate(150deg) scaleY(1.06) rotate(-150deg)" }} />
                      <path d="M27.0004 92.9999 L25.0003 93.4999 L22.0003 91.9999 L22.5004 89.4999 L52.0003 50.5000 L56.0004 55.9999 L34.0003 85.0000 L27.0004 92.9999 M27.0004 92.9999 " fill="currentColor" style={{ transformOrigin: "50px 50px", transform: "rotate(120deg) scaleY(0.997) rotate(-120deg)" }} />
                      <path d="M51.9998 98.0000 L50.5002 100.0000 L47.5002 101.0000 L45.0001 99.0000 L43.5000 96.0000 L51.0003 55.4999 L55.5001 55.9999 L51.9998 98.0000 M51.9998 98.0000 " fill="currentColor" style={{ transformOrigin: "50px 50px", transform: "rotate(90deg) scaleY(1.075) rotate(-90deg)" }} />
                      <path d="M77.5007 86.9997 L77.5007 90.9997 L77.0006 92.4997 L75.0004 93.4997 L71.5006 93.0339 L47.4669 57.2642 L56.9998 50.0002 L64.9994 64.5004 L65.7507 69.7497 L77.5007 86.9997 M77.5007 86.9997 " fill="currentColor" style={{ transformOrigin: "50px 50px", transform: "rotate(60deg) scaleY(1.09691) rotate(-60deg)" }} />
                      <path d="M89.0008 80.9991 L89.5008 83.4991 L88.0008 85.4991 L86.5007 84.9991 L78.0007 78.9991 L65.0007 67.4991 L55.0007 60.4991 L58.0000 51.0000 L62.9999 54.0001 L66.0007 59.4991 L89.0008 80.9991 M89.0008 80.9991 " fill="currentColor" style={{ transformOrigin: "50px 50px", transform: "rotate(30deg) scaleY(1.08858) rotate(-30deg)" }} />
                      <path d="M82.5003 55.5000 L95.0003 56.5000 L98.0003 58.5000 L100.0000 61.5000 L100.0000 63.6587 L94.5003 66.0000 L66.5005 59.0000 L55.0003 58.5000 L58.0000 48.0000 L66.0005 54.0000 L82.5003 55.5000 M82.5003 55.5000 " fill="currentColor" style={{ transformOrigin: "50px 50px", transform: "rotate(0deg) scaleY(1.12524) rotate(0deg)" }} />
                    </svg>
                  </div>
                </div>
                <h2
                  style={{
                    fontSize: "40px",
                    fontWeight: 400,
                    fontFamily: 'copernicus, "copernicus Fallback", Georgia, "Times New Roman", Times, serif',
                    paddingLeft: "8px"
                  }}
                  className="text-gray-800"
                >
                  What's new?
                </h2>
              </div>
            </div>

            {/* Input Area */}
            <form onSubmit={handleSubmit} className="mb-6 flex justify-center">
              <div className="relative w-full max-w-[650px]">
                <textarea
                  ref={textareaRef}
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="How can I help you today?"
                  className="w-full min-h-[120px] pr-20 bg-white border border-gray-300 rounded-[16px] resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
                  style={{ padding: "12px", paddingRight: "80px" }}
                  disabled={isLoading}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault()
                      handleSubmit(e)
                    }
                  }}
                />
                <button
                  type="submit"
                  disabled={!message.trim() || isLoading}
                  className="absolute right-3 bottom-3 p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isLoading ? (
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                  )}
                </button>
              </div>
            </form>

            {/* Action Buttons */}
            <div className="flex justify-center gap-4">
              <button className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                </svg>
                <span className="text-sm text-gray-700">Write</span>
              </button>
              
              <button className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
                <span className="text-sm text-gray-700">Learn</span>
              </button>
              
              <button className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
                <span className="text-sm text-gray-700">Code</span>
              </button>
              
              <button className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
                <span className="text-sm text-gray-700">Life stuff</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Conversation
