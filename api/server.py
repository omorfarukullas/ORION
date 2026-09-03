"""
api/server.py
=============
FastAPI & WebSocket Server for ORION Web Dashboard and Remote Control.

Runs concurrently with ORION desktop app or standalone in headless mode.
Exposes RESTful endpoints and real-time WebSocket state streaming.
"""

from __future__ import annotations
import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import psutil

from config.settings import Settings
from speech.personas import persona_manager
from plugins.registry import plugin_registry
from api.schemas import (
    CommandRequest,
    CommandResponse,
    StatusResponse,
    PersonaChangeRequest,
    PluginActionRequest,
)
from utils.logger import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """Manages active WebSocket client connections for real-time telemetry."""

    def __init__(self) -> None:
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.discard(websocket)

    async def broadcast(self, message: Dict[str, Any]) -> None:
        dead = []
        payload = json.dumps(message)
        for connection in self.active_connections:
            try:
                await connection.send_text(payload)
            except Exception:
                dead.append(connection)
        for d in dead:
            self.active_connections.discard(d)


ws_manager = ConnectionManager()
current_status = {"status": "IDLE"}


def create_app() -> FastAPI:
    """Build and configure the FastAPI application instance."""
    app = FastAPI(
        title="ORION Web Dashboard & Remote API",
        description="Local-first AI Voice Assistant Web Interface & REST API",
        version="2.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── REST API Endpoints ───────────────────────────────────────────────

    @app.get("/api/status", response_model=StatusResponse)
    def get_status():
        battery = psutil.sensors_battery()
        return StatusResponse(
            name=Settings.NAME,
            version=Settings.VERSION,
            status=current_status.get("status", "IDLE"),
            persona=persona_manager.active_persona.name,
            cpu_percent=psutil.cpu_percent(interval=None),
            ram_percent=psutil.virtual_memory().percent,
            battery_percent=int(battery.percent) if battery else None,
            battery_charging=battery.power_plugged if battery else None,
        )

    @app.post("/api/command", response_model=CommandResponse)
    async def post_command(req: CommandRequest):
        raw_text = req.command.strip()
        if not raw_text:
            raise HTTPException(status_code=400, detail="Empty command.")

        # Broadcast PROCESSING status
        await ws_manager.broadcast({"type": "status", "status": "PROCESSING", "command": raw_text})

        try:
            from nlp.command_parser import CommandParser
            from nlp.command_dispatcher import dispatch
            from planner.context import ConversationContext
            from database.database import Database

            parser = CommandParser()
            context = ConversationContext()
            db = Database(Settings.DB_PATH)

            parsed_cmd = parser.parse(raw_text)
            resolved_cmd = context.resolve(parsed_cmd)
            outcome = dispatch(resolved_cmd, db=db)
            context.update(resolved_cmd)

            # Broadcast command outcome
            response_data = CommandResponse(
                raw_text=raw_text,
                intent=resolved_cmd.intent,
                confidence=resolved_cmd.confidence,
                entities=resolved_cmd.entities,
                outcome=outcome,
                success=True,
            )

            await ws_manager.broadcast({
                "type": "command_result",
                "data": response_data.model_dump(),
            })
            await ws_manager.broadcast({"type": "status", "status": "IDLE"})

            return response_data
        except Exception as e:
            logger.error(f"Error processing web command '{raw_text}': {e}")
            await ws_manager.broadcast({"type": "status", "status": "ERROR"})
            return CommandResponse(
                raw_text=raw_text,
                intent="ERROR",
                confidence=0.0,
                outcome=f"Error executing command: {e}",
                success=False,
            )

    @app.get("/api/metrics")
    def get_metrics():
        battery = psutil.sensors_battery()
        mem = psutil.virtual_memory()
        return {
            "cpu_percent": psutil.cpu_percent(interval=None),
            "ram_percent": mem.percent,
            "ram_used_gb": round(mem.used / (1024 ** 3), 2),
            "ram_total_gb": round(mem.total / (1024 ** 3), 2),
            "battery_percent": int(battery.percent) if battery else None,
            "battery_charging": battery.power_plugged if battery else None,
        }

    @app.get("/api/history")
    def get_history(limit: int = 25):
        from database.database import Database
        try:
            db = Database(Settings.DB_PATH)
            history = db.get_recent_commands(limit=limit)
            return {"history": history}
        except Exception as e:
            return {"history": [], "error": str(e)}

    @app.get("/api/personas")
    def get_personas():
        return {
            "active": persona_manager.active_persona.id,
            "personas": persona_manager.list_personas(),
        }

    @app.post("/api/personas/select")
    async def select_persona(req: PersonaChangeRequest):
        success = persona_manager.set_persona(req.persona_id)
        if not success:
            raise HTTPException(status_code=404, detail="Persona not found.")
        
        Settings.VOICE_PERSONA = persona_manager.active_persona.id
        Settings.save_user_settings()

        await ws_manager.broadcast({
            "type": "persona_changed",
            "persona": persona_manager.active_persona.name,
            "persona_id": persona_manager.active_persona.id,
        })
        return {"status": "success", "active": persona_manager.active_persona.name}

    @app.get("/api/plugins")
    def list_plugins():
        installed = plugin_registry.list_installed_plugins()
        cloud = plugin_registry.fetch_cloud_catalog()
        return {
            "installed": installed,
            "catalog": cloud,
        }

    @app.post("/api/plugins/install")
    async def install_plugin(req: PluginActionRequest):
        catalog = plugin_registry.fetch_cloud_catalog()
        match = next((p for p in catalog if p.get("id") == req.plugin_id), None)
        success = plugin_registry.install_plugin(req.plugin_id, manifest=match)
        if success:
            await ws_manager.broadcast({"type": "plugin_installed", "plugin_id": req.plugin_id})
            return {"status": "success", "installed": req.plugin_id}
        raise HTTPException(status_code=500, detail="Failed to install plugin.")

    @app.post("/api/plugins/uninstall")
    async def uninstall_plugin(req: PluginActionRequest):
        success = plugin_registry.uninstall_plugin(req.plugin_id)
        if success:
            await ws_manager.broadcast({"type": "plugin_uninstalled", "plugin_id": req.plugin_id})
            return {"status": "success", "uninstalled": req.plugin_id}
        raise HTTPException(status_code=404, detail="Plugin not found or failed to uninstall.")

    # ── WebSocket Stream ─────────────────────────────────────────────────

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await ws_manager.connect(websocket)
        # Send initial status & telemetry upon connect
        await websocket.send_text(json.dumps({
            "type": "init",
            "status": current_status.get("status", "IDLE"),
            "persona": persona_manager.active_persona.name,
        }))
        try:
            while True:
                data = await websocket.receive_text()
                try:
                    payload = json.loads(data)
                    action = payload.get("action")
                    if action == "ping":
                        await websocket.send_text(json.dumps({"type": "pong"}))
                except Exception:
                    pass
        except WebSocketDisconnect:
            ws_manager.disconnect(websocket)

    # ── Static Web Dashboard Mount ───────────────────────────────────────
    web_dir = Settings.ROOT_DIR / "web"
    if web_dir.exists():
        app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")

        @app.get("/")
        async def serve_index():
            index_file = web_dir / "index.html"
            if index_file.exists():
                return FileResponse(str(index_file))
            return JSONResponse({"message": "ORION Web Server running. Web files not found."})

    return app


def run_api_server(host: str = "127.0.0.1", port: int = 8080) -> None:
    """Launch the Uvicorn web server (blocking or daemon thread)."""
    import uvicorn
    app = create_app()
    logger.info(f"Starting ORION Web Dashboard at http://{host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="warning")


if __name__ == "__main__":
    run_api_server(Settings.WEB_HOST, Settings.WEB_PORT)
