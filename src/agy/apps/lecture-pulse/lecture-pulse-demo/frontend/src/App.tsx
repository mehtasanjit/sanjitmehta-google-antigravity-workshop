import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import JoinPage from './pages/JoinPage'
import SessionPage from './pages/SessionPage'
import CreatePage from './pages/CreatePage'
import DashboardPage from './pages/DashboardPage'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-indigo-500 selection:text-white">
        <header className="border-b border-white/5 bg-slate-900/40 backdrop-blur-md sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <span className="text-2xl" role="img" aria-label="pulse-logo">⚡</span>
              <span className="font-bold text-xl tracking-tight bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                Lecture Pulse
              </span>
            </div>
            <nav className="flex items-center gap-4 text-sm font-medium text-slate-400">
              <a href="/join" className="hover:text-white transition-colors">Join Session</a>
              <span className="text-white/10">|</span>
              <a href="/create" className="hover:text-white transition-colors">Host Lecture</a>
            </nav>
          </div>
        </header>

        <main className="flex-1 flex flex-col max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Navigate to="/join" replace />} />
            <Route path="/join" element={<JoinPage />} />
            <Route path="/session/:code" element={<SessionPage />} />
            <Route path="/create" element={<CreatePage />} />
            <Route path="/dashboard/:code" element={<DashboardPage />} />
            <Route path="*" element={<Navigate to="/join" replace />} />
          </Routes>
        </main>

        <footer className="py-6 border-t border-white/5 text-center text-xs text-slate-500 bg-slate-950/80">
          <p>© {new Date().getFullYear()} Lecture Pulse. Empowering low-pressure academic feedback.</p>
        </footer>
      </div>
    </Router>
  )
}

export default App
