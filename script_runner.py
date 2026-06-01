import subprocess
import os
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

def update_failed_runner(failed_scripts, target_folder, platform):
    runner_filename = "failed-script-runner.py"
    if not os.path.exists(runner_filename):
        print(f"⚠️ '{runner_filename}' not found. Make sure it exists in the root.")
        return

    with open(runner_filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.strip().startswith('platform ='):
            lines[i] = f'    platform = "{platform.upper()}"\n'
        elif line.strip().startswith('target_folder ='):
            lines[i] = f'    target_folder = "{target_folder}"\n'
        elif line.strip().startswith('failed_scripts ='):
            lines[i] = f'    failed_scripts = {repr(failed_scripts)}\n'

    with open(runner_filename, "w", encoding="utf-8") as f:
        f.write("".join(lines))
    print(f"💾 Updated '{runner_filename}' with {len(failed_scripts)} failed script(s).")

def main():
    print("--- Bell BYOD Script Runner ---")
    
    target_folder = "weekly-sanity-automation"
    
    while True:
        platform = input("Enter platform ('desktop', 'mobile', or 'tablet'): ").strip().lower()
        if platform in ["desktop", "mobile", "tablet"]:
            break
        print("Invalid choice. Please type exactly 'desktop', 'mobile', or 'tablet'.\n")
    
    brands = ["bell", "virgin"]
    sim_types = ["esim", "psim"]
    
    results_report = {}
    failed_scripts_list = []
    
    for brand in brands:
        for sim in sim_types:
            filename = f"{brand}_byod_{sim}_{platform}.py"
            target_script_path = os.path.join(target_folder, filename)
            
            is_success = run_script(target_script_path)
            if not is_success:
                failed_scripts_list.append(filename)
                
            results_report[filename] = "PASSED" if is_success else "FAILED"
        
    print("\n" + "="*45)
    print("📋 FINAL AUTOMATION EXECUTION REPORT")
    print("="*45)
    
    failed_count = 0
    for script, status in results_report.items():
        icon = "🟢" if status == "PASSED" else "🔴"
        print(f"{icon} {script.ljust(35)} : {status}")
        if status == "FAILED":
            failed_count += 1
            
    print("="*45)
    if failed_count == 0:
        print("🎉 All tasks completed successfully for the day!")
        update_failed_runner([], target_folder, platform)
    else:
        print(f"⚠️ Done. {failed_count} script(s) failed. Please review the logs above for errors.")
        print("="*45)
        update_failed_runner(failed_scripts_list, target_folder, platform)
    print("="*45)

if __name__ == "__main__":
    main()