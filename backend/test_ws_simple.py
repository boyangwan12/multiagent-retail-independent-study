"""Minimal WebSocket test - connects to /ws-test endpoint."""

import asyncio
import websockets

async def test():
    uri = "ws://localhost:8000/ws-test"
    print(f"Connecting to: {uri}")

    try:
        async with websockets.connect(uri) as ws:
            print("[SUCCESS] Connected!")

            message = await ws.recv()
            print(f"Received: {message}")

            print("[SUCCESS] Test passed!")
    except Exception as e:
        print(f"[FAILED] {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test())
