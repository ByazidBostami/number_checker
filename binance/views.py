import os
import time
import random
import undetected_chromedriver as uc
import phonenumbers
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.http import JsonResponse, FileResponse
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from fake_useragent import UserAgent

# File and URL Settings
UPLOAD_DIR = "uploads/"
VALID_FILE = os.path.join(UPLOAD_DIR, "valid.txt")
BINANCE_URL = "https://accounts.binance.com/en/register"

# Ensure Upload Directory Exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# List of Proxies (Replace with Actual Working Proxies)
PROXIES = [
    "http://proxy1:port",
    "http://proxy2:port",
    "http://proxy3:port",
]

def get_random_proxy():
    """Returns a random proxy from the list."""
    return random.choice(PROXIES)

def format_phone_number(phone_number):
    """Formats phone numbers to E.164 international format."""
    try:
        parsed_number = phonenumbers.parse(phone_number, None)
        if phonenumbers.is_valid_number(parsed_number):
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        return None
    except:
        return None

def check_binance_account(phone_number):
    """Checks if a phone number is registered on Binance."""
    phone_number = format_phone_number(phone_number)
    if not phone_number:
        print(f"[❌] Invalid phone number: {phone_number}")
        return False

    # Proxy & User-Agent Setup
    proxy = get_random_proxy()
    user_agent = UserAgent().random
    print(f"🛡️ Using Proxy: {proxy} | User-Agent: {user_agent}")

    # Chrome Options for Stealth Mode
    options = uc.ChromeOptions()
    options.add_argument(f"--proxy-server={proxy}")
    options.add_argument(f"user-agent={user_agent}")
    options.headless = True  # Run in background

    driver = uc.Chrome(options=options)

    try:
        driver.get(BINANCE_URL)
        time.sleep(random.uniform(2, 5))  # Prevent bot detection

        # Select Phone Number Option
        phone_tab = driver.find_element(By.XPATH, "//div[contains(text(),'Phone')]")
        phone_tab.click()
        time.sleep(1)

        # Enter Phone Number
        phone_input = driver.find_element(By.NAME, "email")
        phone_input.send_keys(phone_number)
        phone_input.send_keys(Keys.RETURN)
        time.sleep(3)

        # Check for "This account already exists" message
        error_messages = driver.find_elements(By.XPATH, "//div[contains(text(),'This account already exists')]")

        if error_messages:
            print(f"[✅] {phone_number} exists on Binance.")
            return True
        else:
            print(f"[❌] {phone_number} not found.")
            return False

    except Exception as e:
        print(f"⚠️ Error checking {phone_number}: {e}")
        return False
    finally:
        driver.quit()

def dashboard(request):
    """Renders the dashboard page."""
    return render(request, "dashboard.html")

def process_file(request):
    """Processes uploaded file and checks phone numbers."""
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]
        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)

        # Save Uploaded File
        with default_storage.open(file_path, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        valid_numbers = []
        invalid_count = 0

        # Read Phone Numbers from File
        with open(file_path, "r") as file:
            phone_numbers = [line.strip() for line in file if line.strip()]

        total_numbers = len(phone_numbers)
        print(f"📋 Total Numbers to Check: {total_numbers}")

        for phone in phone_numbers:
            try:
                exists = check_binance_account(phone)
                if exists:
                    valid_numbers.append(phone)
                else:
                    invalid_count += 1
                time.sleep(random.uniform(3, 6))  # Random delay to prevent detection
            except Exception as e:
                print(f"⚠️ Error processing {phone}: {e}")

        # Save Valid Numbers to File
        with open(VALID_FILE, "w") as valid_file:
            valid_file.write("\n".join(valid_numbers))

        print(f"✅ Valid: {len(valid_numbers)} | ❌ Invalid: {invalid_count}")

        return JsonResponse({
            "total": total_numbers,
            "valid": len(valid_numbers),
            "invalid": invalid_count,
            "download_url": "/binance/download_valid/"
        })

    return JsonResponse({"error": "No file uploaded"}, status=400)

def download_valid(request):
    """Allows users to download valid phone numbers."""
    if os.path.exists(VALID_FILE):
        return FileResponse(open(VALID_FILE, "rb"), as_attachment=True, filename="valid.txt")
    return JsonResponse({"error": "File not found"}, status=404)
