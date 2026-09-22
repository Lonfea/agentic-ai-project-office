from fastapi import FastAPI, HTTPException

from .engine import demo_office

app = FastAPI(title="Agentic AI Project Office", version="1.0.0")
office = demo_office()


@app.get("/health")
def health():
    return {"status": "ok", "audit_chain_valid": office.verify_audit_chain()}


@app.get("/initiatives")
def initiatives():
    return office.records()


@app.post("/initiatives/{initiative_id}/analyze")
def analyze(initiative_id: str):
    try:
        return office.analyze(initiative_id)
    except KeyError as exc:
        raise HTTPException(404, "initiative not found") from exc


@app.post("/initiatives/{initiative_id}/transition")
def transition(initiative_id: str, target: str, actor: str, role: str, reason: str = ""):
    try:
        return office.transition(initiative_id, target, actor, role, reason)
    except KeyError as exc:
        raise HTTPException(404, "initiative not found") from exc
    except (ValueError, PermissionError) as exc:
        raise HTTPException(409, str(exc)) from exc


@app.get("/report")
def report():
    return office.executive_report()

