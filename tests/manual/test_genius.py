import asyncio

from app.clients.genius_client import GeniusClient


async def main() -> None:
    client = GeniusClient()

    try:
        response = await client.search("Yesterday The Beatles")

        print(response.status_code)
        print(response.json())

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())