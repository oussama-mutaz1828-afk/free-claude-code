"""Local admin UI routes and APIs."""

import ipaddress
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from free_claude_code.agents.registry import get_agent_registry
from free_claude_code.commands.registry import get_command_registry
from free_claude_code.config.admin.manifest import FIELD_BY_KEY
from free_claude_code.config.admin.persistence import validate_updates
from free_claude_code.config.admin.values import load_config_response
from free_claude_code.rules.registry import get_rule_registry
from free_claude_code.skills.registry import get_skill_registry

from .dependencies import get_services
from .ports import ApiServices

router = APIRouter()

STATIC_DIR = Path(__file__).resolve().parent / "admin_static"
LOCAL_PROVIDER_PATHS = {
    "lmstudio": "/models",
    "llamacpp": "/models",
    "ollama": "/api/tags",
}


class AdminConfigPayload(BaseModel):
    """Partial config update submitted by the admin UI."""

    values: dict[str, Any] = Field(default_factory=dict)


def _is_loopback_host(host: str | None) -> bool:
    if host is None:
        return False
    normalized = host.strip().strip("[]").lower()
    if normalized == "localhost":
        return True
    try:
        return ipaddress.ip_address(normalized).is_loopback
    except ValueError:
        return False


def _origin_is_local(origin: str | None) -> bool:
    if not origin:
        return True
    parsed = urlsplit(origin)
    return _is_loopback_host(parsed.hostname)


def require_loopback_admin(request: Request) -> None:
    """Allow admin access only from the local machine."""

    client_host = request.client.host if request.client else None
    if not _is_loopback_host(client_host):
        raise HTTPException(status_code=403, detail="Admin UI is local-only")

    origin = request.headers.get("origin")
    if not _origin_is_local(origin):
        raise HTTPException(status_code=403, detail="Admin UI is local-only")


def _asset_response(filename: str) -> FileResponse:
    path = STATIC_DIR / filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Admin asset not found")
    return FileResponse(path)


@router.get("/admin", include_in_schema=False)
async def admin_page(request: Request):
    require_loopback_admin(request)
    return _asset_response("index.html")


@router.get("/admin/assets/{filename}", include_in_schema=False)
async def admin_asset(filename: str, request: Request):
    require_loopback_admin(request)
    if filename not in {"admin.css", "admin.js"}:
        raise HTTPException(status_code=404, detail="Admin asset not found")
    return _asset_response(filename)


@router.get("/admin/api/config")
async def get_admin_config(request: Request):
    require_loopback_admin(request)
    return load_config_response()


@router.post("/admin/api/config/validate")
async def validate_admin_config(payload: AdminConfigPayload, request: Request):
    require_loopback_admin(request)
    return validate_updates(_filtered_values(payload.values))


@router.post("/admin/api/config/apply")
async def apply_admin_config(
    payload: AdminConfigPayload,
    request: Request,
    background_tasks: BackgroundTasks,
    services: ApiServices = Depends(get_services),
):
    require_loopback_admin(request)
    result = await services.admin.apply_admin_config(_filtered_values(payload.values))
    restart = result.get("restart")
    if isinstance(restart, dict) and restart.get("automatic"):
        background_tasks.add_task(services.admin.request_restart)
    return result


@router.get("/admin/api/status")
async def admin_status(
    request: Request,
    services: ApiServices = Depends(get_services),
):
    require_loopback_admin(request)
    return services.admin.admin_status()


@router.get("/admin/api/providers/local-status")
async def local_provider_status(request: Request):
    require_loopback_admin(request)
    config = load_config_response()
    values = {field["key"]: field["value"] for field in config["fields"]}
    checks = []
    for provider_id, path in LOCAL_PROVIDER_PATHS.items():
        base_url = _local_provider_url(provider_id, values)
        checks.append(await _check_local_provider(provider_id, base_url, path))
    return {"providers": checks}


@router.post("/admin/api/providers/{provider_id}/test")
async def test_provider(
    provider_id: str,
    request: Request,
    services: ApiServices = Depends(get_services),
):
    require_loopback_admin(request)
    return await services.admin.test_provider(provider_id)


@router.get("/admin/api/agents")
async def list_agents(request: Request):
    require_loopback_admin(request)
    registry = get_agent_registry()
    agents = [
        {
            "agent_id": a.agent_id,
            "name": a.name,
            "description": a.description,
            "division": a.division,
            "emoji": a.emoji,
            "vibe": a.vibe,
            "tools": list(a.tools),
            "model": a.model,
        }
        for a in registry.agents
    ]
    divisions = [
        {
            "division_id": d.division_id,
            "label": d.label,
            "icon": d.icon,
            "color": d.color,
        }
        for d in registry.divisions
    ]
    return {"agents": agents, "divisions": divisions}


@router.get("/admin/api/agents/{agent_id}")
async def get_agent(agent_id: str, request: Request):
    require_loopback_admin(request)
    registry = get_agent_registry()
    agent = registry.get(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    return {
        "agent_id": agent.agent_id,
        "name": agent.name,
        "description": agent.description,
        "division": agent.division,
        "emoji": agent.emoji,
        "vibe": agent.vibe,
        "tools": list(agent.tools),
        "model": agent.model,
        "system_prompt": agent.system_prompt,
    }


@router.get("/admin/api/skills")
async def list_skills(request: Request):
    require_loopback_admin(request)
    registry = get_skill_registry()
    return {
        "skills": [
            {
                "skill_id": s.skill_id,
                "name": s.name,
                "description": s.description,
                "version": s.version,
                "has_references": s.has_references,
            }
            for s in registry.skills
        ],
        "count": len(registry),
    }


@router.get("/admin/api/skills/{skill_id}")
async def get_skill(skill_id: str, request: Request):
    require_loopback_admin(request)
    registry = get_skill_registry()
    skill = registry.get(skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_id}' not found")
    return {
        "skill_id": skill.skill_id,
        "name": skill.name,
        "description": skill.description,
        "version": skill.version,
        "author": skill.author,
        "has_references": skill.has_references,
        "reference_files": list(skill.reference_files),
        "instructions": skill.instructions,
    }


@router.get("/admin/api/commands")
async def list_commands(request: Request):
    require_loopback_admin(request)
    registry = get_command_registry()
    return {
        "commands": [
            {
                "command_id": c.command_id,
                "description": c.description,
                "argument_hint": c.argument_hint,
            }
            for c in registry.commands
        ],
        "count": len(registry),
    }


@router.get("/admin/api/commands/{command_id}")
async def get_command(command_id: str, request: Request):
    require_loopback_admin(request)
    registry = get_command_registry()
    command = registry.get(command_id)
    if command is None:
        raise HTTPException(status_code=404, detail=f"Command '{command_id}' not found")
    return {
        "command_id": command.command_id,
        "description": command.description,
        "argument_hint": command.argument_hint,
        "instructions": command.instructions,
    }


@router.get("/admin/api/rules")
async def list_rules(request: Request):
    require_loopback_admin(request)
    registry = get_rule_registry()
    return {
        "categories": registry.categories,
        "rules": [
            {
                "rule_id": r.rule_id,
                "category": r.category,
                "file_patterns": list(r.file_patterns),
            }
            for r in registry.rules
        ],
        "count": len(registry),
    }


@router.get("/admin/api/rules/{rule_id:path}")
async def get_rule(rule_id: str, request: Request):
    require_loopback_admin(request)
    registry = get_rule_registry()
    rule = registry.get(rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail=f"Rule '{rule_id}' not found")
    return {
        "rule_id": rule.rule_id,
        "category": rule.category,
        "file_patterns": list(rule.file_patterns),
        "instructions": rule.instructions,
    }


@router.post("/admin/api/models/refresh")
async def refresh_models(
    request: Request,
    services: ApiServices = Depends(get_services),
):
    require_loopback_admin(request)
    return await services.admin.refresh_models()


def _filtered_values(values: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in values.items() if key in FIELD_BY_KEY}


def _local_provider_url(provider_id: str, values: dict[str, str]) -> str:
    if provider_id == "lmstudio":
        return values.get("LM_STUDIO_BASE_URL", "")
    if provider_id == "llamacpp":
        return values.get("LLAMACPP_BASE_URL", "")
    if provider_id == "ollama":
        return values.get("OLLAMA_BASE_URL", "")
    return ""


async def _check_local_provider(
    provider_id: str, base_url: str, path: str
) -> dict[str, Any]:
    clean_url = base_url.strip().rstrip("/")
    if not clean_url:
        return {
            "provider_id": provider_id,
            "status": "missing_url",
            "label": "Missing URL",
            "base_url": base_url,
        }

    url = f"{clean_url}{path}"
    try:
        async with httpx.AsyncClient(timeout=1.5) as client:
            response = await client.get(url)
        ok = 200 <= response.status_code < 300
        return {
            "provider_id": provider_id,
            "status": "reachable" if ok else "offline",
            "label": "Reachable" if ok else "Offline",
            "base_url": base_url,
            "status_code": response.status_code,
        }
    except Exception as exc:
        return {
            "provider_id": provider_id,
            "status": "offline",
            "label": "Offline",
            "base_url": base_url,
            "error_type": type(exc).__name__,
        }
