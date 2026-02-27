"use client"
import { useState } from "react"
import { Play, Pause, RefreshCw } from "lucide-react"

const crews = [
  { name: "Intelligence", icon: "🔍", agents: 4,  color: "blue",   status: "idle", desc: "Daily brief, competitor tracking, opportunity scoring" },
  { name: "Listening",    icon: "👂", agents: 7,  color: "green",  status: "idle", desc: "Instagram, Facebook, X, Pinterest, TikTok" },
  { name: "Engagement",   icon: "💬", agents: 7,  color: "yellow", status: "idle", desc: "Craft and post helpful replies on discovered leads" },
  { name: "Content",      icon: "✍️", agents: 3,  color: "purple", status: "idle", desc: "Generate text + image content per platform" },
  { name: "Posting",      icon: "📤", agents: 6,  color: "pink",   status: "idle", desc: "Schedule and publish approved content" },
  { name: "Analytics",    icon: "📊", agents: 3,  color: "orange", status: "idle", desc: "Track engagement, sentiment, learnings" },
  { name: "Evolution",    icon: "🧬", agents: 7,  color: "teal",   status: "idle", desc: "A/B testing, strategy evolution, lead nurturing" },
]

const colorMap: Record<string, string> = {
  blue:   "border-blue-500/30 bg-blue-500/5",
  green:  "border-green-500/30 bg-green-500/5",
  yellow: "border-yellow-500/30 bg-yellow-500/5",
  purple: "border-purple-500/30 bg-purple-500/5",
  pink:   "border-pink-500/30 bg-pink-500/5",
  orange: "border-orange-500/30 bg-orange-500/5",
  teal:   "border-teal-500/30 bg-teal-500/5",
}

export default function CrewGrid() {
  const [running, setRunning] = useState<string | null>(null)

  const handleRun = async (crew: string) => {
    setRunning(crew)
    await new Promise(r => setTimeout(r, 2000))
    setRunning(null)
  }

  return (
    <section>
      <h2 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider mb-3">Crews</h2>
      <div className="grid grid-cols-4 gap-3">
        {crews.map(crew => (
          <div
            key={crew.name}
            className={`rounded-xl border p-4 ${colorMap[crew.color]} transition-all`}
          >
            <div className="flex items-start justify-between mb-2">
              <div className="text-2xl">{crew.icon}</div>
              <button
                onClick={() => handleRun(crew.name)}
                className="p-1 rounded-md hover:bg-zinc-700/50 text-zinc-400 hover:text-white transition-colors"
                title="Run crew"
              >
                {running === crew.name
                  ? <RefreshCw size={14} className="animate-spin" />
                  : <Play size={14} />
                }
              </button>
            </div>
            <div className="font-semibold text-sm text-white">{crew.name}</div>
            <div className="text-xs text-zinc-500 mt-0.5 mb-3">{crew.desc}</div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-zinc-600">{crew.agents} agents</span>
              <span className={`text-xs px-1.5 py-0.5 rounded-full ${
                running === crew.name
                  ? "bg-green-500/20 text-green-400"
                  : "bg-zinc-700 text-zinc-400"
              }`}>
                {running === crew.name ? "running" : "idle"}
              </span>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
