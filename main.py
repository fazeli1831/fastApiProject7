from fastapi import FastAPI, Path
import logging
import threading
import time
import random
from typing import Dict

# Initialize FastAPI app
app = FastAPI()

# Setup logging
LOG_FORMAT = '%(asctime)s %(threadName)-17s %(levelname)-8s %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
semaphore = threading.Semaphore(0)
item = 0

# Define the consumer function
def consumer() -> Dict[str, int]:
    logging.info('consumer is waiting')
    semaphore.acquire()
    logging.info(f'consumer notify: item number {item}')
    return {"item": item}

# Define the producer function
def producer() -> int:
    global item
    time.sleep(2)
    item = random.randint(0, 100)
    logging.info(f'producer notify: item number {item}')
    semaphore.release()
    return item

# Define the API endpoint to consume an item
@app.get("/consume/{count}")
def consume(count: int = Path(..., title="Number of items to consume")):
    results = []
    for _ in range(count):
        t1 = threading.Thread(target=consumer)
        t1.start()
        t1.join()
        results.append({"consumed_item": item})
    return {"consumed_items": results}

# Define the API endpoint to produce an item
@app.get("/produce")
def produce_item():
    t2 = threading.Thread(target=producer)
    t2.start()
    t2.join()
    return {"produced_item": item}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)