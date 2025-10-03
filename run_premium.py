"""
Minimal launcher to guarantee the premium app (app_premium) is what you're running.
Runs on port 5500 and prints every registered route including a sentinel marker.
"""
from datetime import datetime
import socket
import sys
import traceback
import threading
import time
import webbrowser

try:
    from app_premium import app as premium_app
    from task_scheduler import task_scheduler # Import the scheduler
    app_loaded = True
except Exception as e:
    print("❌ Failed to import app_premium:", e)
    traceback.print_exc()
    app_loaded = False

# Add a sentinel diagnostic route (will only exist if premium app is truly loaded here)
if app_loaded:
    if '__premium_marker' not in [r.endpoint for r in premium_app.url_map.iter_rules()]:
        premium_app.add_url_rule('/__premium_marker', 'premium_marker', lambda: {
            'app': 'premium',
            'time': datetime.now().isoformat(),
            'routes': len(list(premium_app.url_map.iter_rules()))
        })

def dump_routes():
    if not app_loaded:
        print("⚠️ premium app not loaded; no routes to display.")
        return
    print('\n🧭 Premium Route Map:')
    lines = []
    for rule in sorted(premium_app.url_map.iter_rules(), key=lambda r: r.rule):
        methods = ','.join(m for m in rule.methods if m not in ('HEAD','OPTIONS'))
        line = f"{rule.rule} -> {methods}"
        print(f"  {line}")
        lines.append(line)
    print('\n✅ Expected critical routes: /paper-trading, /api/paper-trading/create-portfolio, /__debug/routes, /test-all-features')
    print('🔎 Marker: http://localhost:5500/__premium_marker')
    try:
        with open('route_map.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    except Exception as e:
        print(f"⚠️ Could not write route_map.txt: {e}")

def find_open_port(preferred=5501):
    # If preferred is free, return it; else find next free port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('127.0.0.1', preferred)) != 0:
            return preferred
    for p in range(preferred+1, preferred+20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as t:
            if t.connect_ex(('127.0.0.1', p)) != 0:
                return p
    return preferred

if __name__ == '__main__':
    if not app_loaded:
        print("❌ Cannot start server because app_premium import failed.")
        sys.exit(1)
    dump_routes()
    port = find_open_port(5500)
    # Persist port info for external tools / user clarity
    try:
        with open('premium_port.info', 'w', encoding='utf-8') as f:
            f.write(str(port))
    except Exception as _e:
        print(f"⚠️ Could not write premium_port.info: {_e}")
    print(f"\n🚀 Starting PREMIUM server on http://localhost:{port} ...")
    print("(If browser can't connect, copy this entire console output and send it.)")

    def open_browser():
        # delay to let server bind
        time.sleep(2)
        try:
            webbrowser.open(f"http://localhost:{port}/paper-trading")
            webbrowser.open(f"http://localhost:{port}/test-all-features")
        except Exception as e:
            print(f"⚠️ Could not auto-open browser: {e}")

    def heartbeat():
        while True:
            time.sleep(15)
            print(f"🫀 Heartbeat: server intended on port {port} - {datetime.now().strftime('%H:%M:%S')}")

    threading.Thread(target=open_browser, daemon=True).start()
    threading.Thread(target=heartbeat, daemon=True).start()
    
    # Start the task scheduler
    task_scheduler.start()

    try:
        premium_app.run(debug=False, use_reloader=False, host='127.0.0.1', port=port)
    except OSError as e:
        print(f"❌ Server failed to bind port {port}: {e}")
        traceback.print_exc()
        sys.exit(2)
