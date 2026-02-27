"use client"

const platforms = [
  { name: "Instagram", icon: "📸", color: "from-pink-500 to-purple-600" },
  { name: "Facebook",  icon: "👥", color: "from-blue-600 to-blue-700" },
  { name: "X / Twitter", icon: "🐦", color: "from-zinc-700 to-zinc-800" },
  { name: "Pinterest", icon: "📌", color: "from-red-600 to-red-700" },
  { name: "TikTok",    icon: "🎵", color: "from-zinc-900 to-zinc-800" },
]

export default function PlatformConnections() {
  return (
    <section className="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
      <h2 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider mb-4">
        Platform Connections
      </h2>
      <div className="space-y-3">
        {platforms.map(p => (
          <div key={p.name} className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${p.color} flex items-center justify-center text-sm`}>
                {p.icon}
              </div>
              <span className="text-sm text-zinc-300">{p.name}</span>
            </div>
            <button className="text-xs px-3 py-1 rounded-full border border-purple-500/50 text-purple-400 hover:bg-purple-500/10 transition-colors">
              Connect
            </button>
          </div>
        ))}
      </div>
      <p className="text-xs text-zinc-600 mt-4">Add API keys in Settings to connect platforms.</p>
    </section>
  )
}
