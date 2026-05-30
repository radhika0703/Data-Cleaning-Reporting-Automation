import os
import subprocess
import sys

def main():
    dashboard_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "src", "app", "dashboard.py"))
    if not os.path.exists(dashboard_path):
        print(f"Error: Dashboard file not found at {dashboard_path}")
        sys.exit(1)
        
    print("Starting Antigravity Data Cleaning & Reporting Interactive Dashboard...")
    try:
        subprocess.run(["streamlit", "run", dashboard_path], check=True)
    except KeyboardInterrupt:
        print("\nStopping dashboard server. Goodbye!")
    except Exception as e:
        print(f"Error starting dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
