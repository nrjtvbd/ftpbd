import zipfile
import os
import subprocess
import sys

# নতুন নাম অনুযায়ী কনফিগারেশন
ZIP_FILE = "ftpbd_main.zip" 
EXTRACT_PATH = "temp_core"
PASSWORD = os.getenv("CORE_PASS") 
MAIN_FILE = "ftpbd_auto.py"

def run_process():
    if not PASSWORD:
        print("❌ Error: CORE_PASS secret is missing in GitHub!")
        sys.exit(1)

    try:
        # জিপ ফাইল খোলা
        with zipfile.ZipFile(ZIP_FILE, 'r') as zip_ref:
            print(f"🔓 Extracting {ZIP_FILE}...")
            # পাসওয়ার্ড দিয়ে আনজিপ করা
            zip_ref.extractall(path=EXTRACT_PATH, pwd=PASSWORD.encode())
        
        # আনজিপ হওয়া ফোল্ডারে ঢোকা
        os.chdir(EXTRACT_PATH)
        
        # মেইন ফাইলটি রান করা
        print("🚀 Executing main logic...")
        subprocess.run(["python", MAIN_FILE], check=True)
        
    except Exception as e:
        print(f"❌ Operation Failed: {str(e)}")
        sys.exit(1)
    finally:
        print("🧹 Task completed.")

if __name__ == "__main__":
    run_process()
