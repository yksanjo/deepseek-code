"""DeepSeek Code Server - REST API Server."""

import os
from typing import Any

import typer
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="DeepSeek Code Server",
    description="AI Coding Assistant REST API Server",
    version="0.1.0",
)

# Initialize CLI
cli = typer.Typer(help="DeepSeek Code Server CLI")


class SessionCreate(BaseModel):
    project_id: str
    model: str = "deepseek-chat"
    trust_mode: bool = False
    max_turns: int = 50


class MessageCreate(BaseModel):
    content: str


class HealthResponse(BaseModel):
    status: str
    version: str


@app.get("/health", response_model=HealthResponse)
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


@app.post("/api/sessions")
async def create_session(session: SessionCreate) -> dict[str, Any]:
    """Create a new coding session."""
    import uuid
    session_id = f"sess_{uuid.uuid4().hex[:12]}"
    return {
        "id": session_id,
        "project_id": session.project_id,
        "model": session.model,
        "trust_mode": session.trust_mode,
        "max_turns": session.max_turns,
        "created_at": "2025-01-01T00:00:00Z",
        "status": "active",
    }


@app.get("/api/sessions")
async def list_sessions() -> dict[str, list]:
    """List all sessions."""
    return {"sessions": []}


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str) -> dict[str, Any]:
    """Get session by ID."""
    return {
        "id": session_id,
        "project_id": "default",
        "messages": [],
        "status": "active",
    }


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str) -> dict[str, str]:
    """Delete a session."""
    return {"status": "deleted", "session_id": session_id}


@app.post("/api/sessions/{session_id}/messages")
async def send_message(session_id: str, message: MessageCreate) -> dict[str, Any]:
    """Send a message to a session."""
    return {
        "id": f"msg_{uuid.uuid4().hex[:12]}",
        "session_id": session_id,
        "content": message.content,
        "response": f"Echo: {message.content}",
        "tool_calls": [],
    }


@app.get("/api/projects")
async def list_projects() -> dict[str, list]:
    """List all projects."""
    return {"projects": []}


@app.post("/api/projects")
async def create_project(project_id: str) -> dict[str, str]:
    """Create a new project."""
    return {"id": project_id, "status": "created"}


# Need uuid for the message endpoint
import uuid


@cli.command()
def main(
    host: str = typer.Option("0.0.0.0", help="Server host"),
    port: int = typer.Option(8000, help="Server port"),
    reload: bool = typer.Option(False, help="Enable auto-reload"),
) -> None:
    """Start the DeepSeek Code Server."""
    import uvicorn
    
    typer.echo(f"Starting DeepSeek Code Server on {host}:{port}")
    typer.echo("API Documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        "deepseek_code_server.server:app",
        host=host,
        port=port,
        reload=reload,
    )


if __name__ == "__main__":
    cli()
