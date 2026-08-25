import requests
import time
import json

# --- CONFIGURATION ---
FRIEND_USERNAME = "Carson_211"
FRIEND_UUID = "40f592a7-b506-4dfe-9a43-5c2a40c41c7c"
NTFY_TOPIC = "carson-minecraft-tracker"  # Unique topic for Carson
CHECK_INTERVAL = 30  # Check every 30 seconds
NTFY_SERVER = "https://ntfy.sh"  # Public server (free)

# --- HELPER FUNCTIONS ---

def check_player_online(uuid):
    """Check if player is online using Hypixel API"""
    try:
        resp = requests.get(
            f"https://api.hypixel.net/player",
            params={"uuid": uuid},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("player"):
                return data["player"].get("online", False)
            else:
                return False
        else:
            print(f"⚠️  API error: {resp.status_code}")
            return False
    except Exception as e:
        print(f"⚠️  Connection error: {e}")
        return False

def send_notification(username, status="online"):
    """Send notification to your phone via ntfy"""
    if status == "online":
        title = "🎮 Carson is Online!"
        message = f"Carson_211 just joined Minecraft! Time to play! 🚀"
        priority = 5  # High priority (makes a loud sound)
        tags = "partying_face, minecraft"
    else:
        title = "👋 Carson went Offline"
        message = f"Carson_211 left Minecraft. See you next time!"
        priority = 3  # Default priority
        tags = "wave, minecraft"
    
    # Prepare the notification data
    headers = {
        "Title": title,
        "Priority": str(priority),
        "Tags": tags,
        "Click": "https://minecraft.net",  # Opens Minecraft website when you tap
    }
    
    # Send to ntfy
    try:
        response = requests.post(
            f"{NTFY_SERVER}/{NTFY_TOPIC}",
            data=message.encode('utf-8'),
            headers=headers
        )
        if response.status_code == 200:
            print(f"✅ Notification sent: {title}")
        else:
            print(f"⚠️  Failed to send notification: {response.status_code}")
    except Exception as e:
        print(f"❌ Error sending notification: {e}")

def subscribe_to_ntfy_topic():
    """Print instructions for subscribing to the ntfy topic"""
    print("\n" + "="*60)
    print("📱 TO SET UP YOUR PHONE:")
    print("="*60)
    print(f"1. Install the ntfy app from your app store")
    print(f"   • iOS: https://apps.apple.com/app/ntfy/id1625396347")
    print(f"   • Android: https://play.google.com/store/apps/details?id=io.heckel.ntfy")
    print(f"2. Open the app and subscribe to this topic:")
    print(f"   🔑 Topic: {NTFY_TOPIC}")
    print(f"3. Go to Settings → Notifications and set custom sound")
    print(f"   (You can use any MP3 file on your phone)")
    print("="*60 + "\n")

# --- MAIN SCRIPT ---

def main():
    print("🎮 Minecraft Friend Tracker")
    print("-" * 40)
    print(f"Tracking: {FRIEND_USERNAME}")
    print(f"UUID: {FRIEND_UUID}")
    print("-" * 40)
    
    # Subscribe instructions
    subscribe_to_ntfy_topic()
    
    print(f"🔄 Checking every {CHECK_INTERVAL} seconds...")
    print("Press Ctrl+C to stop\n")
    
    was_online = False
    first_check = True
    
    while True:
        try:
            is_online = check_player_online(FRIEND_UUID)
            
            # Only send notifications after first check (to avoid false positives)
            if not first_check:
                if is_online and not was_online:
                    send_notification(FRIEND_USERNAME, "online")
                    was_online = True
                elif not is_online and was_online:
                    send_notification(FRIEND_USERNAME, "offline")
                    was_online = False
            else:
                # First check - just set the initial state
                was_online = is_online
                status = "online" if is_online else "offline"
                print(f"📊 Initial status: {FRIEND_USERNAME} is {status}")
                first_check = False
            
            # Show status dot with timestamp
            dot = "🟢" if is_online else "🔴"
            timestamp = time.strftime('%H:%M:%S')
            status_text = "ONLINE ✅" if is_online else "OFFLINE ❌"
            print(f"{dot} {timestamp} | {FRIEND_USERNAME}: {status_text}")
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\n👋 Stopping tracker. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()