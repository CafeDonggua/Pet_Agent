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
    print("8. 寫入 excluded behaviors")
    print("9. 查詢 abnormal behaviors")
    print("10. 查詢所有向量記憶")
    print("11. 新增一筆向量記憶")
    print("12. 刪除一筆向量記憶")
    print("13. 查詢狗狗現在狀態")
    print("14. 刪除一筆 excluded behaviors")
    print("15. 刪除一筆 current plan")
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
    elif choice == "8":
        resp = requests.post(f"{BASE_URL}/excluded_behaviors", json={"behavior": "趴睡"})
        print(resp.json())
    elif choice == "9":
        resp = requests.get(f"{BASE_URL}/abnormal_behaviors")
        print(resp.json())
    elif choice == "10":
        resp = requests.get(f"{BASE_URL}/vector_memory/all")
        print(resp.json())
    elif choice == "11":
        text = input("請輸入要新增的向量記憶內容：")
        resp = requests.post(f"{BASE_URL}/vector_memory", json={"text": text})
        print(resp.json())
    elif choice == "12":
        text = input("請輸入要刪除的向量記憶內容（需完全符合）：")
        resp = requests.delete(f"{BASE_URL}/vector_memory", json={"text": text})
        print(resp.json())
    elif choice == "13":
        resp = requests.post(f"{BASE_URL}/ask_agent", json={"text": "狗狗現在情緒正常嗎？"})
        print(resp.json())
    elif choice == "14":
        resp = requests.delete(f"{BASE_URL}/excluded_behaviors", json={"behavior": "趴睡"})
        print(resp.json())
    elif choice == "15":
        resp = requests.delete(f"{BASE_URL}/current_plan", json={"time": "20250429160000", "action": "散步"})
        print(resp.json())
    elif choice == "0":
        break

    else:
        print("無效的選項，請重新輸入！")