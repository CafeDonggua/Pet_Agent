# api_client.py

import requests

BASE_URL = "http://localhost:8000"

while True:
    print("\n===== PetCare Agent API 測試 =====")
    print("1. 查詢 daily plan")
    print("2. 查詢 current plan")
    print("3. 寫入 daily plan")
    print("4. 寫入 current plan")
    print("5. 查詢 pet state")
    print("6. 查詢 recent records")
    print("7. 查詢 excluded behaviors")
    print("0. 離開")
    choice = input("請輸入選項：")

    if choice == "1":
        resp = requests.get(f"{BASE_URL}/daily_plan")
        print(resp.json())
    elif choice == "2":
        resp = requests.get(f"{BASE_URL}/current_plan")
        print(resp.json())
    elif choice == "3":
        resp = requests.post(f"{BASE_URL}/daily_plan", json={"time": "20250429160000", "action": "散步"})
        print(resp.json())
    elif choice == "4":
        resp = requests.post(f"{BASE_URL}/current_plan", json={"time": "20250429160000", "action": "散步"})
        print(resp.json())
    elif choice == "5":
        resp = requests.get(f"{BASE_URL}/pet_state")
        print(resp.json())
    elif choice == "6":
        resp = requests.get(f"{BASE_URL}/recent_records")
        print(resp.json())
    elif choice == "7":
        resp = requests.get(f"{BASE_URL}/excluded_behaviors")
        print(resp.json())
    elif choice == "0":
        break
    else:
        print("無效的選項，請重新輸入！")