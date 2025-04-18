import concurrent.futures
import requests
import time
import json

# 要测试的API URL
API_URL = "http://127.0.0.1:5000/auth/register"


NUM_REQUESTS = 1000


NUM_WORKERS = 50


PAYLOAD = {
    "price": 100,
}

def make_request():
    try:
        response = requests.post(API_URL, json=PAYLOAD)
        return response.status_code, response.text
    except Exception as e:
        return None, str(e)

def run_load_test():
    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        futures = [executor.submit(make_request) for _ in range(NUM_REQUESTS)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    end_time = time.time()
    total_time = end_time - start_time

    # 统计结果
    success_count = sum(1 for status, _ in results if status == 200)
    failure_count = NUM_REQUESTS - success_count

    print(f"Total requests: {NUM_REQUESTS}")
    print(f"Successful requests: {success_count}")
    print(f"Failed requests: {failure_count}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Requests per second: {NUM_REQUESTS / total_time:.2f}")

if __name__ == "__main__":
    run_load_test()
