"use client"
import { TrendingUp, Users, MessageSquare, Eye } from "lucide-react"

const metrics = [
  { label: "Leads Found",    value: "0", icon: Users,         trend: null },
  { label: "Replies Sent",   value: "0", icon: MessageSquare, trend: null },
  { label: "Impressions",    value: "0", icon: Eye,           trend: null },
  { label: "Conversions",    value: "0", icon: TrendingUp,    trend: null },
]

export default function MetricsBar() {
  return (
    <div className="grid grid-cols-4 gap-4">
      {metrics.map(({ label, value, icon: Icon }) => (
        <div key={label} className="rounded-xl border border-zinc-800 bg-zinc-900 p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-zinc-500">{label}</span>
            <Icon size={14} className="text-zinc-600" />
          </div>
          <div className="text-2xl font-bold text-white">{value}</div>
          <div className="text-xs text-zinc-600 mt-1">Connect platforms to start tracking</div>
        </div>
      ))}
    </div>
  )
}
