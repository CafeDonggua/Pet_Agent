import asyncio
import websockets
import json
from websockets.exceptions import ConnectionClosedError

async def listen():
    uri = "ws://localhost:8000/ws"
    while True:
        try:
            async with websockets.connect(uri) as ws:
                print("已連線到 WebSocket，開始接收推播...")
                async for message in ws:
                    data = json.loads(message)
                    print("\n[WebSocket收到推播]")
                    print(json.dumps(data, ensure_ascii=False, indent=2))
        except ConnectionClosedError as e:
            print(f"連線中斷({e.code})，1秒後重連...")
            await asyncio.sleep(1)
        except Exception as e:
            print("WebSocket錯誤，2秒後重試：", e)
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(listen())