"""
ForgeOS ComputerUseAgent.

Replaces browser_use with Claude Computer Use API (claude-sonnet-4-6).
Playwright provides the browser substrate: screenshots, mouse, keyboard.
Claude provides the intelligence: decides what to click and type.

Architecture:
  screenshot → Claude claude-sonnet-4-6 (computer-use beta) → action → execute → repeat

No VNC or Docker required — Playwright runs headless in WSL2.
"""

from __future__ import annotations

import asyncio
import base64
import io
import os
from dataclasses import dataclass, field
from typing import Any

from .browser_agent import BrowserResult

_MAX_STEPS = 20
_DISPLAY_W = 1280
_DISPLAY_H = 720

# Computer use tool definition (Anthropic beta spec)
_COMPUTER_TOOL = {
    "type": "computer_20241022",
    "name": "computer",
    "display_width_px": _DISPLAY_W,
    "display_height_px": _DISPLAY_H,
    "display_number": 1,
}


class ComputerUseAgent:
    """
    Agentic browser automation via Claude Computer Use API + Playwright.

    Claude sees browser screenshots and responds with actions (click, type,
    scroll, key). Playwright executes those actions and feeds the next
    screenshot back to Claude. The loop continues until Claude signals
    task_complete or max_steps is reached.
    """

    def __init__(self, headless: bool = True) -> None:
        self.headless = headless
        self.model = os.environ.get("COMPUTER_USE_MODEL", "claude-sonnet-4-6")
        self._api_key = os.environ.get("ANTHROPIC_API_KEY", "")

    # ── Public API ────────────────────────────────────────────────────────────

    def run(self, task: str, start_url: str = "https://www.google.com") -> BrowserResult:
        """Synchronous wrapper around the async agentic loop."""
        try:
            return asyncio.get_event_loop().run_until_complete(
                self._loop(task, start_url)
            )
        except RuntimeError:
            import concurrent.futures as _cf
            with _cf.ThreadPoolExecutor(max_workers=1) as pool:
                return pool.submit(asyncio.run, self._loop(task, start_url)).result(timeout=300)

    # ── Agentic loop ──────────────────────────────────────────────────────────

    async def _loop(self, task: str, start_url: str) -> BrowserResult:
        if not self._api_key:
            return BrowserResult(
                success=False, url=start_url, action="computer_use",
                output="", errors="ANTHROPIC_API_KEY not set",
            )

        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return BrowserResult(
                success=False, url=start_url, action="computer_use",
                output="", errors="playwright not installed: pip install playwright",
            )

        import anthropic

        client = anthropic.Anthropic(api_key=self._api_key)
        messages: list[dict] = []
        final_url = start_url
        final_output = ""

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                viewport={"width": _DISPLAY_W, "height": _DISPLAY_H}
            )
            page = await context.new_page()

            if start_url:
                await page.goto(start_url, wait_until="domcontentloaded", timeout=30_000)

            for step in range(_MAX_STEPS):
                # Take screenshot
                png = await page.screenshot(type="png")
                b64 = base64.standard_b64encode(png).decode()

                # Build or extend the message list
                if not messages:
                    messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {"type": "base64", "media_type": "image/png", "data": b64},
                            },
                            {"type": "text", "text": task},
                        ],
                    })
                else:
                    # Append screenshot as new user turn after tool_result
                    messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {"type": "base64", "media_type": "image/png", "data": b64},
                            },
                        ],
                    })

                response = client.beta.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    tools=[_COMPUTER_TOOL],
                    betas=["computer-use-2024-10-22"],
                    messages=messages,
                )

                messages.append({"role": "assistant", "content": response.content})

                # Check for task completion
                if response.stop_reason == "end_turn":
                    for block in response.content:
                        if hasattr(block, "text"):
                            final_output = block.text
                    final_url = page.url
                    await browser.close()
                    return BrowserResult(
                        success=True,
                        url=final_url,
                        action="computer_use",
                        output=final_output or f"Task completed in {step + 1} steps",
                    )

                # Execute tool calls
                tool_results = []
                for block in response.content:
                    if block.type != "tool_use":
                        continue
                    action = block.input
                    action_type = action.get("action", "")
                    result_text = await self._execute_action(page, action_type, action)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_text,
                    })

                if tool_results:
                    messages.append({"role": "user", "content": tool_results})

            final_url = page.url
            await browser.close()

        return BrowserResult(
            success=False,
            url=final_url,
            action="computer_use",
            output=final_output,
            errors=f"Reached max_steps={_MAX_STEPS} without completing task",
        )

    # ── Action executor ───────────────────────────────────────────────────────

    async def _execute_action(
        self, page: Any, action_type: str, action: dict
    ) -> str:
        """Execute a single computer use action via Playwright. Returns status string."""
        try:
            if action_type == "screenshot":
                return "Screenshot captured"

            elif action_type in ("left_click", "right_click", "double_click", "middle_click"):
                coord = action.get("coordinate", [0, 0])
                x, y = coord[0], coord[1]
                btn = {
                    "left_click": "left",
                    "right_click": "right",
                    "double_click": "left",
                    "middle_click": "middle",
                }.get(action_type, "left")
                if action_type == "double_click":
                    await page.mouse.dblclick(x, y)
                else:
                    await page.mouse.click(x, y, button=btn)
                await page.wait_for_timeout(500)
                return f"Clicked at ({x}, {y})"

            elif action_type == "left_click_drag":
                start = action.get("start_coordinate", [0, 0])
                end = action.get("coordinate", [0, 0])
                await page.mouse.move(start[0], start[1])
                await page.mouse.down()
                await page.mouse.move(end[0], end[1])
                await page.mouse.up()
                return f"Dragged from {start} to {end}"

            elif action_type == "mouse_move":
                coord = action.get("coordinate", [0, 0])
                await page.mouse.move(coord[0], coord[1])
                return f"Moved mouse to {coord}"

            elif action_type == "type":
                text = action.get("text", "")
                await page.keyboard.type(text)
                await page.wait_for_timeout(300)
                return f"Typed: {text[:50]}"

            elif action_type == "key":
                key = action.get("text", "")
                # Translate common key names to Playwright equivalents
                key_map = {
                    "Return": "Enter", "ctrl+l": "Control+l",
                    "ctrl+a": "Control+a", "ctrl+c": "Control+c",
                    "ctrl+v": "Control+v", "Escape": "Escape",
                    "Tab": "Tab", "BackSpace": "Backspace",
                }
                pw_key = key_map.get(key, key)
                await page.keyboard.press(pw_key)
                await page.wait_for_timeout(200)
                return f"Pressed key: {key}"

            elif action_type == "scroll":
                coord = action.get("coordinate", [0, 0])
                direction = action.get("direction", "down")
                amount = action.get("amount", 3)
                delta = amount * 100 * (-1 if direction == "up" else 1)
                await page.mouse.wheel(0, delta)
                return f"Scrolled {direction} by {amount}"

            elif action_type == "cursor_position":
                return f"Cursor at unknown position"

            else:
                return f"Unknown action: {action_type}"

        except Exception as e:
            return f"Action failed: {e}"


__all__ = ["ComputerUseAgent"]
