import os
import subprocess
import shutil

# --- DEFAULT CONFIGURATION ---
TARGET_BITRATE = "1M"  # Target video bitrate
AUDIO_BITRATE = "64k"  # Target audio bitrate
TARGET_EXTENSION = ".mov"  # Extension to look for


def compress_video(input_path, output_path, codec, bitrate=TARGET_BITRATE):
    """
    Handles the compression process using FFmpeg and syncs metadata using ExifTool.
    """
    # 1. Build FFmpeg command
    # -map_metadata 0: copies internal tags (GPS, camera model, creation time)
    command = [
        "ffmpeg", "-i", input_path,
        "-map_metadata", "0",
        "-c:v", codec,
        "-b:v", bitrate,
        "-maxrate", bitrate,
        "-bufsize", "2M",
        "-c:a", "aac",
        "-b:a", AUDIO_BITRATE,
        "-ac", "1",
        "-movflags", "+faststart",
        output_path,
        "-y"
    ]

    # Add preset only if using software encoding (libx264)
    if codec == "libx264":
        command.insert(-2, "-preset")
        command.insert(-2, "faster")

    try:
        # Execute compression
        subprocess.run(command, check=True, capture_output=True)

        # 2. Sync File System Dates using ExifTool
        # This copies FileModifyDate and FileCreateDate from source to destination
        if shutil.which("exiftool"):
            subprocess.run([
                "exiftool", "-TagsFromFile", input_path,
                "-FileModifyDate", "-FileCreateDate",
                "-CreationDate", "-CreateDate",
                "-overwrite_original",
                output_path
            ], check=False, capture_output=True)

        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error processing {input_path}: {e.stderr.decode()}")
        return False


def main():
    root_dir = os.getcwd()

    # --- MENU 1: DESTINATION MODE ---
    print("\n--- STEP 1: CHOOSE DESTINATION ---")
    print("1. Create copies in 'COMPRESSED_VIDEOS' folder")
    print("2. OVERWRITE originals (Convert .mov to .mp4 and delete original)")

    mode_choice = input("\nSelect an option (1 or 2): ").strip()
    if mode_choice not in ["1", "2"]:
        print("Invalid choice. Exiting.")
        return

    # --- MENU 2: ENCODING ENGINE ---
    print("\n--- STEP 2: CHOOSE ENCODING ENGINE ---")
    print("1. Hardware (h264_videotoolbox) -> Faster, cooler CPU, standard quality")
    print("2. Software (libx264) -> Slower, hotter CPU, better quality/size ratio")

    codec_choice = input("\nSelect an option (1 or 2): ").strip()
    if codec_choice not in ["1", "2"]:
        print("Invalid choice. Exiting.")
        return

    # Set logic variables
    overwrite_mode = (mode_choice == "2")
    selected_codec = "h264_videotoolbox" if codec_choice == "1" else "libx264"
    output_base = os.path.join(root_dir, "COMPRESSED_VIDEOS")

    # --- FILE DISCOVERY ---
    video_files = []
    for root, dirs, files in os.walk(root_dir):
        if "COMPRESSED_VIDEOS" in root:
            continue
        for file in files:
            if file.lower().endswith(TARGET_EXTENSION):
                video_files.append(os.path.join(root, file))

    if not video_files:
        print(f"No {TARGET_EXTENSION} files found in {root_dir}")
        return

    # Check for ExifTool availability
    if not shutil.which("exiftool"):
        print("⚠️  Warning: 'exiftool' not found. File creation dates will not be synced.")

    print(f"\n🚀 Starting process using {selected_codec}")
    print(f"Processing {len(video_files)} videos...\n")

    for i, input_path in enumerate(video_files, 1):
        # Determine output path
        if overwrite_mode:
            output_path = os.path.splitext(input_path)[0] + ".mp4"
        else:
            rel_path = os.path.relpath(input_path, root_dir)
            output_path = os.path.join(output_base, rel_path)
            output_path = os.path.splitext(output_path)[0] + ".mp4"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

        print(f"[{i}/{len(video_files)}] Compressing: {os.path.basename(input_path)}...", end="\r")

        if compress_video(input_path, output_path, selected_codec):
            new_size = os.path.getsize(output_path) / (1024 * 1024)
            print(f"[{i}/{len(video_files)}] ✅ {os.path.basename(input_path)} -> {new_size:.1f} MB")

            # Delete original if overwrite mode is active
            if overwrite_mode:
                if os.path.exists(output_path) and input_path != output_path:
                    os.remove(input_path)
        else:
            print(f"[{i}/{len(video_files)}] ❌ Failed: {os.path.basename(input_path)}")

    print(f"\n--- Process Finished! ---")


if __name__ == "__main__":
    main()