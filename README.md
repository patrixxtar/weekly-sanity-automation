# UI Test Automation Framework (Bell & Virgin)

This repository contains our end-to-end (E2E) automated test framework mapping the user checkout flow for both Bell and Virgin across multiple viewports and devices.

## 🛠 Prerequisites

Before running the tests, ensure your system has the following dependencies installed:

1. **Python 3.8+**
2. **Google Chrome** (The driver handles internal bindings automatically via Selenium 4).
3. **FFmpeg** (Required for screen recording).
   - *Windows:* Install via `winget install ffmpeg` or Chocolatey.
   - *Mac/Linux:* `brew install ffmpeg` or `sudo apt install ffmpeg`.
4. **Xvfb / PyVirtualDisplay bindings** (Required for headless virtual displays if running on Linux/CI).

Install the Python libraries via pip:
```bash
pip install pytest pyvirtualdisplay selenium