import time
import threading
import subprocess
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException, TimeoutException

from pathlib import Path

class GlobalNav:
    
    def __init__(self, driver):
        # We store the driver inside the instance so all methods can see it
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 20)

    def start_recording(self, display_num: int, display_size: tuple, file_name: str):
        
        ffmpeg_cmd = [
            "ffmpeg", "-y", 
            "-f", "x11grab", 
            "-draw_mouse", "0",
            "-video_size", f"{display_size[0]}x{display_size[1]}",
            "-i", f":{display_num}.0+0,0",
            "-codec:v", "libx264", "-pix_fmt", "yuv420p", "-r", "24",
            "-preset", "ultrafast", "-tune", "zerolatency", file_name
        ]
        
        self.video_recorder = subprocess.Popen(
            ffmpeg_cmd, 
            stdin=subprocess.PIPE, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        print(f"🎥 Video recorder instantiated inside GlobalNav framework context.")

    def stop_recording(self):
        if hasattr(self, 'video_recorder'):
            self.video_recorder.terminate() # SIGTERM allows FFmpeg to close the file
            try:
                self.video_recorder.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.video_recorder.kill()
                self.video_recorder.wait()

            if hasattr(self, 'current_recording_file'):
                input_path = Path(self.current_recording_file)
                if input_path.exists():
                    compressed_path = input_path.with_name(f"compressed_{input_path.name}")
                    
                    print(f"🤐 Compressing recording... {input_path.name}")
                    
                    # -crf 23 to 28 is the sweet spot for great compression vs quality
                    compress_cmd = [
                        "ffmpeg", "-y", "-i", str(input_path),
                        "-codec:v", "libx264", "-preset", "medium", "-crf", "24",
                        "-codec:a", "copy", str(compressed_path)
                    ]
                    
                    # Run synchronously (or thread/process it if you don't want to block)
                    subprocess.run(compress_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    
                    # Replace the giant original with the small compressed file
                    input_path.unlink()  
                    compressed_path.rename(input_path)  
                    print(f"✅ Compression complete! File shrunk drastically.")
                    

    def stable_click(self, locator_or_element, timeout=15, scroll=True):
        """Clicks an element reliably. Logs details if elements are missing or stale."""
        custom_wait = WebDriverWait(
            self.driver, timeout, poll_frequency=1.0, 
            ignored_exceptions=[ElementClickInterceptedException, StaleElementReferenceException]
        )

        for attempt in range(3):
            try:
                # 1. Resolve element
                if isinstance(locator_or_element, WebElement):
                    element = locator_or_element
                else:
                    try:
                        element = custom_wait.until(EC.element_to_be_clickable(locator_or_element))
                    except Exception as e:
                        if attempt == 2:
                            print(f"ERROR: Element missing or not clickable after {timeout}s: {locator_or_element}")
                            raise TimeoutException(f"Element not found: {locator_or_element}") from e
                        
                        print(f"Warning: Element not found on attempt {attempt + 1}/3. Retrying locator: {locator_or_element}")
                        time.sleep(1.5)
                        continue

                # 2. Scroll if requested
                if scroll:
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", element)

                # 3. Click execution
                try:
                    element.click()
                    return 
                except Exception:
                    # Fallback to JavaScript if native click is blocked by an overlay/animation
                    self.driver.execute_script("arguments[0].click();", element)
                    return 

            except Exception as e:
                if attempt == 2:
                    raise e
                print(f"Warning: Click action failed on attempt {attempt + 1}/3. Retrying entire sequence...")
                time.sleep(1.0)


    def landing_popups(self):
        time.sleep(2)
        
        current_url = self.driver.current_url.lower()
        is_bell = "bell.ca" in current_url
        is_virgin = "virginplus.ca" in current_url

        try:
            if is_bell:
                # 1. Handle potential Lightbox
                self.wait.until(
                    EC.visibility_of_element_located((By.ID, "connector"))
                )

                try:
                    lightbox_close = self.wait.until(
                        EC.element_to_be_clickable((By.ID, "close-lightbox"))
                    )
                    time.sleep(1)
                    lightbox_close.click()
                    self.wait.until(EC.staleness_of(lightbox_close))
                    print("Lightbox dismissed instantly.")
                except:
                    print("No lightbox detected, proceeding.")

                # 2. Handle Cookie Banner
                try:
                    cookie_btn = self.driver.find_element(By.ID, "onetrust-accept-btn-handler")
                    if cookie_btn.is_displayed():
                        cookie_btn.click()
                        print("Cookie banner dismissed.")
                except:
                    pass
            
            elif is_virgin:
                try:
                    self.wait.until(
                        EC.visibility_of_element_located((By.ID, "roaming-lightbox-fifa"))
                    )
                    lightbox_close = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//*[@id='close-lightbox'] | //a[@title='Close' and contains(@class, 'closeBtn')]"))
                    )
                    self.driver.execute_script("arguments[0].click();", lightbox_close)
                    print("Virgin Plus Lightbox dismissed.")
                
                except:
                    print("No landing popups appeared")

                # 2. Handle Cookie Banner for Virgin Plus
                try:
                    cookie_btn = self.driver.find_element(By.ID, "onetrust-accept-btn-handler")
                    if cookie_btn.is_displayed():
                        cookie_btn.click()
                        print("Virgin Plus Cookie banner dismissed.")
                except:
                    pass

            else:
                print("Current page not supported")
        
        except Exception as e:
            print("No brand lightbox active or timeout exception reached, proceeding.")


    def start_popup_checker(self):
        """Call this ONCE in your main execution script to begin background monitoring."""
        self._stop_popup_loop = False
        self.popup_thread = threading.Thread(target=self._dismiss_popup_loop, daemon=True)
        self.popup_thread.start()
        print("🤖 Background popup monitoring thread initialized.")

    def stop_popup_checker(self):
        """Call this at the very end of your script to cleanly close down the thread."""
        self._stop_popup_loop = True  # Flips the flag to False, breaking the while loop
        if self.popup_thread:
            self.popup_thread.join(timeout=3)  # Waits up to 3 seconds for the thread to finish its current cycle
            print("🛑 Background popup monitoring thread stopped.")


    def _dismiss_popup_loop(self):
        """The actual loop execution running in the background thread."""
        print("🤖 Background popup monitoring thread actively running...")
        while not self._stop_popup_loop:
            try:

                if self.driver.find_elements(By.ID, "eligible_offers_lightbox"):
                    print("⏸️ Checkout lightbox detected by background thread. Pausing popup checker cycle.")
                    time.sleep(3)
                    continue
                
                # 1. Quickly poll to see if either element is present via the lambda
                target_btn = self.wait.until(
                    lambda d: (
                        d.find_element(By.ID, "ujet-widget").shadow_root.find_element(By.CLASS_NAME, "ujet-minimize")
                        if d.find_elements(By.ID, "ujet-widget") else None
                    ) or (
                        d.find_element(By.XPATH, "//div[@class='home_foot']//button[text()='No']")
                        if d.find_elements(By.XPATH, "//div[@class='home_foot']//button[text()='No']") else None
                    )
                )
                
                # 2. Pass the resolved element into your custom stable_click framework.
                self.stable_click(target_btn, timeout=1, scroll=False)
                print("💥 Unexpected popup intercepted and dismissed via stable_click!")
                
                # 🔥 FIX: Flip the flag immediately to break the while loop and kill the thread
                self._stop_popup_loop = True
                print("🛑 Popup detected. Self-terminating background monitoring thread.")
                break # Hard exit out of the loop immediately
                
            except TimeoutException:
                # Expected when the popup is not present on the DOM
                pass
            except Exception as e:
                # Catching stale element or click interceptions silently so the loop keeps running
                pass
            
            # Rest for 5 seconds before cycling again to minimize CPU usage
            time.sleep(5)