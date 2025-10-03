import os
import time
import asyncio


async def cleanup_old_files(folder: str = "output", max_age: int = 24*60*60, interval: int = 3600, stop_event: asyncio.Event = None):
    """
    Периодически удаляет файлы из папки `folder`, которые старше `max_age` секунд.
    interval — как часто проверять (в секундах).
    stop_event — asyncio.Event, чтобы корректно завершить цикл при остановке бота.
    """

    while True:
        now = time.time()
        removed = []

        if os.path.exists(folder):
            for fname in os.listdir(folder):
                path = os.path.join(folder, fname)
                if not os.path.isfile(path):
                    continue

                age = now - os.path.getmtime(path)
                if age > max_age:
                    try:
                        os.remove(path)
                        removed.append(fname)
                    except Exception as e:
                        print(f"Не удалось удалить {fname}: {e}")

        if removed:
            print(f"Удалены старые файлы: {removed}")

        # ждём до следующей проверки
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval)
            break  # если stop_event установлен — выходим
        except asyncio.TimeoutError:
            continue
