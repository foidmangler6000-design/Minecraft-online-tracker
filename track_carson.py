import requests
import time
import threading
import os
import subprocess
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

def send_notification_curl(username, status="online"):
    """Fallback method: Send notification using curl"""
    if status == "online":
        message = f"Carson_211 just joined Minecraft! Time to play! 🚀"
        title = "🎮 Carson is Online!"
        priority = "5"
        tags = "partying_face,minecraft"
    else:
        message = f"Carson_211 left Minecraft. See you next time!"
        title = "👋 Carson went Offline"
        priority = "3"
        tags = "wave,minecraft"
    
    # Format the curl command
    cmd = [
        "curl", "-s",
        "-H", f"Title: {title}",
        "-H", f"Priority: {priority}",
        "-H", f"Tags: {tags}",
        "-H", f"Click: https://minecraft.net",
        "-d", message,
        f"{NTFY_SERVER}/{NTFY_TOPIC}"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Curl notification sent successfully!")
            return True
        else:
            print(f"❌ Curl failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Curl exception: {e}")
        return False

def send_notification(username, status="online"):
    """Send notification using requests, fallback to curl"""
    if status == "online":
        message = f"Carson_211 just joined Minecraft! Time to play! 🚀"
        title = "🎮 Carson is Online!"
        priority = "5"
        tags = "partying_face,minecraft"
    else:
        message = f"Carson_211 left Minecraft. See you next time!"
        title = "👋 Carson went Offline"
        priority = "3"
        tags = "wave,minecraft"
    
    # Method 1: Try requests with proper headers
    try:
        url = f"{NTFY_SERVER}/{NTFY_TOPIC}"
        headers = {
            "Content-Type": "text/plain",
            "Title": title,
            "Priority": priority,
            "Tags": tags,
            "Click": "https://minecraft.net",
        }
        
        print(f"📤 Sending to: {url}")
        print(f"   Title: {title}")
        print(f"   Message: {message}")
        
        response = requests.post(
            url,
            data=message.encode('utf-8'),
            headers=headers,
            timeout=10
        )
        
        print(f"   Response status: {response.status_code}")
        print(f"   Response body: {response.text}")
        
        if response.status_code == 200:
            print(f"✅ Notification sent successfully!")
            return True
        else:
            print(f"❌ Requests method failed, trying curl fallback...")
            return send_notification_curl(username, status)
            
    except Exception as e:
        print(f"❌ Requests exception: {e}")
        print(f"🔄 Trying curl fallback...")
        return send_notification_curl(username, status)

# ============================================
# MAIN TRACKING LOOP
# ============================================
def tracker_loop():
    """Main background loop that checks player status"""
    last_status = None
    
    print(f"🏠 Minecraft Friend Tracker Started")
    print(f"Tracking: {FRIEND_USERNAME}")
    print(f"UUID: {FRIEND_UUID}")
    print(f"NTFY Topic: {NTFY_TOPIC}")
    print(f"Checking every {CHECK_INTERVAL} seconds...")
    
    while True:
        try:
            current_status = check_player_online(FRIEND_UUID)
            
            # Only notify if status changed
            if last_status is None or current_status != last_status:
                if current_status:
                    send_notification(FRIEND_USERNAME, "online")
                else:
                    send_notification(FRIEND_USERNAME, "offline")
                last_status = current_status
                
        except Exception as e:
            print(f"⚠️  Main loop error: {e}")
        
        time.sleep(CHECK_INTERVAL)

# ============================================
# FLASK ROUTES (For Render Health Checks)
# ============================================
@app.route('/')
def home():
    return jsonify({"status": "running", "tracking": FRIEND_USERNAME})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/test')
def test():
    result = send_notification(FRIEND_USERNAME, "online")
    return jsonify({"notification_sent": result})

# ============================================
# START SERVER & TRACKER
# ============================================
if __name__ == '__main__':
    # Start the tracker in a background thread
    tracker_thread = threading.Thread(target=tracker_loop, daemon=True)
    tracker_thread.start()
    
    # Get port from environment
    port = int(os.environ.get('PORT', 10000))
    
    # Use Gunicorn for production, fall back to Flask if not available
    try:
        from gunicorn.app.wsgiapp import run
        print("🚀 Starting with Gunicorn (Production)...")
        run()
    except ImportError:
        print("⚠️  Gunicorn not found, using Flask dev server...")
        app.run(host='0.0.0.0', port=port)
    
    print(f"✅ Server started successfully!")
def send_notification_curl(username, status="online"):
    """Fallback: Send notification using curl command"""
    if status == "online":
        message = f"Carson_211 just joined Minecraft! Time to play! 🚀"
        title = "🎮 Carson is Online!"
    else:
        message = f"Carson_211 left Minecraft. See you next time!"
        title = "👋 Carson went Offline"
    
    try:
        # Build curl command
        cmd = [
            "curl", "-X", "POST",
            "-H", "Content-Type: text/plain",
            "-d", message,
            "-H", f"Title: {title}",
            "-H", "Priority: 5" if status == "online" else "Priority: 3",
            f"https://ntfy.sh/{NTFY_TOPIC}"
        ]
        
        print(f"📤 Running curl: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        print(f"   Exit code: {result.returncode}")
        print(f"   Output: {result.stdout}")
        if result.stderr:
            print(f"   Error: {result.stderr}")
        
        if result.returncode == 0:
            print(f"✅ Notification sent via curl!")
            return True
        else:
            print(f"❌ Curl failed with exit code: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ Curl timeout")
        return False
    except Exception as e:
        print(f"❌ Curl exception: {e}")
        return False

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
    print("   Topic: " + NTFY_TOPIC)
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
    print(f"🧪 Test endpoint called at {time.strftime('%H:%M:%S')}")
    success = send_notification(FRIEND_USERNAME, "online")
    
    if success:
        return jsonify({
            "message": "Test notification sent successfully!",
            "topic": NTFY_TOPIC,
            "friend": FRIEND_USERNAME
        })
    else:
        return jsonify({
            "message": "Failed to send notification. Check Render logs.",
            "topic": NTFY_TOPIC,
            "friend": FRIEND_USERNAME,
            "status": "error"
        }), 500

@app.route('/test-offline')
def test_offline_notification():
    """Send a test offline notification"""
    print(f"🧪 Test offline endpoint called at {time.strftime('%H:%M:%S')}")
    success = send_notification(FRIEND_USERNAME, "offline")
    
    if success:
        return jsonify({
            "message": "Test offline notification sent successfully!",
            "topic": NTFY_TOPIC,
            "friend": FRIEND_USERNAME
        })
    else:
        return jsonify({
            "message": "Failed to send notification. Check Render logs.",
            "topic": NTFY_TOPIC,
            "friend": FRIEND_USERNAME,
            "status": "error"
        }), 500

@app.route('/debug')
def debug_info():
    """Show debug information about the ntfy connection"""
    print(f"🔍 Debug endpoint called at {time.strftime('%H:%M:%S')}")
    
    test_result = {
        "ntfy_server": NTFY_SERVER,
        "ntfy_topic": NTFY_TOPIC,
        "friend": FRIEND_USERNAME,
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Try to send a test message
    try:
        test_response = requests.post(
            f"{NTFY_SERVER}/{NTFY_TOPIC}",
            data="Debug test from Render".encode('utf-8'),
            headers={"Title": "Debug Test", "Content-Type": "text/plain"},
            timeout=5
        )
        test_result["connection_test"] = {
            "status_code": test_response.status_code,
            "success": test_response.status_code == 200,
            "response": test_response.text
        }
    except Exception as e:
        test_result["connection_test"] = {
            "error": str(e),
            "success": False
        }
    
    return jsonify(test_result)

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
    print(f"🔍 Debug info: http://localhost:{port}/debug")
    print("=" * 40)
    
    app.run(host='0.0.0.0', port=port)            
    print(f"✅ Notification sent successfully!")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print(f"❌ Connection timeout to ntfy.sh")
        return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

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
    print("   Topic: " + NTFY_TOPIC)
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
    print(f"🧪 Test endpoint called at {time.strftime('%H:%M:%S')}")
    success = send_notification(FRIEND_USERNAME, "online")
    
    if success:
        return jsonify({
            "message": "Test notification sent successfully!",
            "topic": NTFY_TOPIC,
            "friend": FRIEND_USERNAME
        })
    else:
        return jsonify({
            "message": "Failed to send notification. Check Render logs.",
            "topic": NTFY_TOPIC,
            "friend": FRIEND_USERNAME,
            "status": "error"
        }), 500

@app.route('/test-offline')
def test_offline_notification():
    """Send a test offline notification"""
    print(f"🧪 Test offline endpoint called at {time.strftime('%H:%M:%S')}")
    success = send_notification(FRIEND_USERNAME, "offline")
    
    if success:
        return jsonify({
            "message": "Test offline notification sent successfully!",
            "topic": NTFY_TOPIC,
            "friend": FRIEND_USERNAME
        })
    else:
        return jsonify({
            "message": "Failed to send notification. Check Render logs.",
            "topic": NTFY_TOPIC,
            "friend": FRIEND_USERNAME,
            "status": "error"
        }), 500

@app.route('/debug')
def debug_info():
    """Show debug information about the ntfy connection"""
    print(f"🔍 Debug endpoint called at {time.strftime('%H:%M:%S')}")
    
    # Test the ntfy connection
    test_result = {
        "ntfy_server": NTFY_SERVER,
        "ntfy_topic": NTFY_TOPIC,
        "friend": FRIEND_USERNAME,
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Try to send a test message
    try:
        test_response = requests.post(
            f"{NTFY_SERVER}/{NTFY_TOPIC}",
            data="Debug test from Render".encode('utf-8'),
            headers={"Title": "Debug Test"},
            timeout=5
        )
        test_result["connection_test"] = {
            "status_code": test_response.status_code,
            "success": test_response.status_code == 200
        }
    except Exception as e:
        test_result["connection_test"] = {
            "error": str(e),
            "success": False
        }
    
    return jsonify(test_result)

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
    print(f"🔍 Debug info: http://localhost:{port}/debug")
    print("=" * 40)
    
    app.run(host='0.0.0.0', port=port)
