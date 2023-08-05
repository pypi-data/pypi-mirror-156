import asyncio


async def sleep_return_1(sleep_time: float) -> int:
    await asyncio.sleep(sleep_time)
    return 1
