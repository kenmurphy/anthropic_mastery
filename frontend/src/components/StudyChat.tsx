import { useState, useRef } from 'react'
import MarkdownRenderer from './MarkdownRenderer'
import { buildApiUrl } from '../config/api'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

interface StudyChatProps {
  courseTitle?: string
  activeConcept?: string
}

function StudyChat({ courseTitle, activeConcept }: StudyChatProps) {
  const [messages, setMessages] = useState<Message[]>([])
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

    // Add user message to local state
    const newUserMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    }
    
    setMessages(prev => [...prev, newUserMessage])

    try {
      // Build context for the study session
      const studyContext = {
        course_title: courseTitle || 'Study Session',
        active_concept: activeConcept,
        message: userMessage,
        message_history: messages.map(msg => ({
          role: msg.role,
          content: msg.content
        }))
      }

      const response = await fetch(buildApiUrl('/api/study/chat'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(studyContext)
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
                // Add assistant message to local state
                const assistantMessage: Message = {
                  id: `assistant-${Date.now()}`,
                  role: 'assistant',
                  content: accumulatedContent,
                  timestamp: new Date().toISOString()
                }
                
                setMessages(prev => [...prev, assistantMessage])
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
      
      // Add error message
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, errorMessage])
    }
  }

  const clearChat = () => {
    setMessages([])
    setMessage('')
    setStreamingContent('')
    setIsLoading(false)
  }

  return (
    <div className="flex flex-col h-full">
      {/* Chat Header */}
      <div className="border-b border-gray-100 p-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-semibold text-gray-900">Study Assistant</h3>
          {messages.length > 0 && (
            <button
              onClick={clearChat}
              className="text-xs text-gray-500 hover:text-gray-700 transition-colors"
            >
              Clear
            </button>
          )}
        </div>
        {courseTitle && (
          <p className="text-xs text-gray-600 mb-1">Course: {courseTitle}</p>
        )}
        {activeConcept && (
          <p className="text-xs text-blue-600">Studying: {activeConcept}</p>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <div className="text-center py-8">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p className="text-sm text-gray-600 mb-2">Ask me anything about your study topics!</p>
            <p className="text-xs text-gray-500">I can help explain concepts, answer questions, and provide examples.</p>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] rounded-lg p-3 text-sm ${
              msg.role === 'user' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-100 text-gray-900'
            }`}>
              {msg.role === 'user' ? (
                <div className="whitespace-pre-wrap">{msg.content}</div>
              ) : (
                <MarkdownRenderer content={msg.content} className="prose-invert" />
              )}
            </div>
          </div>
        ))}
        
        {/* Streaming Response */}
        {streamingContent && (
          <div className="flex justify-start">
            <div className="max-w-[85%] bg-gray-100 text-gray-900 rounded-lg p-3 text-sm">
              <MarkdownRenderer content={streamingContent} />
              <div className="mt-2 flex items-center text-gray-400">
                <div className="animate-pulse">●</div>
                <span className="ml-1 text-xs">Assistant is typing...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-100 p-4">
        <form onSubmit={handleSubmit} className="space-y-2">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask a question about your studies..."
            className="w-full min-h-[60px] max-h-[120px] px-3 py-2 text-sm border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
            className="w-full px-3 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <div className="flex items-center justify-center gap-2">
                <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Sending...</span>
              </div>
            ) : (
              'Ask Question'
            )}
          </button>
        </form>
      </div>
    </div>
  )
}

export default StudyChat
