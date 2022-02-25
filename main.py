import httpcore

# read from config and convert to bytes
pool = [b"localhost:3000"]


class Pithy:
    def __init__(self):
        self.client = None

    # Starlette application line 117
    async def __call__(self, scope, receive, send):

        if scope["type"] == "http":
            # url = f'{scope["scheme"]}://{scope["headers"][0]},  headers=scope["headers"]'

            message = await receive()

            scope["headers"][0] = (b"host", b"www.google.com")

            print(scope["headers"])

            async with self.client.stream(
                method=scope["method"],
                # Replace
                url=f'{scope["scheme"]}://www.google.com',
                headers=scope["headers"],
                content=message.get("body", b""),
            ) as response:
                print(response.headers)

                await send(
                    {
                        "type": "http.response.start",
                        "status": response.status,
                        "headers": response.headers,
                    }
                )
                async for chunk in response.aiter_stream():
                    await send(
                        {"type": "http.response.body", "body": chunk, "more_body": True}
                    )

                await send(
                    {
                        "type": "http.response.body",
                        "body": b"",
                    }
                )

        elif scope["type"] == "lifespan":
            while True:
                message = await receive()
                if message["type"] == "lifespan.startup":
                    try:
                        # startup code goes here
                        self.client = httpcore.AsyncConnectionPool()
                        await send({"type": "lifespan.startup.complete"})
                    except Exception:
                        await send({"type": "lifespan.startup.failed"})
                elif message["type"] == "lifespan.shutdown":
                    try:
                        # shutdown code goes here
                        await self.client.aclose()
                        await send({"type": "lifespan.shutdown.complete"})
                    except Exception:
                        await send({"type": "lifespan.shutdown.failed"})
                    return


app = Pithy()
