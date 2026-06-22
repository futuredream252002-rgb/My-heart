import os
import json
import time
import requests
from datetime import datetime

# configuration
TRX_API = "https://draw.ar-lottery01.com/TrxWinGo/TrxWinGo_1M/GetHistoryIssuePage.json"
JSON_FILE = "data.json"
MAX_CANDLES = 500  # Server နေရာမပြည့်စေရန် နောက်ဆုံး data 500 ပဲ သိမ်းမည်

def fetch_and_update_data():
    try:
        # Cache ငြိခြင်းမှ ကာကွယ်ရန် timestamp ထည့်ခေါ်ခြင်း
        nocache_url = f"{TRX_API}?nocache={int(time.time() * 1000)}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(nocache_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"[{datetime.now()}] API Error: Status Code {response.status_code}")
            return
            
        json_data = response.json()
        
        if json_data.get("code") == 0 and "data" in json_data and "list" in json_data["data"]:
            api_list = json_data["data"]["list"]  # API မှ ပါလာသော array
            
            # ရှိပြီးသား local data.json ကို ဖတ်ရန်
            local_data = []
            if os.path.exists(JSON_FILE):
                try:
                    with open(JSON_FILE, 'r', encoding='utf-8') as f:
                        local_data = json.load(f)
                except Exception:
                    local_data = []

            # ဓာတ်ခွဲခန်း - ဒေတာအသစ်များကို Issue Number စစ်ပြီး ပေါင်းထည့်ခြင်း
            updated = False
            # API က အသစ်ကနေ အဟောင်းအတိုင်း ပြန်ပေးတတ်လို့ ပြောင်းပြန်လှန်ပြီး ပေါင်းထည့်သည်
            for item in reversed(api_list):
                issue_number = item.get("issueNumber")
                
                # ရှိပြီးသား ဒေတာထဲမှာ ဒီ issue number ပါပြီးသားလား စစ်ဆေးခြင်း
                if not any(d.get("issueNumber") == issue_number for d in local_data):
                    local_data.append(item)
                    updated = True
                    print(f"[{datetime.now()}] New Period Captured: {issue_number}")

            if updated:
                # ဒေတာ အရေအတွက် ကန့်သတ်ချက်ထက် ကျော်ပါက အဟောင်းများကို ဖြတ်ထုတ်ရန်
                if len(local_data) > MAX_CANDLES:
                    local_data = local_data[-MAX_CANDLES:]
                    
                # ဒေတာအသစ်ကို JSON ဖိုင်ထဲ ပြန်သိမ်းခြင်း
                with open(JSON_FILE, 'w', encoding='utf-8') as f:
                    json.dump(local_data, f, indent=4, ensure_ascii=False)
                print(f"[{datetime.now()}] data.json synchronized successfully.")
                
    except Exception as e:
        print(f"[{datetime.now()}] Exception occurred: {str(e)}")

if __name__ == "__main__":
    print("🚀 TRX 24/7 Python Engine Started...")
   
    fetch_and_update_data()
    while True:
        time.sleep(15) 
        fetch_and_update_data()
