import { useState, useEffect, useRef } from 'react'
import { useLocation, useParams } from 'react-router-dom'
import { 
  Smile, Frown, Hourglass, CheckCircle2, Trash2, 
  Monitor, Layout, QrCode, ArrowLeft, RefreshCw 
} from 'lucide-react'

interface ModQuestion {
  id: string
  content: string
  upvotes: number
}

function DashboardPage() {
  const location = useLocation()
  const { code } = useParams<{ code: string }>()
  const cleanCode = (code || '').toUpperCase()

  const state = location.state as { title?: string; description?: string } | null
  const [session, setSession] = useState<{ title: string; description?: string } | null>(null)
  
  const lectureTitle = session?.title || state?.title || 'CS 101: Introduction to WebSockets & Real-time Systems'
  const lectureDesc = session?.description || state?.description || 'Active lecture covering low-latency communications, pub-sub architectures, and bidirectional connection pooling.'

  const [presenterMode, setPresenterMode] = useState(false)
  const [pulse, setPulse] = useState({
    gotIt: 0,
    slower: 0,
    confused: 0
  })

  const [questions, setQuestions] = useState<ModQuestion[]>([])
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
          
          setPulse({
            gotIt: data.pulse_totals?.got_it ?? data.pulse_totals?.gotIt ?? 0,
            slower: data.pulse_totals?.slower ?? 0,
            confused: data.pulse_totals?.confused ?? 0,
          })

          const activeQuestions = (data.questions || [])
            .filter((q: any) => q.status === 'active')
            .map((q: any) => ({
              id: q.id.toString(),
              content: q.text,
              upvotes: q.upvotes,
            }))
            .sort((a: any, b: any) => b.upvotes - a.upvotes)
          setQuestions(activeQuestions)
        }
      } catch (err) {
        console.error('Error fetching dashboard details:', err)
      }
    }

    fetchSessionDetails()

    // 2. Connect WebSocket
    const ws = new WebSocket(`ws://localhost:8000/ws/${cleanCode}`)
    socketRef.current = ws

    ws.onopen = () => {
      console.log('Dashboard WebSocket connected')
    }

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        const type = (message.type || '').toUpperCase()

        if (type === 'PULSE_EVENT' || type === 'PULSE_UPDATE') {
          if (message.pulse_totals) {
            setPulse({
              gotIt: message.pulse_totals.got_it ?? message.pulse_totals.gotIt ?? 0,
              slower: message.pulse_totals.slower ?? 0,
              confused: message.pulse_totals.confused ?? 0,
            })
          }
        } else if (type === 'NEW_QUESTION') {
          const q = message.question
          if (q && q.status === 'active') {
            setQuestions((prev) => {
              if (prev.some((item) => item.id === q.id.toString())) {
                return prev
              }
              const newQ: ModQuestion = {
                id: q.id.toString(),
                content: q.text,
                upvotes: q.upvotes,
              }
              return [...prev, newQ].sort((a, b) => b.upvotes - a.upvotes)
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
        }
      } catch (err) {
        console.error('WebSocket parsing error in dashboard:', err)
      }
    }

    ws.onclose = () => {
      console.log('Dashboard WebSocket disconnected')
    }

    return () => {
      ws.close()
    }
  }, [cleanCode])

  const totalVotes = pulse.gotIt + pulse.slower + pulse.confused
  const getPercent = (count: number) => {
    if (totalVotes === 0) return 0
    return Math.round((count / totalVotes) * 100)
  }

  const handleMarkAnswered = (id: string) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(
        JSON.stringify({
          type: 'update_question_status',
          question_id: parseInt(id, 10),
          status: 'answered',
        })
      )
    }
  }

  const handleDismiss = (id: string) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(
        JSON.stringify({
          type: 'update_question_status',
          question_id: parseInt(id, 10),
          status: 'dismissed',
        })
      )
    }
  }

  const simulateRandomPulse = () => {
    const options = ['got_it', 'slower', 'confused']
    const choice = options[Math.floor(Math.random() * options.length)] as 'got_it' | 'slower' | 'confused'
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(
        JSON.stringify({
          type: 'pulse',
          pulse_type: choice,
        })
      )
    }
  }

  if (presenterMode) {
    return (
      <div className="fixed inset-0 bg-slate-950 text-white z-[9999] flex flex-col p-10 font-sans selection:bg-indigo-500">
        {/* Presenter Mode Top bar */}
        <div className="flex items-center justify-between border-b border-white/5 pb-8 mb-10">
          <div>
            <span className="text-sm font-bold uppercase tracking-widest text-indigo-400">Presenter Mode</span>
            <h1 className="text-4xl font-extrabold tracking-tight mt-1">{lectureTitle}</h1>
          </div>
          <div className="flex items-center gap-6">
            <div className="text-right">
              <span className="text-xs text-slate-500 font-bold block uppercase tracking-wider">Join Code</span>
              <span className="text-5xl font-black text-indigo-400 tracking-wider text-glow-green select-all">{cleanCode}</span>
            </div>
            <button 
              onClick={() => setPresenterMode(false)}
              className="px-6 py-3 bg-white/10 hover:bg-white/15 rounded-xl text-sm font-semibold tracking-wide border border-white/10 transition-all flex items-center gap-2 cursor-pointer"
            >
              <Layout className="h-4 w-4" />
              Exit Presenter Mode
            </button>
          </div>
        </div>

        {/* Presenter Mode Grid */}
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-10 min-h-0">
          {/* Sentiment gauge - Huge */}
          <div className="lg:col-span-7 flex flex-col justify-between glass-card p-10 rounded-3xl relative overflow-hidden">
            <div>
              <h2 className="text-2xl font-bold mb-8">Understanding Gauge</h2>
              <div className="grid grid-cols-3 gap-6 text-center">
                <div className="p-6 bg-emerald-500/10 rounded-2xl border border-emerald-500/20">
                  <Smile className="h-16 w-16 text-emerald-400 mx-auto mb-4 animate-bounce" />
                  <span className="text-5xl font-extrabold text-emerald-400">{getPercent(pulse.gotIt)}%</span>
                  <span className="text-xs font-semibold text-slate-400 block mt-2 uppercase tracking-wider">Got It ({pulse.gotIt})</span>
                </div>
                <div className="p-6 bg-amber-500/10 rounded-2xl border border-amber-500/20">
                  <Hourglass className="h-16 w-16 text-amber-400 mx-auto mb-4 animate-pulse" />
                  <span className="text-5xl font-extrabold text-amber-400">{getPercent(pulse.slower)}%</span>
                  <span className="text-xs font-semibold text-slate-400 block mt-2 uppercase tracking-wider">Slower ({pulse.slower})</span>
                </div>
                <div className="p-6 bg-rose-500/10 rounded-2xl border border-rose-500/20">
                  <Frown className="h-16 w-16 text-rose-400 mx-auto mb-4 animate-pulse" />
                  <span className="text-5xl font-extrabold text-rose-400">{getPercent(pulse.confused)}%</span>
                  <span className="text-xs font-semibold text-slate-400 block mt-2 uppercase tracking-wider">Confused ({pulse.confused})</span>
                </div>
              </div>
            </div>

            {/* Quick action simulation */}
            <div className="flex justify-between items-center pt-8 border-t border-white/5 mt-8">
              <span className="text-sm text-slate-500 font-medium">Total participants: {totalVotes} student pulses recorded</span>
              <button 
                onClick={simulateRandomPulse}
                className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors bg-white/5 px-3 py-1.5 rounded-lg border border-white/5 cursor-pointer"
              >
                <RefreshCw className="h-3 w-3 animate-spin" />
                Simulate Live Pulse
              </button>
            </div>
          </div>

          {/* Top question - huge list */}
          <div className="lg:col-span-5 flex flex-col justify-between glass-card p-10 rounded-3xl min-h-0">
            <div className="flex-1 flex flex-col min-h-0">
              <h2 className="text-2xl font-bold mb-6">Featured Question</h2>
              {questions.length === 0 ? (
                <div className="flex-1 flex flex-col items-center justify-center text-slate-500">
                  <CheckCircle2 className="h-16 w-16 text-slate-700 mb-4" />
                  <p className="text-lg font-medium">All questions have been answered!</p>
                </div>
              ) : (
                <div className="flex-1 flex flex-col justify-center bg-slate-900/40 border border-white/5 rounded-2xl p-8 relative overflow-hidden">
                  <div className="absolute top-4 left-4 bg-indigo-500/20 border border-indigo-500/30 text-indigo-400 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
                    Highest Voted (▲ {questions[0].upvotes})
                  </div>
                  <p className="text-2xl font-bold text-white leading-relaxed mt-6">
                    "{questions[0].content}"
                  </p>
                  <p className="text-sm text-slate-400 mt-4 font-semibold">— Anonymous Student</p>
                </div>
              )}
            </div>

            <div className="flex gap-4 mt-8">
              {questions.length > 0 && (
                <>
                  <button
                    onClick={() => handleMarkAnswered(questions[0].id)}
                    className="flex-1 py-4 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/10 cursor-pointer"
                  >
                    <CheckCircle2 className="h-5 w-5" />
                    Mark Answered
                  </button>
                  <button
                    onClick={() => handleDismiss(questions[0].id)}
                    className="py-4 px-6 bg-slate-900 hover:bg-slate-800 text-slate-300 font-semibold rounded-xl border border-white/5 hover:border-white/10 flex items-center justify-center cursor-pointer"
                  >
                    Dismiss
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 py-4">
      {/* Top Session Dashboard Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-card p-6 rounded-2xl">
        <div className="flex items-center gap-3">
          <a href="/create" className="p-2 hover:bg-white/5 rounded-lg transition-colors text-slate-400 hover:text-white">
            <ArrowLeft className="h-5 w-5" />
          </a>
          <div>
            <h1 className="text-xl font-bold text-white flex items-center gap-2">
              Lecturer Live Dashboard
              <span className="px-2.5 py-0.5 text-xs font-bold bg-indigo-500/15 text-indigo-400 rounded-full border border-indigo-500/25 tracking-wider">
                {cleanCode}
              </span>
            </h1>
            <p className="text-xs text-slate-400 mt-0.5">{lectureTitle}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setPresenterMode(true)}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm rounded-xl transition-all shadow-lg shadow-indigo-600/10 cursor-pointer"
          >
            <Monitor className="h-4 w-4" />
            Presenter Mode
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
        {/* Real-time Sentiment Gauge */}
        <div className="md:col-span-5 space-y-6">
          <div className="glass-card p-6 rounded-2xl">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Smile className="h-5 w-5 text-indigo-400" />
                Comprehension Gauge
              </h2>
              <button 
                onClick={simulateRandomPulse}
                className="p-1.5 bg-white/5 hover:bg-white/10 rounded-lg border border-white/5 text-slate-400 hover:text-white transition-all cursor-pointer"
                title="Simulate student activity"
              >
                <RefreshCw className="h-4 w-4" />
              </button>
            </div>

            <div className="space-y-6">
              {/* Got It (Green) */}
              <div className="space-y-2">
                <div className="flex justify-between text-xs font-bold tracking-wide">
                  <span className="text-emerald-400 uppercase">Got It ({pulse.gotIt})</span>
                  <span className="text-emerald-400 text-glow-green">{getPercent(pulse.gotIt)}%</span>
                </div>
                <div className="w-full bg-slate-900 rounded-full h-3 border border-white/5 overflow-hidden">
                  <div 
                    className="bg-gradient-to-r from-emerald-500 to-teal-400 h-full rounded-full transition-all duration-500" 
                    style={{ width: `${getPercent(pulse.gotIt)}%` }}
                  ></div>
                </div>
              </div>

              {/* Slower (Amber) */}
              <div className="space-y-2">
                <div className="flex justify-between text-xs font-bold tracking-wide">
                  <span className="text-amber-400 uppercase">Slower ({pulse.slower})</span>
                  <span className="text-amber-400 text-glow-yellow">{getPercent(pulse.slower)}%</span>
                </div>
                <div className="w-full bg-slate-900 rounded-full h-3 border border-white/5 overflow-hidden">
                  <div 
                    className="bg-gradient-to-r from-amber-500 to-orange-400 h-full rounded-full transition-all duration-500" 
                    style={{ width: `${getPercent(pulse.slower)}%` }}
                  ></div>
                </div>
              </div>

              {/* Confused (Crimson) */}
              <div className="space-y-2">
                <div className="flex justify-between text-xs font-bold tracking-wide">
                  <span className="text-rose-400 uppercase">Confused ({pulse.confused})</span>
                  <span className="text-rose-400 text-glow-red">{getPercent(pulse.confused)}%</span>
                </div>
                <div className="w-full bg-slate-900 rounded-full h-3 border border-white/5 overflow-hidden">
                  <div 
                    className="bg-gradient-to-r from-rose-500 to-pink-400 h-full rounded-full transition-all duration-500" 
                    style={{ width: `${getPercent(pulse.confused)}%` }}
                  ></div>
                </div>
              </div>
            </div>

            <div className="mt-8 pt-6 border-t border-white/5 text-center">
              <div className="inline-block p-4 bg-slate-900/50 rounded-2xl border border-white/5 text-center">
                <QrCode className="h-24 w-24 text-slate-300 mx-auto mb-2" />
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Scan to Join</span>
                <span className="text-sm font-black text-indigo-400 tracking-wider uppercase select-all">{cleanCode}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Q&A Moderation Column */}
        <div className="md:col-span-7 space-y-6">
          <div className="glass-card p-6 rounded-2xl">
            <h2 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <Smile className="h-5 w-5 text-purple-400" />
              Student Q&A Feed ({questions.length})
            </h2>
            <p className="text-xs text-slate-400 mb-6">Moderation queue sorted by student upvotes. Mark questions answered as you address them.</p>

            {questions.length === 0 ? (
              <div className="p-8 text-center bg-slate-900/20 border border-dashed border-white/5 rounded-2xl">
                <CheckCircle2 className="mx-auto h-8 w-8 text-emerald-500/80 mb-2" />
                <p className="text-slate-400 text-sm font-medium">All student questions cleared!</p>
              </div>
            ) : (
              <div className="space-y-4">
                {questions.map((q) => (
                  <div key={q.id} className="p-4 bg-slate-900/30 border border-white/5 rounded-xl flex items-start justify-between gap-4">
                    <div className="space-y-2">
                      <p className="text-slate-200 text-sm leading-relaxed font-medium">"{q.content}"</p>
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/15 px-2 py-0.5 rounded">
                          ▲ {q.upvotes} votes
                        </span>
                        <span className="text-[10px] text-slate-500 font-semibold">Anonymous</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleMarkAnswered(q.id)}
                        className="p-2 bg-emerald-500/10 hover:bg-emerald-500/25 border border-emerald-500/20 hover:border-emerald-500/40 text-emerald-400 rounded-lg transition-all cursor-pointer"
                        title="Mark Answered"
                      >
                        <CheckCircle2 className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDismiss(q.id)}
                        className="p-2 bg-slate-800 hover:bg-slate-750 border border-white/5 text-slate-400 hover:text-rose-400 rounded-lg transition-all cursor-pointer"
                        title="Dismiss Question"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
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

export default DashboardPage
