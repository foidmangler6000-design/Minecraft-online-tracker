import requests
import time
import threading
import os
from flask import Flask, jsonify

# ============================================
# CONFIGURATION
# ============================================
FRIEND_USERNAME = "Carson_211"
FRIEND_UUID = "40f592a7-b506-4dfe-9a43-5c2a40c41c7c"
NTFY_TOPIC = "carson-minecraft-tracker"
CHECK_INTERVAL = 30  # Check every 30 seconds
NTFY_SERVER = "https://ntfy.sh"

# ============================================
# FLASK WEB SERVER (For Render Keep-Alive)
# ============================================
app = Flask(__name__)

# ============================================
# TRACKER FUNCTIONS
# ============================================

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
    
    headers = {
        "Title": title,
        "Priority": str(priority),
        "Tags": tags,
        "Click": "https://minecraft.net",
    }
    
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

def run_tracker():
    """Main tracking loop - runs continuously in background"""
    print("🎮 Minecraft Friend Tracker Started")
    print("-" * 40)
    print(f"Tracking: {FRIEND_USERNAME}")
    print(f"UUID: {FRIEND_UUID}")
    print(f"NTFY Topic: {NTFY_TOPIC}")
    print(f"Checking every {CHECK_INTERVAL} seconds...")
    print("-" * 40)
    print("📱 Subscribe to the ntfy topic on your phone!")
    print("   App: https://ntfy.sh/app")
    print("-" * 40)
    
    was_online = False
    first_check = True
    
    while True:
        try:
            is_online = check_player_online(FRIEND_UUID)
            
            if not first_check:
                if is_online and not was_online:
                    send_notification(FRIEND_USERNAME, "online")
                    was_online = True
                elif not is_online and was_online:
                    send_notification(FRIEND_USERNAME, "offline")
                    was_online = False
            else:
                was_online = is_online
                status = "online" if is_online else "offline"
                print(f"📊 Initial status: {FRIEND_USERNAME} is {status}")
                first_check = False
            
            # Show status
            dot = "🟢" if is_online else "🔴"
            timestamp = time.strftime('%H:%M:%S')
            status_text = "ONLINE ✅" if is_online else "OFFLINE ❌"
            print(f"{dot} {timestamp} | {FRIEND_USERNAME}: {status_text}")
            
            time.sleep(CHECK_INTERVAL)
            
        except Exception as e:
            print(f"❌ Error in tracker loop: {e}")
            time.sleep(CHECK_INTERVAL)

# ============================================
# WEB ENDPOINTS (For Render Keep-Alive)
# ============================================

@app.route('/')
def home():
    """Home page showing status"""
    return jsonify({
        "service": "Minecraft Friend Tracker",
        "friend": FRIEND_USERNAME,
        "uuid": FRIEND_UUID,
        "status": "running",
        "topic": NTFY_TOPIC
    })

@app.route('/health')
def health_check():
    """Health check endpoint for keep-alive pings"""
    return jsonify({
        "status": "alive",
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
        "friend": FRIEND_USERNAME
    })

@app.route('/test')
def test_notification():
    """Send a test notification to your phone"""
    send_notification(FRIEND_USERNAME, "online")
    return jsonify({"message": "Test notification sent!"})

# ============================================
# MAIN ENTRY POINT
# ============================================

if __name__ == '__main__':
    # Start the tracker in a background thread
    tracker_thread = threading.Thread(target=run_tracker)
    tracker_thread.daemon = True
    tracker_thread.start()
    
    # Get port from environment (Render sets this automatically)
    port = int(os.environ.get('PORT', 10000))
    
    # Start the web server
    print(f"🌐 Web server running on port {port}")
    print(f"📊 Health check: http://localhost:{port}/health")
    print(f"📱 Test notification: http://localhost:{port}/test")
    print("=" * 40)
    
    app.run(host='0.0.0.0', port=port)
