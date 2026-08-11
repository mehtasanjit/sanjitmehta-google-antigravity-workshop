import React, { useState, useEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'
import { ThumbsUp, Send, HelpCircle, MessageSquare, ArrowLeft } from 'lucide-react'

interface Question {
  id: string
  content: string
  upvotes: number
  hasUpvoted: boolean
  timestamp: string
}

function SessionPage() {
  const { code } = useParams<{ code: string }>()
  const cleanCode = (code || '').toUpperCase()

  const [session, setSession] = useState<{ title: string; description?: string } | null>(null)
  const [activePulse, setActivePulse] = useState<string | null>(null)
  const [pulseMessage, setPulseMessage] = useState('')
  const [questionContent, setQuestionContent] = useState('')
  const [questions, setQuestions] = useState<Question[]>([])
  const [upvotedIds, setUpvotedIds] = useState<string[]>([])
  const socketRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    // 1. Fetch initial session details
    const fetchSessionDetails = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/sessions/${cleanCode}`)
        if (response.ok) {
          const data = await response.json()
          setSession({
            title: data.title,
            description: data.description,
          })

          const mappedQuestions = (data.questions || [])
            .filter((q: any) => q.status === 'active')
            .map((q: any) => ({
              id: q.id.toString(),
              content: q.text,
              upvotes: q.upvotes,
              hasUpvoted: false,
              timestamp: 'Earlier',
            }))
          setQuestions(mappedQuestions)
        }
      } catch (err) {
        console.error('Error fetching session details:', err)
      }
    }

    fetchSessionDetails()

    // 2. Connect WebSocket
    const ws = new WebSocket(`ws://localhost:8000/ws/${cleanCode}`)
    socketRef.current = ws

    ws.onopen = () => {
      console.log('WebSocket connected')
    }

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        const type = (message.type || '').toUpperCase()

        if (type === 'NEW_QUESTION') {
          const q = message.question
          if (q && q.status === 'active') {
            setQuestions((prev) => {
              if (prev.some((item) => item.id === q.id.toString())) {
                return prev
              }
              const newQ: Question = {
                id: q.id.toString(),
                content: q.text,
                upvotes: q.upvotes,
                hasUpvoted: false,
                timestamp: 'Just now',
              }
              return [newQ, ...prev]
            })
          }
        } else if (type === 'UPVOTE_QUESTION') {
          setQuestions((prev) => {
            return prev
              .map((q) => {
                if (q.id === message.question_id.toString()) {
                  return { ...q, upvotes: message.upvotes }
                }
                return q
              })
              .sort((a, b) => b.upvotes - a.upvotes)
          })
        } else if (type === 'UPDATE_QUESTION_STATUS' || type === 'QUESTION_UPDATED') {
          const status = message.status
          if (status && status !== 'active') {
            setQuestions((prev) => prev.filter((q) => q.id !== message.question_id.toString()))
          }
        } else if (type === 'PULSE_UPDATE' || type === 'PULSE_EVENT') {
          console.log('Pulse update received:', message.pulse_totals)
        }
      } catch (err) {
        console.error('WebSocket parsing error:', err)
      }
    }

    ws.onclose = () => {
      console.log('WebSocket disconnected')
    }

    return () => {
      ws.close()
    }
  }, [cleanCode])

  const handlePulse = (pulseType: 'slower' | 'confused' | 'got_it') => {
    setActivePulse(pulseType)
    let message = ''
    switch (pulseType) {
      case 'slower':
        message = 'Sent signal: Needs slower pace ⏳'
        break
      case 'confused':
        message = 'Sent signal: Feeling confused ❓'
        break
      case 'got_it':
        message = 'Sent signal: Understood perfectly! ✨'
        break
    }
    setPulseMessage(message)
    setTimeout(() => {
      setPulseMessage('')
    }, 3000)

    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(
        JSON.stringify({
          type: 'pulse',
          pulse_type: pulseType,
        })
      )
    }
  }

  const handleQuestionSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!questionContent.trim()) return

    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(
        JSON.stringify({
          type: 'new_question',
          text: questionContent.trim(),
        })
      )
      setQuestionContent('')
    }
  }

  const handleUpvote = (id: string) => {
    if (upvotedIds.includes(id)) return

    setUpvotedIds((prev) => [...prev, id])

    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(
        JSON.stringify({
          type: 'upvote_question',
          question_id: parseInt(id, 10),
        })
      )
    }
  }

  return (
    <div className="max-w-4xl mx-auto w-full space-y-8 py-4">
      {/* Session Title Bar */}
      <div className="flex items-center justify-between glass-card p-6 rounded-2xl">
        <div className="flex items-center gap-3">
          <a href="/join" className="p-2 hover:bg-white/5 rounded-lg transition-colors text-slate-400 hover:text-white">
            <ArrowLeft className="h-5 w-5" />
          </a>
          <div>
            <h1 className="text-xl font-bold text-white flex items-center gap-2">
              {session?.title || 'Lecture Session'}
              <span className="px-2.5 py-0.5 text-xs font-bold bg-indigo-500/15 text-indigo-400 rounded-full border border-indigo-500/25 tracking-wider uppercase">
                {cleanCode}
              </span>
            </h1>
            <p className="text-xs text-slate-400 mt-0.5">
              {session?.description || 'Anonymous, secure, and low-pressure engagement'}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 bg-emerald-500 rounded-full animate-pulse"></span>
          <span className="text-xs text-slate-400 font-semibold tracking-wide">Connected Live</span>
        </div>
      </div>

      {/* Grid Layout: Left Column (Pulse Controls), Right Column (Q&A Feed) */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
        
        {/* Pulse Check Box */}
        <div className="md:col-span-5 space-y-6">
          <div className="glass-card p-6 rounded-2xl relative overflow-hidden">
            <h2 className="text-lg font-bold text-white mb-1">Your Pulse Check</h2>
            <p className="text-xs text-slate-400 mb-6">Let your lecturer know how you are following right now. Change your pulse at any time.</p>
            
            <div className="space-y-4">
              {/* Slower (Amber) */}
              <button
                onClick={() => handlePulse('slower')}
                className={`w-full flex items-center justify-between p-4 rounded-xl font-semibold border transition-all ${
                  activePulse === 'slower'
                    ? 'bg-amber-500/20 border-amber-500 text-amber-300 shadow-lg shadow-amber-500/10'
                    : 'bg-slate-900/50 border-white/5 text-slate-300 hover:border-amber-500/30 hover:bg-slate-900/80'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">⏳</span>
                  <span className="tracking-wide">Too Fast / Slower</span>
                </div>
                <span className="text-xs text-amber-500/80 font-bold bg-amber-500/10 px-2 py-0.5 rounded">Pace</span>
              </button>

              {/* Confused (Crimson) */}
              <button
                onClick={() => handlePulse('confused')}
                className={`w-full flex items-center justify-between p-4 rounded-xl font-semibold border transition-all ${
                  activePulse === 'confused'
                    ? 'bg-rose-500/20 border-rose-500 text-rose-300 shadow-lg shadow-rose-500/10'
                    : 'bg-slate-900/50 border-white/5 text-slate-300 hover:border-rose-500/30 hover:bg-slate-900/80'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">❓</span>
                  <span className="tracking-wide">I am Confused</span>
                </div>
                <span className="text-xs text-rose-500/80 font-bold bg-rose-500/10 px-2 py-0.5 rounded">Help</span>
              </button>

              {/* Got It (Green) */}
              <button
                onClick={() => handlePulse('got_it')}
                className={`w-full flex items-center justify-between p-4 rounded-xl font-semibold border transition-all ${
                  activePulse === 'got_it'
                    ? 'bg-emerald-500/20 border-emerald-500 text-emerald-300 shadow-lg shadow-emerald-500/10'
                    : 'bg-slate-900/50 border-white/5 text-slate-300 hover:border-emerald-500/30 hover:bg-slate-900/80'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">✨</span>
                  <span className="tracking-wide">I Got It!</span>
                </div>
                <span className="text-xs text-emerald-500/80 font-bold bg-emerald-500/10 px-2 py-0.5 rounded">Clear</span>
              </button>
            </div>

            {pulseMessage && (
              <div className="mt-4 p-3 bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-semibold rounded-lg text-center animate-fade-in">
                {pulseMessage}
              </div>
            )}
          </div>
        </div>

        {/* Q&A Section */}
        <div className="md:col-span-7 space-y-6">
          {/* Ask Question Form */}
          <div className="glass-card p-6 rounded-2xl">
            <h2 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <HelpCircle className="h-5 w-5 text-indigo-400" />
              Ask a Question
            </h2>
            <p className="text-xs text-slate-400 mb-4">Your question is posted anonymously. Other students can see and upvote it.</p>
            
            <form onSubmit={handleQuestionSubmit} className="space-y-3">
              <div className="relative">
                <textarea
                  rows={2}
                  maxLength={180}
                  value={questionContent}
                  onChange={(e) => setQuestionContent(e.target.value)}
                  placeholder="e.g. Can you explain the difference between Rest and WebSockets again?"
                  className="w-full px-4 py-3 bg-slate-900/50 border border-white/10 rounded-xl text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all text-sm resize-none text-white"
                />
                <span className="absolute bottom-2.5 right-3 text-[10px] font-semibold text-slate-600">
                  {questionContent.length}/180
                </span>
              </div>
              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={!questionContent.trim()}
                  className="inline-flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:hover:bg-indigo-600 text-white font-semibold text-sm rounded-xl transition-all shadow-lg shadow-indigo-600/10 cursor-pointer"
                >
                  <Send className="h-4 w-4" />
                  Post Anonymously
                </button>
              </div>
            </form>
          </div>

          {/* Peer Questions Feed */}
          <div className="space-y-4">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <MessageSquare className="h-4 w-4" />
              Active Questions ({questions.length})
            </h3>

            {questions.length === 0 ? (
              <div className="glass-card p-8 rounded-2xl text-center">
                <HelpCircle className="mx-auto h-8 w-8 text-slate-600 mb-2" />
                <p className="text-slate-400 text-sm font-medium">No questions yet. Be the first to ask!</p>
              </div>
            ) : (
              <div className="space-y-3">
                {questions.map((q) => (
                  <div key={q.id} className="glass-card p-4 rounded-xl flex items-start justify-between gap-4">
                    <div className="space-y-1">
                      <p className="text-slate-200 text-sm leading-relaxed">{q.content}</p>
                      <span className="text-[10px] text-slate-500 font-semibold">{q.timestamp} • Anonymous</span>
                    </div>
                    <button
                      onClick={() => handleUpvote(q.id)}
                      disabled={upvotedIds.includes(q.id)}
                      className={`flex flex-col items-center justify-center p-2.5 rounded-lg border transition-all ${
                        upvotedIds.includes(q.id)
                          ? 'bg-indigo-500/25 border-indigo-500 text-indigo-400 shadow-md shadow-indigo-500/5 cursor-not-allowed opacity-80'
                          : 'bg-slate-900/50 border-white/5 text-slate-400 hover:text-white hover:bg-slate-900/80'
                      }`}
                    >
                      <ThumbsUp className="h-4 w-4 mb-1" />
                      <span className="text-xs font-bold">{q.upvotes}</span>
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  )
}

export default SessionPage

