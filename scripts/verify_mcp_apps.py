#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""Minimal verification for spatial-media MCP + MCP Apps compatibility."""

from __future__ import annotations

import argparse
import asyncio
import sys

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def verify(server_url: str, sample_file: str) -> int:
    failures: list[str] = []

    async with streamablehttp_client(server_url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            tool_names = [t.name for t in tools.tools]
            required_tools = {"inspect_spatial_metadata", "preview_metadata_settings"}
            missing = sorted(required_tools - set(tool_names))
            if missing:
                failures.append(f"必須ツール不足: {', '.join(missing)}")

            if "inspect_spatial_metadata" not in tool_names:
                failures.append("inspect_spatial_metadata が list_tools に存在しない")
            else:
                tool = next(t for t in tools.tools if t.name == "inspect_spatial_metadata")
                if not (tool.annotations and tool.annotations.readOnlyHint is True):
                    failures.append("readOnlyHint が true ではない")
                if not (tool.annotations and tool.annotations.destructiveHint is False):
                    failures.append("destructiveHint が false ではない")
                uri = (tool.meta or {}).get("ui", {}).get("resourceUri")
                if uri != "ui://widget/spatial-metadata-viewer.html":
                    failures.append("_meta.ui.resourceUri が期待値ではない")
            if "preview_metadata_settings" in tool_names:
                preview_tool = next(t for t in tools.tools if t.name == "preview_metadata_settings")
                if not (preview_tool.annotations and preview_tool.annotations.readOnlyHint is True):
                    failures.append("preview_metadata_settings の readOnlyHint が true ではない")

            call = await session.call_tool(
                "inspect_spatial_metadata",
                {"file_path": sample_file, "include_logs": False},
            )
            if call.isError:
                failures.append("tools/call が isError=True を返した")
            if (call.meta or {}).get("ui", {}).get("resourceUri") != "ui://widget/spatial-metadata-viewer.html":
                failures.append("tools/call 結果の _meta.ui.resourceUri が欠落/不一致")
            preview = await session.call_tool(
                "preview_metadata_settings",
                {"projection": "equirectangular", "stereo_mode": "left-right"},
            )
            if preview.isError:
                failures.append("preview_metadata_settings が isError=True を返した")
            if (preview.structuredContent or {}).get("note") != "Preview only. No file is modified.":
                failures.append("preview_metadata_settings の structuredContent が期待値と不一致")

            resources = await session.list_resources()
            resource_uris = [str(r.uri) for r in resources.resources]
            if "ui://widget/spatial-metadata-viewer.html" not in resource_uris:
                failures.append("ui リソースが list_resources に存在しない")

            read_resource = await session.read_resource("ui://widget/spatial-metadata-viewer.html")
            first = read_resource.contents[0]
            if first.mimeType != "text/html;profile=mcp-app":
                failures.append("UI リソースの MIME type が text/html;profile=mcp-app ではない")
            if "tools/call" not in first.text:
                failures.append("UI に tools/call 利用コードがない")
            if "ui/notifications/tool-result" not in first.text:
                failures.append("UI に ui/notifications/tool-result 処理がない")
            if "window.openai" in first.text:
                failures.append("UI が window.openai 依存コードを含んでいる")
            if "preview_metadata_settings" not in first.text:
                failures.append("UI に preview_metadata_settings の呼び出しUIがない")

    if failures:
        print("VERIFY: FAIL")
        for item in failures:
            print(f"- {item}")
        return 1

    print("VERIFY: PASS")
    print("- list_tools / annotations / _meta.ui.resourceUri (2 tools)")
    print("- tools/call result / _meta.ui.resourceUri")
    print("- preview_metadata_settings behavior")
    print("- read_resource MIME type")
    print("- UI standard bridge usage (ui/* + tools/call)")
    print("- no window.openai dependency")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-url", default="http://127.0.0.1:8000/mcp/")
    parser.add_argument("--sample-file", default="data/testsrc_320x240_h264.mp4")
    args = parser.parse_args()
    return asyncio.run(verify(args.server_url, args.sample_file))


if __name__ == "__main__":
    sys.exit(main())
