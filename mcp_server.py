#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""Minimal MCP + MCP Apps server for spatial-media-py3.

Exposes read-only tools:
  - inspect_spatial_metadata
  - preview_metadata_settings

And one UI resource:
  - ui://widget/spatial-metadata-viewer.html
"""

from __future__ import annotations

import contextlib
import os
from pathlib import Path
from typing import Any

import uvicorn
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.server.lowlevel.helper_types import ReadResourceContents
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    Resource,
    TextContent,
    Tool,
    ToolAnnotations,
)
from starlette.applications import Starlette
from starlette.routing import Mount

from spatialmedia import metadata_utils

APP_NAME = "spatial-media-mcp"
APP_VERSION = "0.1.0"
INSPECT_TOOL_NAME = "inspect_spatial_metadata"
PREVIEW_TOOL_NAME = "preview_metadata_settings"
UI_RESOURCE_URI = "ui://widget/spatial-metadata-viewer.html"
UI_FILE_PATH = Path(__file__).resolve().parent / "mcp_ui" / "spatial_metadata_widget.html"

server = Server(
    APP_NAME,
    version=APP_VERSION,
    instructions=(
        "Read-only MCP server for inspecting spatial media metadata from local mp4/mov files."
    ),
)


def _inspect_input_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to a local .mp4 or .mov file to inspect.",
            },
            "include_logs": {
                "type": "boolean",
                "description": "Include parser console logs in structured output.",
                "default": True,
            },
        },
        "required": ["file_path"],
        "additionalProperties": False,
    }


def _preview_input_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "projection": {
                "type": "string",
                "enum": ["none", "equirectangular"],
                "default": "equirectangular",
            },
            "stereo_mode": {
                "type": "string",
                "enum": ["none", "top-bottom", "left-right"],
                "default": "none",
            },
            "crop": {
                "type": "string",
                "description": 'Optional crop in "w:h:f_w:f_h:x:y" format.',
            },
            "audio_channels": {
                "type": "integer",
                "minimum": 0,
                "description": "Optional input channel count to evaluate spatial audio support.",
            },
        },
        "additionalProperties": False,
    }


def _serialize_audio(parsed: Any) -> dict[str, Any] | None:
    if not parsed.audio:
        return None
    audio = parsed.audio
    return {
        "ambisonic_type": audio.ambisonic_type_name(),
        "head_locked_stereo": audio.head_locked_stereo,
        "ambisonic_order": audio.ambisonic_order,
        "ambisonic_channel_ordering": audio.ambisonic_channel_ordering_name(),
        "ambisonic_normalization": audio.ambisonic_normalization_name(),
        "num_channels": audio.num_channels,
        "channel_map": audio.channel_map,
        "metadata_string": audio.get_metadata_string(),
    }


def _build_result(file_path: str, include_logs: bool) -> CallToolResult:
    absolute_path = os.path.abspath(file_path)
    logs: list[str] = []

    def console(message: Any) -> None:
        logs.append(str(message))

    if not os.path.exists(absolute_path):
        error_text = f"File not found: {absolute_path}"
        return CallToolResult(
            isError=True,
            content=[TextContent(type="text", text=error_text)],
            structuredContent={"ok": False, "file_path": absolute_path, "error": error_text},
            _meta={"ui": {"resourceUri": UI_RESOURCE_URI}},
        )

    parsed = metadata_utils.parse_metadata(absolute_path, console)
    if parsed is None:
        error_text = "Failed to parse metadata. Check file type and parser logs."
        payload = {
            "ok": False,
            "file_path": absolute_path,
            "error": error_text,
            "logs": logs if include_logs else [],
        }
        return CallToolResult(
            isError=True,
            content=[TextContent(type="text", text=error_text)],
            structuredContent=payload,
            _meta={"ui": {"resourceUri": UI_RESOURCE_URI}, "logs": logs},
        )

    video_tracks = parsed.video or {}
    payload = {
        "ok": True,
        "file_path": absolute_path,
        "video_track_count": len(video_tracks),
        "video_tracks": video_tracks,
        "audio": _serialize_audio(parsed),
        "num_audio_channels": parsed.num_audio_channels,
        "logs": logs if include_logs else [],
    }
    summary = (
        f"Parsed {os.path.basename(absolute_path)}: "
        f"{len(video_tracks)} video track(s), "
        f"{parsed.num_audio_channels} audio channel(s)."
    )

    return CallToolResult(
        content=[TextContent(type="text", text=summary)],
        structuredContent=payload,
        _meta={
            "ui": {"resourceUri": UI_RESOURCE_URI},
            "openai/outputTemplate": UI_RESOURCE_URI,
            "logs": logs,
        },
    )


def _build_preview_result(arguments: dict[str, Any]) -> CallToolResult:
    projection = arguments.get("projection", "equirectangular")
    stereo_mode = arguments.get("stereo_mode", "none")
    crop = arguments.get("crop")
    audio_channels = arguments.get("audio_channels")

    if projection not in {"none", "equirectangular"}:
        return CallToolResult(
            isError=True,
            content=[TextContent(type="text", text="`projection` is invalid.")],
            structuredContent={"ok": False, "error": "`projection` is invalid."},
            _meta={"ui": {"resourceUri": UI_RESOURCE_URI}},
        )
    if stereo_mode not in {"none", "top-bottom", "left-right"}:
        return CallToolResult(
            isError=True,
            content=[TextContent(type="text", text="`stereo_mode` is invalid.")],
            structuredContent={"ok": False, "error": "`stereo_mode` is invalid."},
            _meta={"ui": {"resourceUri": UI_RESOURCE_URI}},
        )
    if audio_channels is not None and not isinstance(audio_channels, int):
        return CallToolResult(
            isError=True,
            content=[TextContent(type="text", text="`audio_channels` must be an integer.")],
            structuredContent={"ok": False, "error": "`audio_channels` must be an integer."},
            _meta={"ui": {"resourceUri": UI_RESOURCE_URI}},
        )

    v1_xml = metadata_utils.generate_spherical_xml(projection, stereo_mode, crop)
    if v1_xml is False:
        return CallToolResult(
            isError=True,
            content=[TextContent(type="text", text="Invalid crop format or crop values.")],
            structuredContent={"ok": False, "error": "Invalid crop format or crop values."},
            _meta={"ui": {"resourceUri": UI_RESOURCE_URI}},
        )

    audio_preview = None
    if isinstance(audio_channels, int):
        desc = metadata_utils.get_spatial_audio_description(audio_channels)
        audio_preview = {
            "num_channels": audio_channels,
            "is_supported": desc.is_supported,
            "order": desc.order,
            "head_locked_stereo": desc.has_head_locked_stereo,
        }
        if desc.is_supported:
            audio_preview["metadata_template"] = dict(
                metadata_utils.get_spatial_audio_metadata(desc.order, desc.has_head_locked_stereo)
            )

    payload = {
        "ok": True,
        "projection": projection,
        "stereo_mode": stereo_mode,
        "crop": crop,
        "v1_xml": v1_xml,
        "v2_atoms": {
            "projection": None if projection == "none" else projection,
            "stereo_mode": None if stereo_mode == "none" else stereo_mode,
            "sv3d": projection == "equirectangular",
            "st3d": stereo_mode != "none",
        },
        "audio_preview": audio_preview,
        "note": "Preview only. No file is modified.",
    }

    summary = (
        f"Preview ready: projection={projection}, stereo_mode={stereo_mode}, "
        f"crop={'set' if crop else 'none'}."
    )
    return CallToolResult(
        content=[TextContent(type="text", text=summary)],
        structuredContent=payload,
        _meta={"ui": {"resourceUri": UI_RESOURCE_URI}, "openai/outputTemplate": UI_RESOURCE_URI},
    )


@server.list_tools()
async def list_tools() -> ListToolsResult:
    inspect_tool = Tool(
        name=INSPECT_TOOL_NAME,
        title="Inspect Spatial Metadata",
        description=(
            "Read metadata from a local mp4/mov file and return spherical/spatial audio summary."
        ),
        inputSchema=_inspect_input_schema(),
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
        _meta={
            "ui": {"resourceUri": UI_RESOURCE_URI, "visibility": ["model", "app"]},
            "openai/outputTemplate": UI_RESOURCE_URI,
        },
    )
    preview_tool = Tool(
        name=PREVIEW_TOOL_NAME,
        title="Preview Metadata Settings",
        description="Preview v1/v2 metadata settings and spatial audio compatibility without modifying files.",
        inputSchema=_preview_input_schema(),
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
        _meta={
            "ui": {"resourceUri": UI_RESOURCE_URI, "visibility": ["model", "app"]},
            "openai/outputTemplate": UI_RESOURCE_URI,
        },
    )
    return ListToolsResult(tools=[inspect_tool, preview_tool])


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> CallToolResult:
    if name == INSPECT_TOOL_NAME:
        file_path = arguments.get("file_path")
        include_logs = bool(arguments.get("include_logs", True))
        if not isinstance(file_path, str) or not file_path.strip():
            return CallToolResult(
                isError=True,
                content=[TextContent(type="text", text="`file_path` must be a non-empty string.")],
                structuredContent={
                    "ok": False,
                    "error": "`file_path` must be a non-empty string.",
                },
                _meta={"ui": {"resourceUri": UI_RESOURCE_URI}},
            )
        return _build_result(file_path=file_path, include_logs=include_logs)

    if name == PREVIEW_TOOL_NAME:
        return _build_preview_result(arguments)

    if name not in {INSPECT_TOOL_NAME, PREVIEW_TOOL_NAME}:
        return CallToolResult(
            isError=True,
            content=[TextContent(type="text", text=f"Unknown tool: {name}")],
            structuredContent={"ok": False, "error": f"Unknown tool: {name}"},
        )


@server.list_resources()
async def list_resources() -> list[Resource]:
    return [
        Resource(
            name="Spatial Metadata Viewer",
            title="Spatial Metadata Viewer",
            uri=UI_RESOURCE_URI,
            description="Interactive MCP Apps UI for metadata inspection.",
            mimeType="text/html;profile=mcp-app",
        )
    ]


@server.read_resource()
async def read_resource(uri: Any) -> list[ReadResourceContents]:
    uri_str = str(uri)
    if uri_str != UI_RESOURCE_URI:
        raise ValueError(f"Unknown resource uri: {uri_str}")

    html = UI_FILE_PATH.read_text(encoding="utf-8")
    return [
        ReadResourceContents(
            content=html,
            mime_type="text/html;profile=mcp-app",
            meta={
                "ui": {
                    "prefersBorder": True,
                    "csp": {"connectDomains": [], "resourceDomains": []},
                },
                "openai/widgetDescription": (
                    "Shows metadata results and allows calling inspect_spatial_metadata from the UI."
                ),
            },
        )
    ]


def create_app() -> Starlette:
    session_manager = StreamableHTTPSessionManager(app=server, stateless=True, json_response=True)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette):
        async with session_manager.run():
            yield

    return Starlette(
        routes=[Mount("/mcp", app=session_manager.handle_request)],
        lifespan=lifespan,
    )


app = create_app()


if __name__ == "__main__":
    uvicorn.run("mcp_server:app", host="127.0.0.1", port=8000, reload=False)
