"use client"

export default function ActivityFeed() {
  return (
    <section className="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
      <h2 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider mb-4">
        Activity Feed
      </h2>
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="text-4xl mb-3">🤖</div>
        <p className="text-zinc-500 text-sm">No activity yet.</p>
        <p className="text-zinc-600 text-xs mt-1">
          Connect your platforms and run a crew to see activity here.
        </p>
      </div>
    </section>
  )
}
