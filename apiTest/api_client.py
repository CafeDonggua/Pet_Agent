# api_client.py

import requests

BASE_URL = "http://localhost:8000"
sample_memories_A = [
    "狗狗在興奮時喜歡搖尾巴",
    "當狗狗肚子餓時會坐在餵食機旁邊等待。"
]

sample_memories_B = [
    "狗狗知道攝影機的存在，也知道主人能透過攝影機看著他，所以想要吸引主人注意。",
    "狗狗喜歡翻滾玩耍。"
]


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
    print("10. 新增一筆向量記憶")
    print("11. 刪除一筆向量記憶")
    print("12. 詢問 Agent 關於狗狗的問題")
    print("13. 刪除一筆 excluded behaviors")
    print("14. 刪除一筆 current plan")
    print("15. 設定 Dog A")
    print("16. 刪除一筆 Dog A 記憶")
    print("17. 設定 Dog B")
    print("18. 刪除 Dog B 記憶")
    print("0. 離開")
    choice = input("請輸入選項：")

    if choice == "1":
        resp = requests.get(f"{BASE_URL}/daily_plan")
        if resp.status_code != 200:
            print(f" 錯誤：{resp.status_code} - {resp.text}")
        else:
            plans = resp.json()
            for i, plan in enumerate(plans, 1):
                print(f"\n [計畫 {i}]")
                print(f"   時間   ：{plan.get('time', '')}")
                print(f"   行動   ：{plan.get('action', '')}")
                print(f"   備註   ：{plan.get('備註', '')}")
                print(f"   頻率   ：{plan.get('頻率', '')}")
        text = input("===== 按Enter以繼續 =====")

    elif choice == "2":
        resp = requests.get(f"{BASE_URL}/current_plan")
        if resp.status_code != 200:
            print(f" 錯誤：{resp.status_code} - {resp.text}")
        else:
            plans = resp.json()
            for i, plan in enumerate(plans, 1):
                print(f"\n [當前計畫 {i}]")
                print(f"   時間   ：{plan.get('time', '')}")
                print(f"   行動   ：{plan.get('action', '')}")
                print(f"   來源   ：{plan.get('來源', '')}")
                print(f"   衝突   ：{plan.get('衝突', '')}")
            text = input("===== 按Enter以繼續 =====")

    elif choice == "3":
        resp = requests.post(f"{BASE_URL}/daily_plan", json={"time": "20250429160000", "action": "散步"})
        print(resp.json())
    elif choice == "4":
        resp = requests.post(f"{BASE_URL}/current_plan", json={"time": "20250429160000", "action": "散步"})
        print(resp.json())
    elif choice == "5":
        resp = requests.get(f"{BASE_URL}/pet_state")
        print(resp.json())
        text = input("===== 按Enter以繼續 =====")

    elif choice == "6":
        resp = requests.get(f"{BASE_URL}/recent_records")
        if resp.status_code != 200:
            print(f" 錯誤：{resp.status_code} - {resp.text}")
        else:
            records = resp.json()
            for i, record in enumerate(records, 1):
                print(f"\n [第 {i} 筆記錄]")
                print(f"   時間       ：{record.get('時間', '')}")
                print(f"   行為       ：{record.get('行為', '')}")
                print(f"   地點       ：{record.get('地點', '')}")
                print(f"   採取行動   ：{record.get('採取行動', '')}")
                print(f"   行動成效   ：{record.get('行動成效', '')}")
        text = input("===== 按Enter以繼續 =====")

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
        text = input("請輸入要新增的向量記憶內容：")
        resp = requests.post(f"{BASE_URL}/vector_memory", json={"text": text})
        print(resp.json())
    elif choice == "11":
        text = input("請輸入要刪除的向量記憶內容（需完全符合）：")
        resp = requests.delete(f"{BASE_URL}/vector_memory", json={"text": text})
        print(resp.json())
    elif choice == "12":
        text = input("請提問：")
        resp = requests.post(f"{BASE_URL}/ask_agent", json={"text": text})
        try:
            print(resp.json()["answer"])
        except Exception as e:
            print("找不到類似紀錄")
        text = input("===== 按Enter以繼續 =====")

    elif choice == "13":
        resp = requests.delete(f"{BASE_URL}/excluded_behaviors", json={"behavior": "趴睡"})
        print(resp.json())
    elif choice == "14":
        resp = requests.delete(f"{BASE_URL}/current_plan", json={"time": "20250429160000", "action": "散步"})
        print(resp.json())
    elif choice == "15":
        for memory in sample_memories_A:
            resp = requests.post(f"{BASE_URL}/vector_memory", json={"text": memory})
            print(resp.json())
        text = input("===== 按Enter以繼續 =====")

    elif choice == "16":
        resp = requests.delete(f"{BASE_URL}/vector_memory", json={"text": "狗狗在興奮時喜歡搖尾巴"})
        print(resp.json())
        text = input("===== 按Enter以繼續 =====")

    elif choice == "17":
        for memory in sample_memories_B:
            resp = requests.post(f"{BASE_URL}/vector_memory", json={"text": memory})
            print(resp.json())
        text = input("===== 按Enter以繼續 =====")

    elif choice == "18":
        for memory in sample_memories_B:
            resp = requests.delete(f"{BASE_URL}/vector_memory", json={"text": memory})
            print(resp.json())
        text = input("===== 按Enter以繼續 =====")

    elif choice == "0":
        break

    else:
        print("無效的選項，請重新輸入！")
