"use client"
import { LayoutDashboard, Bot, BarChart3, Settings, Zap } from "lucide-react"

const nav = [
  { id: "overview",  icon: LayoutDashboard, label: "Overview" },
  { id: "agents",    icon: Bot,             label: "Agents" },
  { id: "analytics", icon: BarChart3,       label: "Analytics" },
  { id: "settings",  icon: Settings,        label: "Settings" },
]

export default function Sidebar({ activeTab, onTabChange }: { activeTab: string; onTabChange: (tab: string) => void }) {
  return (
    <aside className="w-56 bg-zinc-900 border-r border-zinc-800 flex flex-col py-6 px-3 shrink-0">
      {/* Logo */}
      <div className="flex items-center gap-2 px-3 mb-8">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-600 to-yellow-500 flex items-center justify-center">
          <Zap size={16} className="text-white" />
        </div>
        <div>
          <div className="text-sm font-bold text-white">ZipJeweler</div>
          <div className="text-xs text-zinc-500">Command Center</div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-1">
        {nav.map(({ id, icon: Icon, label }) => (
          <button
            key={id}
            onClick={() => onTabChange(id)}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
              activeTab === id
                ? "bg-purple-600/20 text-purple-400 font-medium"
                : "text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800"
            }`}
          >
            <Icon size={16} />
            {label}
          </button>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-3 pt-4 border-t border-zinc-800">
        <div className="text-xs text-zinc-600">zipjeweler.com</div>
        <div className="text-xs text-zinc-600">v0.1.0</div>
      </div>
    </aside>
  )
}
