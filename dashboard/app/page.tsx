"use client"
import { useState } from "react"
import Sidebar from "@/components/Sidebar"
import CrewGrid from "@/components/CrewGrid"
import PlatformConnections from "@/components/PlatformConnections"
import LeadFunnel from "@/components/LeadFunnel"
import ActivityFeed from "@/components/ActivityFeed"
import MetricsBar from "@/components/MetricsBar"

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("overview")

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
      <main className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold gradient-text">ZipJeweler Command Center</h1>
            <p className="text-zinc-500 text-sm mt-1">36 agents · 7 crews · zipjeweler.com</p>
          </div>
          <div className="flex gap-2">
            <span className="px-3 py-1 rounded-full bg-yellow-500/10 text-yellow-400 text-xs font-medium border border-yellow-500/20">
              🟡 Dry Run Mode
            </span>
            <span className="px-3 py-1 rounded-full bg-purple-500/10 text-purple-400 text-xs font-medium border border-purple-500/20">
              Supervised
            </span>
          </div>
        </div>

        {activeTab === "overview" && (
          <>
            <MetricsBar />
            <CrewGrid />
            <div className="grid grid-cols-2 gap-6">
              <PlatformConnections />
              <LeadFunnel />
            </div>
            <ActivityFeed />
          </>
        )}

        {activeTab === "agents" && (
          <div className="text-zinc-400">Agent detail view — coming next</div>
        )}

        {activeTab === "analytics" && (
          <div className="text-zinc-400">Analytics charts — coming next</div>
        )}

        {activeTab === "settings" && (
          <div className="text-zinc-400">Settings panel — coming next</div>
        )}
      </main>
    </div>
  )
}
