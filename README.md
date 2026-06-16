# Apple Silicon Video Compressor

A Python utility for batch compressing `.mov` videos on macOS (optimized for M1/M2/M3/M4 chips). Choose between lightning-fast **Hardware Acceleration** (HEVC/H.265) or high-efficiency **Software Encoding** (H.264), while preserving original file metadata and creation dates.

## 🚀 Features

- **Apple Silicon Optimized:** Leverages `hevc_videotoolbox` (H.265) for near-instant compression using dedicated media engines.
- **Dual Encoding Modes:**
    - **Hardware:** Ultra-fast HEVC encoding at ~2 Mbps average (VBR, up to 4 Mbps peak for complex scenes).
    - **Software:** H.264 at 1 Mbps CBR — slower but compatible with a wider range of players.
- **Multi-directory Support:** Pass multiple target folders as arguments to process them all in one run.
- **Flexible Invocation:** Run from any directory by passing the target folder(s) as arguments, or run directly from within the folder to process.
- **Metadata Preservation:** Uses `ExifTool` to keep "Date Created" and "Date Modified" identical to the original file.
- **Intelligent Logging:** Real-time display of original size, new size, and reduction percentage across a shared global counter.
- **Batch Processing:** Recursively scans directories to process hundreds of videos while maintaining folder structure.

---

## 🛠 Prerequisites

You must have the following tools installed on your Mac:

1. **Python 3.x**
2. **FFmpeg:** For the video processing engine.
3. **ExifTool:** For syncing file system creation dates.

Install via [Homebrew](https://brew.sh/):

```bash
brew install ffmpeg exiftool
```

---

## 📖 How to Use

### Option A — Run from within the target directory

```bash
cd "/path/to/my/videos/" && python3 /path/to/video-compress/video_compress.py
```

### Option B — Pass a single target directory as an argument

```bash
python3 video-compress/video_compress.py "/path/to/my/videos/"
```

### Option C — Pass multiple directories to process them in one run

```bash
python3 video-compress/video_compress.py "/path/to/folder1/" "/path/to/folder2/" "/path/to/folder3/"
```

All videos across the provided folders are counted upfront and share a single global progress counter. A folder header is printed before each directory when multiple paths are given.

### Interactive menus

After launching, the script will ask:

1. **Destination:**
   - `1` — **Overwrite originals** (convert `.mov` to `.mp4` in place and delete the source) ← default
   - `2` — Create copies in a `COMPRESSED_VIDEOS` subfolder
2. **Encoding engine:** Hardware (fast) or Software (slower, wider compatibility).

The quickest way to run with default settings is to type `1` then `1`.

---

## 📊 Comparison: Hardware vs. Software

| Feature | Hardware (hevc_videotoolbox) | Software (libx264) |
|---------|-----------------------------|--------------------|
| Codec | H.265 (HEVC) | H.264 |
| Speed | ⚡ Ultra-Fast | 🐢 Slower |
| CPU Load | Minimal (Mac stays cool) | High (fans may spin) |
| Bitrate mode | VBR ~2 Mbps (up to 4 Mbps) | CBR 1 Mbps |
| Compatibility | Apple devices (tagged `hvc1`) | Universal |
| Best For | Fast exports / large batches | Broad device compatibility |

---

## 📝 Global Configuration

Tweak the constants at the top of `video_compress.py` to suit your needs:

- `HARDWARE_BITRATE`: Average target bitrate for hardware encoding (Default: `2M`)
- `SOFTWARE_BITRATE`: Fixed bitrate for software encoding (Default: `1M`)
- `TARGET_EXTENSION`: File extension to scan for (Default: `.mov`)
- `AUDIO_BITRATE`: Audio track bitrate (Default: `64k`)
