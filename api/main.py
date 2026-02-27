"""ZipJeweler FastAPI backend — serves the Next.js dashboard."""
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio

app = FastAPI(title="ZipJeweler API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://zipjeweler.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory state (replace with DB later) ──────────────────────────────────
crew_status: dict = {
    crew: {"status": "idle", "last_run": None, "runs": 0}
    for crew in ["intelligence", "listening", "engagement", "content", "posting", "analytics", "evolution"]
}

activity_log: list = []


# ── Models ───────────────────────────────────────────────────────────────────
class RunCrewRequest(BaseModel):
    dry_run: bool = True


# ── Routes ───────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


@app.get("/crews")
async def get_crews():
    return crew_status


@app.post("/crews/{crew_name}/run")
async def run_crew(crew_name: str, req: RunCrewRequest, background_tasks: BackgroundTasks):
    if crew_name not in crew_status:
        return {"error": f"Unknown crew: {crew_name}"}

    crew_status[crew_name]["status"] = "running"
    background_tasks.add_task(_run_crew_task, crew_name, req.dry_run)
    return {"message": f"Crew {crew_name} started", "dry_run": req.dry_run}


async def _run_crew_task(crew_name: str, dry_run: bool):
    from datetime import datetime
    try:
        # Simulate or actually run crew
        await asyncio.sleep(2)  # placeholder
        crew_status[crew_name]["status"] = "idle"
        crew_status[crew_name]["last_run"] = datetime.utcnow().isoformat()
        crew_status[crew_name]["runs"] += 1
        activity_log.insert(0, {
            "time": datetime.utcnow().isoformat(),
            "crew": crew_name,
            "message": f"[{'DRY RUN' if dry_run else 'LIVE'}] {crew_name.title()} crew completed",
        })
    except Exception as e:
        crew_status[crew_name]["status"] = "error"
        activity_log.insert(0, {"time": "now", "crew": crew_name, "message": f"Error: {e}"})


@app.get("/activity")
async def get_activity(limit: int = 50):
    return activity_log[:limit]


@app.get("/metrics")
async def get_metrics():
    return {
        "leads_found": 0,
        "replies_sent": 0,
        "impressions": 0,
        "conversions": 0,
        "platforms_connected": 0,
    }


@app.get("/platforms")
async def get_platforms():
    return {
        "instagram": {"connected": False, "username": None},
        "facebook":  {"connected": False, "page_id": None},
        "twitter":   {"connected": False, "username": None},
        "pinterest": {"connected": False, "username": None},
        "tiktok":    {"connected": False, "username": None},
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
