import asyncio

from wordpy.app import Master

async def main():
    my_app = Master()
    await my_app.run()

if __name__ == '__main__':
    print("[info]", "[main]", "application started.")
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except BaseException as e:
        print("[debug]", "[main]", e)
        print("[info]", "[main]", "application shut down.")
