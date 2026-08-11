import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { PlusCircle, BookOpen, Sparkles, Settings } from 'lucide-react'

function CreatePage() {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const navigate = useNavigate()

  const generateRoomCode = () => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    let part1 = ''
    let part2 = ''
    for (let i = 0; i < 3; i++) {
      part1 += chars.charAt(Math.floor(Math.random() * chars.length))
      part2 += chars.charAt(Math.floor(Math.random() * chars.length))
    }
    return `LP-${part1}${part2}`
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim()) return

    setIsSubmitting(true)
    
    try {
      const response = await fetch('http://localhost:8000/api/sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: title.trim(),
          description: description.trim() || null,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to create session')
      }

      const data = await response.json()
      navigate(`/dashboard/${data.code}`, { state: { title: data.title, description: data.description || description } })
    } catch (error) {
      console.error('Error creating session:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="flex-1 flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-xl w-full space-y-8 glass-card p-8 sm:p-10 rounded-2xl relative overflow-hidden animate-pulse-gentle">
        <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/10 rounded-full blur-2xl pointer-events-none"></div>
        <div className="absolute bottom-0 left-0 w-32 h-32 bg-pink-500/10 rounded-full blur-2xl pointer-events-none"></div>

        <div className="text-center">
          <div className="inline-flex items-center justify-center p-3 bg-purple-500/10 rounded-xl mb-4 border border-purple-500/20">
            <PlusCircle className="h-8 w-8 text-purple-400" />
          </div>
          <h2 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-300 bg-clip-text text-transparent">
            Host a New Lecture
          </h2>
          <p className="mt-2.5 text-sm text-slate-400 max-w-md mx-auto leading-relaxed">
            Create an active, live feedback session for your classroom. We'll generate a unique 6-character room code for your students.
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleCreate}>
          <div className="space-y-4">
            <div className="space-y-1.5">
              <label htmlFor="title" className="text-sm font-semibold tracking-wide text-slate-300 block">
                Lecture Title
              </label>
              <input
                id="title"
                name="title"
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full px-4 py-3 bg-slate-900/50 border border-white/10 rounded-xl text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all text-sm"
                placeholder="e.g. CS101: Intro to WebSockets and Async API Design"
              />
            </div>

            <div className="space-y-1.5">
              <label htmlFor="description" className="text-sm font-semibold tracking-wide text-slate-300 block">
                Description (Optional)
              </label>
              <textarea
                id="description"
                name="description"
                rows={3}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full px-4 py-3 bg-slate-900/50 border border-white/10 rounded-xl text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all text-sm resize-none"
                placeholder="e.g. Discussing bi-directional event systems, socket states, and connection pooling."
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting || !title.trim()}
            className="group relative w-full flex justify-center items-center gap-2 py-4 px-4 border border-transparent text-sm font-semibold rounded-xl text-white bg-purple-600 hover:bg-purple-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-950 focus:ring-purple-500 transition-all shadow-lg shadow-purple-600/20 hover:shadow-purple-600/30 disabled:opacity-50 cursor-pointer"
          >
            {isSubmitting ? (
              <div className="flex items-center gap-2">
                <span className="h-4 w-4 border-2 border-white/20 border-t-white rounded-full animate-spin"></span>
                Generating Room Code...
              </div>
            ) : (
              <div className="flex items-center gap-2">
                Create Live Session
                <Sparkles className="h-4 w-4" />
              </div>
            )}
          </button>
        </form>

        <div className="pt-6 border-t border-white/5 flex items-center justify-around text-xs text-slate-500">
          <div className="flex items-center gap-1.5">
            <BookOpen className="h-4 w-4 text-slate-600" />
            <span>Interactive Q&A</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Settings className="h-4 w-4 text-slate-600" />
            <span>Real-time Pulse Analytics</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CreatePage
