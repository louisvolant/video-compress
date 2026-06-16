import os
import sys
import subprocess
import shutil

# --- GLOBAL CONFIGURATION ---
HARDWARE_CODEC = "hevc_videotoolbox"
SOFTWARE_CODEC = "libx264"

HARDWARE_BITRATE = "2M"   # Average target; encoder can burst up to 2x for complex scenes
SOFTWARE_BITRATE = "1M"  # Software is more efficient, can use lower bitrate

AUDIO_BITRATE = "64k"
TARGET_EXTENSION = ".mov"


def compress_video(input_path, output_path, codec, bitrate):
    """
    Compresses video and preserves metadata + file system dates.
    """
    if codec == HARDWARE_CODEC:
        maxrate = str(int(bitrate[:-1]) * 2) + bitrate[-1]  # 2x target as ceiling
        command = [
            "ffmpeg", "-i", input_path,
            "-map_metadata", "0",
            "-c:v", codec,
            "-b:v", bitrate,
            "-maxrate", maxrate,
            "-bufsize", maxrate,
            "-tag:v", "hvc1",
            "-c:a", "aac",
            "-b:a", AUDIO_BITRATE,
            "-ac", "1",
            "-movflags", "+faststart",
            output_path,
            "-y"
        ]
    else:
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


def process_directory(root_dir, overwrite_mode, selected_codec, use_hardware, index_offset, total):
    output_base = os.path.join(root_dir, "COMPRESSED_VIDEOS")

    video_files = [os.path.join(r, f) for r, d, fs in os.walk(root_dir)
                   for f in fs if f.lower().endswith(TARGET_EXTENSION) and "COMPRESSED_VIDEOS" not in r]

    if not video_files:
        print(f"No {TARGET_EXTENSION} files found in: {root_dir}")
        return index_offset

    for i, input_path in enumerate(video_files, index_offset + 1):
        orig_size_bytes = os.path.getsize(input_path)
        orig_size_mb = orig_size_bytes / (1024 * 1024)

        if overwrite_mode:
            output_path = os.path.splitext(input_path)[0] + ".mp4"
        else:
            rel_path = os.path.relpath(input_path, root_dir)
            output_path = os.path.join(output_base, rel_path)
            output_path = os.path.splitext(output_path)[0] + ".mp4"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

        print(f"[{i}/{total}] Compressing: {os.path.basename(input_path)}...", end="\r")

        if compress_video(input_path, output_path, selected_codec,
                          bitrate=HARDWARE_BITRATE if use_hardware else SOFTWARE_BITRATE):
            new_size_bytes = os.path.getsize(output_path)
            new_size_mb = new_size_bytes / (1024 * 1024)
            reduction = (1 - (new_size_bytes / orig_size_bytes)) * 100
            sign = "-" if reduction >= 0 else "+"
            print(f"[{i}/{total}] ✅ {os.path.basename(input_path)}: {orig_size_mb:.1f} MB -> {new_size_mb:.1f} MB ({sign}{abs(reduction):.1f}%)")

            if overwrite_mode and input_path != output_path:
                os.remove(input_path)
        else:
            print(f"[{i}/{total}] ❌ Failed: {os.path.basename(input_path)}")

    return index_offset + len(video_files)


def main():
    if len(sys.argv) > 1:
        root_dirs = []
        for arg in sys.argv[1:]:
            path = os.path.abspath(arg)
            if not os.path.isdir(path):
                print(f"Error: '{path}' is not a valid directory.")
                return
            root_dirs.append(path)
    else:
        root_dirs = [os.getcwd()]

    # --- UI MENUS ---
    print("\n--- STEP 1: CHOOSE DESTINATION ---")
    print("1. OVERWRITE originals (convert .mov to .mp4 and delete original)")
    print("2. Create copies in 'COMPRESSED_VIDEOS' folder")
    mode_choice = input("\nSelect an option (1 or 2): ").strip()

    print("\n--- STEP 2: CHOOSE ENCODING ENGINE ---")
    print(f"1. Hardware ({HARDWARE_CODEC}) -> Fast, ~{HARDWARE_BITRATE} VBR (up to {str(int(HARDWARE_BITRATE[:-1])*2)+HARDWARE_BITRATE[-1]} peak)")
    print(f"2. Software ({SOFTWARE_CODEC}) -> Slower, {SOFTWARE_BITRATE} CBR")
    codec_choice = input("\nSelect an option (1 or 2): ").strip()

    if mode_choice not in ["1", "2"] or codec_choice not in ["1", "2"]:
        print("Invalid choices. Exiting.")
        return

    overwrite_mode = (mode_choice == "1")
    selected_codec = HARDWARE_CODEC if codec_choice == "1" else SOFTWARE_CODEC
    use_hardware = codec_choice == "1"

    all_video_files = [
        f for root_dir in root_dirs
        for r, d, fs in os.walk(root_dir)
        for f in fs if f.lower().endswith(TARGET_EXTENSION) and "COMPRESSED_VIDEOS" not in r
    ]
    total = len(all_video_files)

    if total == 0:
        print(f"No {TARGET_EXTENSION} files found.")
        return

    mode_label = f"~{HARDWARE_BITRATE} VBR" if use_hardware else f"{SOFTWARE_BITRATE} CBR"
    print(f"\n🚀 Processing {total} videos using {selected_codec} ({mode_label})...")

    offset = 0
    for root_dir in root_dirs:
        if len(root_dirs) > 1:
            print(f"\n📁 {os.path.basename(root_dir)}/")
        offset = process_directory(root_dir, overwrite_mode, selected_codec, use_hardware, offset, total)

    print(f"\n--- Done! ---")


if __name__ == "__main__":
    main()