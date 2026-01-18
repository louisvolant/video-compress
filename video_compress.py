import os
import subprocess
import shutil

# --- GLOBAL CONFIGURATION ---
HARDWARE_CODEC = "h264_videotoolbox"
SOFTWARE_CODEC = "libx264"

HARDWARE_BITRATE = "1.5M"  # Compensate hardware speed with higher bitrate
SOFTWARE_BITRATE = "1M"  # Software is more efficient, can use lower bitrate

AUDIO_BITRATE = "64k"
TARGET_EXTENSION = ".mov"


def compress_video(input_path, output_path, codec, bitrate):
    """
    Compresses video and preserves metadata + file system dates.
    """
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

    if codec == SOFTWARE_CODEC:
        command.insert(-2, "-preset")
        command.insert(-2, "faster")

    try:
        subprocess.run(command, check=True, capture_output=True)

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
        print(f"\n❌ Error on {input_path}: {e.stderr.decode()}")
        return False


def main():
    root_dir = os.getcwd()

    # --- UI MENUS ---
    print("\n--- STEP 1: CHOOSE DESTINATION ---")
    print("1. Create copies in 'COMPRESSED_VIDEOS' folder")
    print("2. OVERWRITE originals (Convert .mov to .mp4 and delete original)")
    mode_choice = input("\nSelect an option (1 or 2): ").strip()

    print("\n--- STEP 2: CHOOSE ENCODING ENGINE ---")
    print(f"1. Hardware ({HARDWARE_CODEC}) -> Fast, {HARDWARE_BITRATE}")
    print(f"2. Software ({SOFTWARE_CODEC}) -> Quality, {SOFTWARE_BITRATE}")
    codec_choice = input("\nSelect an option (1 or 2): ").strip()

    if mode_choice not in ["1", "2"] or codec_choice not in ["1", "2"]:
        print("Invalid choices. Exiting.")
        return

    overwrite_mode = (mode_choice == "2")
    selected_codec = HARDWARE_CODEC if codec_choice == "1" else SOFTWARE_CODEC
    selected_bitrate = HARDWARE_BITRATE if codec_choice == "1" else SOFTWARE_BITRATE
    output_base = os.path.join(root_dir, "COMPRESSED_VIDEOS")

    video_files = [os.path.join(r, f) for r, d, fs in os.walk(root_dir)
                   for f in fs if f.lower().endswith(TARGET_EXTENSION) and "COMPRESSED_VIDEOS" not in r]

    if not video_files:
        print(f"No {TARGET_EXTENSION} files found.")
        return

    print(f"\n🚀 Processing {len(video_files)} videos using {selected_codec}...")

    for i, input_path in enumerate(video_files, 1):
        # 1. Capture original size
        orig_size_bytes = os.path.getsize(input_path)
        orig_size_mb = orig_size_bytes / (1024 * 1024)

        # 2. Determine output path
        if overwrite_mode:
            output_path = os.path.splitext(input_path)[0] + ".mp4"
        else:
            rel_path = os.path.relpath(input_path, root_dir)
            output_path = os.path.join(output_base, rel_path)
            output_path = os.path.splitext(output_path)[0] + ".mp4"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

        print(f"[{i}/{len(video_files)}] Compressing: {os.path.basename(input_path)}...", end="\r")

        # 3. Process
        if compress_video(input_path, output_path, selected_codec, selected_bitrate):
            new_size_bytes = os.path.getsize(output_path)
            new_size_mb = new_size_bytes / (1024 * 1024)
            reduction = (1 - (new_size_bytes / orig_size_bytes)) * 100

            # Updated log line with size comparison and percentage
            print(
                f"[{i}/{len(video_files)}] ✅ {os.path.basename(input_path)}: {orig_size_mb:.1f} MB -> {new_size_mb:.1f} MB (-{reduction:.1f}%)")

            if overwrite_mode and input_path != output_path:
                os.remove(input_path)
        else:
            print(f"[{i}/{len(video_files)}] ❌ Failed: {os.path.basename(input_path)}")

    print(f"\n--- Done! ---")


if __name__ == "__main__":
    main()