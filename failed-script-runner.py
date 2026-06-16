import os
import subprocess
import time

def run_script(script_path, max_retries=2):
    if not os.path.exists(script_path):
        print(f"❌ Error: The file '{script_path}' was not found.")
        return False

    success_marker = "✅ Order submitted successfully!"
    script_name = os.path.basename(script_path)
    
    for attempt in range(1, max_retries + 1):
        print(f"\n🚀 Launching {script_name} (Attempt {attempt}/{max_retries})...")
        
        result = subprocess.run(["python", script_path], capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="")

        failed_with_stacktrace = result.returncode != 0
        missing_success_message = success_marker not in result.stdout

        if failed_with_stacktrace or missing_success_message:
            print(f"⚠️ {script_name} failed or didn't complete properly.")
            if attempt < max_retries:
                print("🔄 Retrying in 3 seconds...")
                time.sleep(3)
            else:
                print(f"❌ {script_name} failed after {max_retries} attempts.")
                return False
        else:
            print(f"✅ {script_name} finished successfully.")
            return True
            
    return False

def main():    
    print("--- 🔄 Failed Scripts Recovery Runner ---")
    
    # The main runner will overwrite the values below dynamically
    platform = "TABLET"
    target_folder = "weekly-sanity-automation"
    failed_scripts = ['virgin_byod_psim_tablet.py']
    
    print(f"Platform Context: {platform}")
    
    if not failed_scripts:
        print("🎉 No failed scripts configured to run!")
        return

    results_report = {}
    
    for filename in failed_scripts:
        target_script_path = os.path.join(target_folder, filename)
        is_success = run_script(target_script_path)
        results_report[filename] = "PASSED" if is_success else "FAILED"
        
    print("\n" + "="*45)
    print("📋 RE-RUN AUTOMATION EXECUTION REPORT")
    print("="*45)
    
    still_failed = 0
    for script, status in results_report.items():
        icon = "🟢" if status == "PASSED" else "🔴"
        print(f"{icon} {script.ljust(35)} : {status}")
        if status == "FAILED":
            still_failed += 1
            
    print("="*45)
    if still_failed == 0:
        print("🎉 All previously failed tasks completed successfully!")
    else:
        print(f"⚠️ {still_failed} script(s) STILL failed. Please review logs.")
    print("="*45)

if __name__ == '__main__':
    main()