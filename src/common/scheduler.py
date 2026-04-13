import asyncio
import time
import logging
from src.common.queue_manager import request_queue
from src.common.model_manager import model_manager
import json
import csv

CSV_FILE = "metrics.csv"
with open(CSV_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "latency", "batch_size", "group_size"])
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


USE_GROUPING = True
MAX_BATCH_SIZE = 8


def get_prefix(text: str, k: int = 20) -> str:
    return text[:k].strip().lower()


def group_by_prefix(requests):
    groups = {}
    for req in requests:
        key = get_prefix(req.message)
        if key not in groups:
            groups[key] = []
        groups[key].append(req)

    return list(groups.values())


async def scheduler_loop():
    llm, sampling_params = model_manager.get()

    while True:
        await asyncio.sleep(0.05)
        while True:
            batch = request_queue.pop_batch(max_batch_size=MAX_BATCH_SIZE)
            if not batch:
                break
            try:
                batch_size = len(batch)
                if USE_GROUPING:
                    groups = group_by_prefix(batch)
                    logging.info(f"[Scheduler] Groups formed: {len(groups)}")
                else:
                    groups = [batch]
                    logging.info("[Scheduler] Grouping disabled (naive batching)")
                for group in groups:
                    group_size = len(group)
                    for req in group:
                        req.batch_size = batch_size
                        req.group_size = group_size
                        req.start_time = time.time()
                    logging.info(f"[Scheduler] Processing group size: {len(group)}")

                    prompts = [r.message for r in group]

                    outputs = await asyncio.to_thread(
                        llm.generate, prompts, sampling_params
                    )

                    for req, output in zip(group, outputs):
                        result = output.outputs[0].text

                        if not req.future.done():
                            req.future.set_result(result)
                        req.end_time = time.time()
                        latency = time.time() - req.arrival_time
                        logging.info(f"[Latency][{req.id}] {latency:.2f}s")
                        log_data = {
                            "id": req.id,
                            "latency": round(latency, 3),
                            "batch_size": req.batch_size,
                            "group_size": req.group_size,
                        }
                        logging.info(f"[Metrics] {json.dumps(log_data)}")
                        with open(CSV_FILE, "a", newline="") as f:
                            writer = csv.writer(f)
                            writer.writerow([
                                req.id,
                                round(latency, 3),
                                req.batch_size,
                                req.group_size
                            ])
            except Exception as e:
                logging.error(f"[Scheduler] Error: {e}")

                for req in batch:
                    if not req.future.done():
                        req.future.set_exception(e)
