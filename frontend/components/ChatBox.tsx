import React, { useState, useRef, useEffect } from 'react'
import ProductCard from './ProductCard'
import MessageList from './MessageList'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Message {
  role: 'user' | 'assistant'
  content: string
  products?: any[]
  isTyping?: boolean
  fullContent?: string
}

export default function ChatBox() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'How can I help?'
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [conversationHistory, setConversationHistory] = useState<Array<[string, string]>>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' })
    }
  }

  useEffect(() => {
    // Only scroll when assistant message typing completes, not during typing or when user submits
    const lastMessage = messages[messages.length - 1]
    if (lastMessage && lastMessage.role === 'assistant' && !lastMessage.isTyping) {
      // Only scroll after typing animation completes
      // Use setTimeout to ensure DOM is updated
      setTimeout(() => {
        scrollToBottom()
      }, 100)
    }
    // Don't scroll when user messages are added - user is already at input area
  }, [messages.length]) // Only trigger on new messages, not content updates

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')
    setIsLoading(true)

    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          conversation_history: conversationHistory
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      // Add assistant message with typing animation
      const fullResponse = data.response
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: '',
          products: data.products,
          isTyping: true,
          fullContent: fullResponse
        }
      ])

      // Typing animation
      let currentIndex = 0
      const typingInterval = setInterval(() => {
        currentIndex++
        const currentText = fullResponse.slice(0, currentIndex)
        
        setMessages(prev => {
          const newMessages = [...prev]
          const lastMessage = newMessages[newMessages.length - 1]
          if (lastMessage.role === 'assistant') {
            lastMessage.content = currentText
            if (currentIndex >= fullResponse.length) {
              lastMessage.isTyping = false
            }
          }
          return newMessages
        })

        if (currentIndex >= fullResponse.length) {
          clearInterval(typingInterval)
        }
      }, 20) // Adjust speed here (lower = faster)

      // Update conversation history
      setConversationHistory(prev => [
        ...prev,
        [userMessage, fullResponse]
      ])

    } catch (error) {
      console.error('Error sending message:', error)
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please make sure the backend server is running and try again.'
        }
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      e.stopPropagation()
      sendMessage()
    }
  }

  return (
    <div className="w-full glass-effect rounded-2xl overflow-hidden shadow-2xl">
      {/* Header */}
      <div className="bg-white p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {/* Kyocera logo from public folder */}
            <img
              src="/kyocera-logo.svg"
              alt="Kyocera logo"
              className="w-7 h-7"
            />
            <h2 className="text-gray-900 font-semibold text-base">Kyocera Unimerco — Product Finder</h2>
          </div>
          {/* Language selector */}
          <div className="bg-gray-100 rounded-full px-3 py-1.5 border border-gray-200">
            <span className="text-gray-700 text-xs font-medium">en-global</span>
          </div>
        </div>
      </div>

      {/* Chat messages */}
      <div className="h-[500px] overflow-y-auto p-4 bg-white">
        <MessageList messages={messages} />
        {isLoading && (
          <div className="flex justify-start mb-4 message-enter-left">
            <div className="bg-gray-100 rounded-2xl p-4 shadow-sm border border-gray-200">
              <div className="flex items-center gap-3">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
                  <div className="w-2 h-2 bg-gray-500 rounded-full typing-dot" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-gray-600 rounded-full typing-dot" style={{ animationDelay: '0.4s' }}></div>
                </div>
                <span className="text-sm text-gray-700 font-medium">AI is thinking...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="border-t border-gray-200 p-4 bg-white">
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              className="w-full border border-gray-300 rounded-2xl px-4 py-2.5 pr-10 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition-all duration-300 bg-gray-50 shadow-sm text-gray-900 placeholder-gray-500 text-sm"
              disabled={isLoading}
            />
          </div>
          <button
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            className="bg-red-600 hover:bg-red-700 disabled:bg-gray-300 text-white font-semibold py-2.5 px-5 rounded-2xl transition-all duration-300 shadow-md disabled:transform-none disabled:cursor-not-allowed text-sm"
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </span>
            ) : (
              <span>Send</span>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

