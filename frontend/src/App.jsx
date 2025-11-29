import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Toaster, toast } from 'react-hot-toast'
function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [username, setUsername] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [progressStep, setProgressStep] = useState(0)
  // Login State
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  // Provider State
  const [provider, setProvider] = useState('gemini')
  const [apiKey, setApiKey] = useState('')
  useEffect(() => {
    // Check for saved credentials
    const storedEmail = localStorage.getItem('linkedin_email')
    const storedPassword = localStorage.getItem('linkedin_password')
    if (storedEmail && storedPassword) {
      setEmail(storedEmail)
      setPassword(storedPassword)
      setIsLoggedIn(true)
    }
    // Check for saved provider settings
    const storedProvider = localStorage.getItem('llm_provider')
    const storedApiKey = localStorage.getItem('llm_api_key')
    if (storedProvider) setProvider(storedProvider)
    if (storedApiKey) setApiKey(storedApiKey)
  }, [])
  const handleLogin = (e) => {
    e.preventDefault()
    if (!email || !password) {
      toast.error('Please enter your LinkedIn credentials')
      return
    }
    if (!email.includes('@')) {
      toast.error('Please enter a valid email address')
      return
    }
    // Save credentials locally
    localStorage.setItem('linkedin_email', email)
    localStorage.setItem('linkedin_password', password)
    // Save provider settings
    localStorage.setItem('llm_provider', provider)
    localStorage.setItem('llm_api_key', apiKey)
    setIsLoggedIn(true)
    toast.success('Welcome back!')
  }
  const handleLogout = () => {
    localStorage.removeItem('linkedin_email')
    localStorage.removeItem('linkedin_password')
    setIsLoggedIn(false)
    setEmail('')
    setPassword('')
    setResult(null)
    toast.success('Signed out successfully')
  }
  const handleGenerate = async (e) => {
    e.preventDefault()
    if (!username.trim()) {
      toast.error('Please enter a LinkedIn username')
      return
    }
    // Save settings on generate too, just in case
    localStorage.setItem('llm_provider', provider)
    localStorage.setItem('llm_api_key', apiKey)
    setLoading(true)
    setResult(null)
    setProgressStep(0)
    // Simulate progress steps
    const steps = ['Connecting to LinkedIn...', 'Scraping Profile...', 'Analyzing Data...', 'Drafting Email...']
    let currentStep = 0
    const interval = setInterval(() => {
      if (currentStep < steps.length - 1) {
        currentStep++
        setProgressStep(currentStep)
      }
    }, 2000)
    try {
      // Construct full URL if just username provided
      let profileUrl = username
      if (!username.includes('linkedin.com')) {
        profileUrl = `https://www.linkedin.com/in/${username.replace('/', '')}/`
      }
      // Use environment variable for API URL or fallback to localhost
      let API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      // Ensure protocol is present
      if (!API_URL.startsWith('http')) {
        API_URL = `https://${API_URL}`
      }
      // Remove trailing slash if present
      if (API_URL.endsWith('/')) {
        API_URL = API_URL.slice(0, -1)
      }
      const response = await fetch(`${API_URL}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: profileUrl,
          linkedin_email: email || undefined,
          linkedin_password: password || undefined,
          llm_provider: provider,
          api_key: apiKey || undefined
        }),
      })
      const data = await response.json()
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to generate email')
      }
      setResult(data)
      toast.success('Magic email generated!')
    } catch (error) {
      console.error('Error:', error)
      toast.error(error.message)
    } finally {
      clearInterval(interval)
      setLoading(false)
      setProgressStep(0)
    }
  }
  return (
    <div className="min-h-screen text-white font-outfit overflow-hidden relative selection:bg-accent-pink selection:text-white">
      <Toaster position="top-center" toastOptions={{
        style: {
          background: 'rgba(15, 23, 42, 0.8)',
          color: '#fff',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
        }
      }} />
      {/* Floating Background Elements */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary-cyan/20 rounded-full blur-[120px] animate-pulse-slow" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-accent-purple/20 rounded-full blur-[120px] animate-pulse-slow delay-1000" />
        <div className="absolute top-[40%] left-[60%] w-[20%] h-[20%] bg-accent-pink/20 rounded-full blur-[100px] animate-pulse-slow delay-2000" />
      </div>
      <div className="container mx-auto px-4 py-8 relative z-10">
        <header className="flex justify-between items-center mb-12">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-cyan to-accent-purple flex items-center justify-center shadow-lg shadow-primary-cyan/20">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-primary-cyan to-accent-purple">
              LinkedIn<span className="font-light">Genius</span>
            </h1>
          </div>
          {isLoggedIn && (
            <button
              onClick={handleLogout}
              className="px-4 py-2 rounded-lg glass-card hover:bg-white/10 transition-all duration-300 text-sm font-medium text-red-300 hover:text-red-200"
            >
              Sign Out
            </button>
          )}
        </header>
        <AnimatePresence mode="wait">
          {!isLoggedIn ? (
            <motion.div
              key="login"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="max-w-md mx-auto"
            >
              <div className="glass-card p-8 rounded-3xl border border-white/10 shadow-2xl backdrop-blur-xl relative overflow-hidden group">
                <div className="absolute inset-0 bg-gradient-to-br from-primary-cyan/5 to-accent-purple/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <div className="text-center mb-8 relative z-10">
                  <h2 className="text-3xl font-bold mb-2">Welcome Back</h2>
                  <p className="text-gray-400">Enter your credentials to continue</p>
                </div>
                <form onSubmit={handleLogin} className="space-y-6 relative z-10">
                  {/* LinkedIn Credentials */}
                  <div className="space-y-4">
                    <h3 className="text-sm font-bold text-primary-cyan uppercase tracking-wider">LinkedIn Login</h3>
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-1 ml-1">Email</label>
                      <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="w-full bg-black/30 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:ring-2 focus:ring-primary-cyan focus:border-transparent outline-none transition-all"
                        placeholder="name@company.com"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-1 ml-1">Password</label>
                      <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full bg-black/30 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:ring-2 focus:ring-primary-cyan focus:border-transparent outline-none transition-all"
                        placeholder="••••••••"
                      />
                    </div>
                  </div>
                  {/* AI Settings */}
                  <div className="space-y-4 pt-4 border-t border-white/10">
                    <h3 className="text-sm font-bold text-accent-amber uppercase tracking-wider">AI Settings</h3>
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-1 ml-1">Provider</label>
                      <select
                        value={provider}
                        onChange={(e) => setProvider(e.target.value)}
                        className="w-full bg-black/30 border border-white/10 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-primary-cyan focus:border-transparent outline-none transition-all"
                      >
                        <option value="gemini">Google Gemini (Free)</option>
                        <option value="openai">OpenAI (GPT-4)</option>
                        <option value="azure">Azure OpenAI</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-1 ml-1">API Key</label>
                      <input
                        type="password"
                        value={apiKey}
                        onChange={(e) => setApiKey(e.target.value)}
                        placeholder="Enter your API Key"
                        className="w-full bg-black/30 border border-white/10 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-primary-cyan focus:border-transparent outline-none transition-all"
                      />
                    </div>
                  </div>
                  <button
                    type="submit"
                    className="w-full py-3.5 bg-gradient-to-r from-primary-cyan to-blue-500 rounded-xl font-bold text-white shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 transform hover:-translate-y-0.5 transition-all duration-300"
                  >
                    Save & Continue
                  </button>
                </form>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="generator"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="max-w-4xl mx-auto"
            >
              <div className="text-center mb-12">
                <h2 className="text-4xl md:text-5xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-white via-primary-cyan to-accent-purple animate-gradient-x">
                  Generate Magic Emails
                </h2>
                <p className="text-lg text-gray-400 max-w-2xl mx-auto">
                  Enter a LinkedIn username and let our AI craft the perfect outreach message.
                </p>
              </div>
              <div className="mb-12 relative z-10">
                <form onSubmit={handleGenerate} className="flex flex-col md:flex-row gap-4 max-w-2xl mx-auto mb-8">
                  <div className="flex-1 relative group">
                    <div className="absolute inset-0 bg-gradient-to-r from-primary-cyan to-accent-purple rounded-xl blur opacity-25 group-hover:opacity-50 transition-opacity duration-300" />
                    <input
                      type="text"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      placeholder="Enter LinkedIn username (e.g. johndoe)"
                      className="relative w-full bg-black/50 border border-white/10 rounded-xl px-6 py-4 text-lg text-white placeholder-gray-500 focus:ring-2 focus:ring-primary-cyan focus:border-transparent outline-none transition-all backdrop-blur-sm"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={loading}
                    className="px-8 py-4 bg-white text-black rounded-xl font-bold text-lg shadow-[0_0_20px_rgba(255,255,255,0.3)] hover:shadow-[0_0_30px_rgba(255,255,255,0.5)] transform hover:-translate-y-1 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                  >
                    {loading ? (
                      <span className="flex items-center gap-2">
                        <span className="w-5 h-5 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                        Processing
                      </span>
                    ) : (
                      'Generate ✨'
                    )}
                  </button>
                </form>
                {/* Inline Settings for Quick Access */}
                <div className="max-w-2xl mx-auto">
                  <details className="group glass-card rounded-xl border border-white/10 overflow-hidden">
                    <summary className="flex items-center justify-between p-4 cursor-pointer hover:bg-white/5 transition-colors">
                      <div className="flex items-center gap-2 text-sm font-medium text-gray-300">
                        <span className="text-accent-amber">⚙️</span>
                        <span>AI Configuration</span>
                        <span className="text-xs text-gray-500 ml-2">({provider})</span>
                      </div>
                      <svg className="w-5 h-5 text-gray-500 group-open:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </summary>
                    <div className="p-4 pt-0 grid gap-4 md:grid-cols-2 border-t border-white/5 mt-2">
                      <div className="mt-4">
                        <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Provider</label>
                        <select
                          value={provider}
                          onChange={(e) => setProvider(e.target.value)}
                          className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:ring-1 focus:ring-primary-cyan outline-none"
                        >
                          <option value="gemini">Google Gemini</option>
                          <option value="openai">OpenAI</option>
                          <option value="azure">Azure OpenAI</option>
                        </select>
                      </div>
                      <div className="mt-4">
                        <label className="block text-xs font-bold text-gray-500 uppercase mb-1">API Key</label>
                        <input
                          type="password"
                          value={apiKey}
                          onChange={(e) => setApiKey(e.target.value)}
                          placeholder="Update API Key"
                          className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:ring-1 focus:ring-primary-cyan outline-none"
                        />
                      </div>
                    </div>
                  </details>
                </div>
              </div>
              {loading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="max-w-xl mx-auto mb-12"
                >
                  <div className="glass-card p-6 rounded-2xl border border-white/10">
                    <div className="flex justify-between mb-2 text-sm font-medium text-gray-400">
                      <span>Progress</span>
                      <span>{Math.round(((progressStep + 1) / 4) * 100)}%</span>
                    </div>
                    <div className="h-2 bg-white/5 rounded-full overflow-hidden mb-4">
                      <motion.div
                        className="h-full bg-gradient-to-r from-primary-cyan to-accent-purple"
                        initial={{ width: '0%' }}
                        animate={{ width: `${((progressStep + 1) / 4) * 100}%` }}
                        transition={{ duration: 0.5 }}
                      />
                    </div>
                    <p className="text-center text-primary-cyan animate-pulse">
                      {['Connecting to LinkedIn...', 'Scraping Profile...', 'Analyzing Data...', 'Drafting Email...'][progressStep]}
                    </p>
                  </div>
                </motion.div>
              )}
              {result && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95, rotateX: 20 }}
                  animate={{ opacity: 1, scale: 1, rotateX: 0 }}
                  transition={{ type: "spring", duration: 0.8 }}
                  className="grid md:grid-cols-2 gap-6 perspective-1000"
                >
                  {/* Profile Card */}
                  <div className="glass-card p-6 rounded-2xl border border-white/10 hover:border-primary-cyan/30 transition-colors group">
                    <div className="flex items-start justify-between mb-4">
                      <h3 className="text-xl font-bold text-white group-hover:text-primary-cyan transition-colors">Profile Insights</h3>
                      <span className="px-3 py-1 rounded-full bg-white/5 text-xs font-medium text-gray-400 border border-white/5">
                        Source: LinkedIn
                      </span>
                    </div>
                    <div className="space-y-4">
                      <div>
                        <label className="text-xs uppercase tracking-wider text-gray-500 font-bold">Name</label>
                        <p className="text-lg font-medium">{result.profile.name || 'Unknown'}</p>
                      </div>
                      <div>
                        <label className="text-xs uppercase tracking-wider text-gray-500 font-bold">Role</label>
                        <p className="text-gray-300">{result.profile.title || 'Unknown'}</p>
                      </div>
                      <div>
                        <label className="text-xs uppercase tracking-wider text-gray-500 font-bold">Company</label>
                        <p className="text-gray-300">{result.profile.company || 'Unknown'}</p>
                      </div>
                    </div>
                  </div>
                  {/* Email Card */}
                  <div className="glass-card p-6 rounded-2xl border border-white/10 hover:border-accent-purple/30 transition-colors group relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-4 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={() => {
                          navigator.clipboard.writeText(`Subject: ${result.email.subject}\n\n${result.email.body}`)
                          toast.success('Copied to clipboard!')
                        }}
                        className="p-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors"
                        title="Copy to clipboard"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                        </svg>
                      </button>
                    </div>
                    <div className="mb-4">
                      <h3 className="text-xl font-bold text-white group-hover:text-accent-purple transition-colors mb-4">Generated Email</h3>
                      <div className="bg-black/30 rounded-lg p-3 mb-4 border border-white/5">
                        <span className="text-gray-500 text-sm mr-2">Subject:</span>
                        <span className="font-medium text-white">{result.email.subject}</span>
                      </div>
                    </div>
                    <div className="prose prose-invert max-w-none">
                      <div className="whitespace-pre-wrap text-gray-300 text-sm leading-relaxed font-light">
                        {result.email.body}
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
export default App
