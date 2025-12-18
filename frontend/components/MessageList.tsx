import React, { useState, useEffect } from 'react'
import ProductCard from './ProductCard'

interface Message {
  role: 'user' | 'assistant'
  content: string
  products?: any[]
  isTyping?: boolean
  fullContent?: string
}

interface MessageListProps {
  messages: Message[]
}

// Convert markdown to HTML (links and bold)
const renderMessageContent = (content: string) => {
  const parts: (string | JSX.Element)[] = []
  let keyCounter = 0

  // Link regex:
  //  - Matches [link text](https://...)
  //  - Allows spaces/newlines between ] and (
  const linkRegex = /\[([^\]]+)\]\s*\((https?:\/\/[^)\s]+)\)/g
  // Fallback for bare URLs
  const urlRegex = /(https?:\/\/[^\s)]+)/g

  let lastIndex = 0
  let match: RegExpExecArray | null

  // First pass: handle all markdown links in order
  while ((match = linkRegex.exec(content)) !== null) {
    const matchIndex = match.index
    const fullMatch = match[0]
    const linkText = match[1]
    const url = match[2]

    // Text before this link → still process bold
    if (matchIndex > lastIndex) {
      const beforeText = content.substring(lastIndex, matchIndex)
      parts.push(...processBoldText(beforeText, keyCounter))
    }

    // Add the clickable link (product name only)
    parts.push(
      <a
        key={`link-${keyCounter++}`}
        href={url}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 hover:underline transition-all duration-200 cursor-pointer font-medium underline decoration-blue-500 decoration-2"
        onClick={(e) => {
          e.stopPropagation()
        }}
        style={{
          pointerEvents: 'auto',
          zIndex: 999,
          position: 'relative',
          display: 'inline',
          touchAction: 'auto',
          userSelect: 'auto',
        }}
      >
        <span>{linkText}</span>
        <span className="text-xs align-middle">↗</span>
      </a>
    )

    lastIndex = matchIndex + fullMatch.length
  }

  // Text after the last markdown link
  if (lastIndex < content.length) {
    const remainingText = content.substring(lastIndex)
    parts.push(...processBoldText(remainingText, keyCounter))
  }

  // If we didn't find any markdown links but there are bare URLs, auto-link them
  if (parts.length === 0 && urlRegex.test(content)) {
    const urlParts: (string | JSX.Element)[] = []
    let last = 0
    let urlMatch: RegExpExecArray | null
    urlRegex.lastIndex = 0

    while ((urlMatch = urlRegex.exec(content)) !== null) {
      const urlStart = urlMatch.index
      const urlText = urlMatch[0]

      if (urlStart > last) {
        urlParts.push(content.slice(last, urlStart))
      }

      urlParts.push(
        <a
          key={`auto-link-${keyCounter++}`}
          href={urlText}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 hover:underline transition-all duration-200 cursor-pointer font-medium underline decoration-blue-500 decoration-2"
          style={{
            pointerEvents: 'auto',
            zIndex: 999,
            position: 'relative',
            display: 'inline',
            touchAction: 'auto',
            userSelect: 'auto',
          }}
        >
          <span>{urlText}</span>
          <span className="text-xs align-middle">↗</span>
        </a>
      )

      last = urlStart + urlText.length
    }

    if (last < content.length) {
      urlParts.push(content.slice(last))
    }

    return urlParts
  }

  // If no links at all, still support bold text
  if (parts.length === 0) {
    return processBoldText(content, 0)
  }

  return parts
}

// Helper to process bold text in a string segment
const processBoldText = (text: string, startKey: number): (string | JSX.Element)[] => {
  const parts: (string | JSX.Element)[] = []
  const boldRegex = /\*\*([^*]+)\*\*/g
  let lastIndex = 0
  let match
  let keyCounter = startKey

  while ((match = boldRegex.exec(text)) !== null) {
    // Add text before the bold
    if (match.index > lastIndex) {
      parts.push(text.substring(lastIndex, match.index))
    }
    
    // Add the bold element
    parts.push(
      <strong key={`bold-${keyCounter++}`} className="font-semibold">
        {match[1]}
      </strong>
    )
    
    lastIndex = match.index + match[0].length
  }
  
  // Add remaining text
  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex))
  }
  
  return parts.length > 0 ? parts : [text]
}

export default function MessageList({ messages }: MessageListProps) {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])
  return (
    <div className="space-y-3">
      {messages.map((message, index) => (
        <div
          key={index}
          className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} ${
            message.role === 'user' ? 'message-enter-right' : 'message-enter-left'
          }`}
        >
          <div className={`${message.role === 'user' ? 'max-w-xs ml-auto' : 'max-w-lg'}`}>
            {/* Message bubble - no avatar for cleaner look */}
            <div className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {/* Message bubble */}
              <div className={message.role === 'user' ? '' : 'flex-1'}>
                <div
                  className={`rounded-2xl p-3 shadow-sm ${
                    message.role === 'user'
                      ? 'bg-gray-900 text-white border border-gray-800'
                      : 'bg-gray-100 text-gray-800 border border-gray-200'
                  }`}
                  style={{ pointerEvents: 'auto' }}
                >
                   <div 
                     className="whitespace-pre-wrap leading-relaxed text-sm message-content [&_a]:pointer-events-auto [&_a]:relative [&_a]:z-[999] [&_a]:cursor-pointer"
                     style={{ pointerEvents: 'auto' }}
                   >
                     {renderMessageContent(message.content)}
                     {message.isTyping && <span className="inline-block w-1 h-4 bg-gray-400 ml-1 animate-pulse"></span>}
                   </div>
                </div>
              </div>
            </div>

            {/* Product cards hidden - links are now inline in the text */}
          </div>
        </div>
      ))}
    </div>
  )
}


