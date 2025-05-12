import asyncio
import uvloop
import datetime

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

LISTEN_PORT = 80
FORWARD_HOST = '127.0.0.1'
FORWARD_PORT = 22

WELCOME_RESPONSE = (
    "HTTP/1.1 101 <b><i><font color=\"green\">WELCOME TO FN NETWORK</font></i></b>\r\n"
    "Date: {date}\r\n"
    "Connection: upgrade\r\n"
    "Upgrade: websocket\r\n"
    "Server: cloudflare\r\n"
    "CF-RAY: 1234567890abcdef-BOM\r\n"
    "\r\n"
)

async def handle_client(reader, writer):
    try:
        data = await reader.read(1024)
        if b"Host:" not in data:
            writer.close()
            await writer.wait_closed()
            return

        # Send welcome header
        date_str = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        writer.write(WELCOME_RESPONSE.format(date=date_str).encode())
        await writer.drain()

        # Connect to SSH backend
        remote_reader, remote_writer = await asyncio.open_connection(FORWARD_HOST, FORWARD_PORT)

        # Bi-directional tunnel
        await asyncio.gather(
            pipe(reader, remote_writer),
            pipe(remote_reader, writer)
        )

    except Exception:
        pass
    finally:
        writer.close()
        await writer.wait_closed()

async def pipe(reader, writer):
    try:
        while True:
            data = await reader.read(4096)
            if not data:
                break
            writer.write(data)
            await writer.drain()
    except:
        pass
    finally:
        writer.close()
        await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle_client, '0.0.0.0', LISTEN_PORT)
    print(f"[+] Ultra-Fast SNI Proxy Listening on port {LISTEN_PORT}")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
