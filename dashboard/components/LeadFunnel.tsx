"use client"

const stages = [
  { name: "Discovery",     count: 0, color: "bg-zinc-600" },
  { name: "Awareness",     count: 0, color: "bg-blue-600" },
  { name: "Interest",      count: 0, color: "bg-purple-600" },
  { name: "Consideration", count: 0, color: "bg-yellow-600" },
  { name: "Decision",      count: 0, color: "bg-orange-600" },
  { name: "Conversion",    count: 0, color: "bg-green-600" },
]

export default function LeadFunnel() {
  return (
    <section className="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
      <h2 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider mb-4">
        Lead Funnel
      </h2>
      <div className="space-y-2">
        {stages.map((stage, i) => {
          const width = `${100 - i * 12}%`
          return (
            <div key={stage.name} className="flex items-center gap-3">
              <div className="w-24 text-xs text-zinc-500 text-right shrink-0">{stage.name}</div>
              <div className="flex-1 bg-zinc-800 rounded-full h-6 overflow-hidden">
                <div
                  className={`h-full ${stage.color} opacity-30 rounded-full transition-all`}
                  style={{ width }}
                />
              </div>
              <div className="w-6 text-xs text-zinc-500 text-right">{stage.count}</div>
            </div>
          )
        })}
      </div>
      <p className="text-xs text-zinc-600 mt-4">Funnel fills as agents find and nurture leads.</p>
    </section>
  )
}
