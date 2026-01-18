# Apple Silicon Video Compressor

A specialized Python utility designed for batch compressing `.mov` videos on macOS (optimized for M1/M2/M3/M4 chips). This script allows you to choose between lightning-fast **Hardware Acceleration** or high-efficiency **Software Encoding**, while meticulously preserving original file metadata and creation dates.

## 🚀 Features

- **Apple Silicon Optimized:** Leverages `h264_videotoolbox` for near-instant compression using dedicated media engines.
- **Dual Encoding Modes:**
    - **Hardware:** Ultra-fast and energy-efficient (compensates quality with a higher 1.5M bitrate).
    - **Software:** Maximum quality-to-size ratio (uses 1M bitrate).
- **Metadata Preservation:** Uses `ExifTool` to ensure "Date Created" and "Date Modified" in the Finder remain identical to the original file.
- **Intelligent Logging:** Real-time display of original size, new size, and the exact reduction percentage.
- **Batch Processing:** Recursively scans directories to process hundreds of videos while maintaining folder structure.

---

## 🛠 Prerequisites

You must have the following tools installed on your Mac:

1. **Python 3.x**
2. **FFmpeg:** For the video processing engine.
3. **ExifTool:** For syncing file system creation dates.

You can install the dependencies via [Homebrew](https://brew.sh/):

```bash
brew install ffmpeg exiftool
```

---

## 📖 How to Use

1. **Setup:** Place the script in the parent directory containing the videos you wish to compress.
2. **Run:** Open your terminal and execute:

```bash
python3 compress_video.py
```

3. **Menu 1:** Choose whether to create copies in a separate folder or overwrite the original files.
4. **Menu 2:** Select your preferred encoding engine (Hardware for speed, Software for quality).

---

## 📊 Comparison: Hardware vs. Software

| Feature | Hardware (videotoolbox) | Software (libx264) |
|---------|------------------------|-------------------|
| Speed | ⚡ Ultra-Fast | 🐢 Slower |
| CPU Load | Minimal (Mac stays cool) | High (Fans may spin) |
| Efficiency | Good (at 1.5 Mbps) | Excellent (at 1.0 Mbps) |
| Best For | Fast exports / Large batches | Long-term archiving |

---

## 📝 Global Configuration

You can tweak the constants at the top of the Python file to suit your needs:

- `HARDWARE_BITRATE`: (Default: `1.5M`)
- `SOFTWARE_BITRATE`: (Default: `1M`)
- `TARGET_EXTENSION`: (Default: `.mov`)
- `AUDIO_BITRATE`: (Default: `64k`)