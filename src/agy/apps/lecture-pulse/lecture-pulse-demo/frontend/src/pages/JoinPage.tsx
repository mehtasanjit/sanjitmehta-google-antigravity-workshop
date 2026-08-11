import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, Sparkles, Users } from 'lucide-react'

function JoinPage() {
  const [code, setCode] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleJoin = (e: React.FormEvent) => {
    e.preventDefault()
    // Clean and validate code
    const cleanCode = code.trim().toUpperCase().replace(/[^A-Z0-9-]/g, '')
    
    if (!cleanCode) {
      setError('Please enter a room code')
      return
    }

    const unhyphenated = cleanCode.replace('-', '')
    if (unhyphenated.length !== 6) {
      setError('Room code must be exactly 6 characters (e.g. LP-392)')
      return
    }

    setError('')
    navigate(`/session/${cleanCode}`)
  }

  return (
    <div className="flex-1 flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 glass-card p-8 sm:p-10 rounded-2xl relative overflow-hidden animate-pulse-gentle">
        <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 rounded-full blur-2xl pointer-events-none"></div>
        <div className="absolute bottom-0 left-0 w-32 h-32 bg-purple-500/10 rounded-full blur-2xl pointer-events-none"></div>

        <div className="text-center">
          <div className="inline-flex items-center justify-center p-3 bg-indigo-500/10 rounded-xl mb-4 border border-indigo-500/20">
            <Users className="h-8 w-8 text-indigo-400" />
          </div>
          <h2 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-300 bg-clip-text text-transparent">
            Join Lecture Pulse
          </h2>
          <p className="mt-2.5 text-sm text-slate-400 max-w-sm mx-auto leading-relaxed">
            Enter the 6-character room code provided by your lecturer to join anonymously. No signup required.
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleJoin}>
          <div className="space-y-2">
            <label htmlFor="room-code" className="text-sm font-semibold tracking-wide text-slate-300 block">
              Session Code
            </label>
            <div className="relative rounded-lg shadow-sm">
              <input
                id="room-code"
                name="code"
                type="text"
                required
                maxLength={8}
                value={code}
                onChange={(e) => {
                  setCode(e.target.value)
                  if (error) setError('')
                }}
                className="w-full px-4 py-3.5 bg-slate-900/50 border border-white/10 rounded-xl text-center text-xl font-bold tracking-widest uppercase placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all text-white"
                placeholder="LP-123"
              />
            </div>
            {error && (
              <p className="text-sm text-rose-400 text-center font-medium mt-1">
                {error}
              </p>
            )}
          </div>

          <button
            type="submit"
            className="group relative w-full flex justify-center items-center gap-2 py-4 px-4 border border-transparent text-sm font-semibold rounded-xl text-white bg-indigo-600 hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-950 focus:ring-indigo-500 transition-all shadow-lg shadow-indigo-600/20 hover:shadow-indigo-600/30"
          >
            Join Session
            <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
          </button>
        </form>

        <div className="pt-6 border-t border-white/5 text-center">
          <p className="text-sm text-slate-400">
            Are you a lecturer?{' '}
            <a
              href="/create"
              className="inline-flex items-center gap-1 font-semibold text-indigo-400 hover:text-indigo-300 transition-colors"
            >
              Create a Session
              <Sparkles className="h-3 w-3" />
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}

export default JoinPage
