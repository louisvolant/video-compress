import os
import subprocess

# --- CONFIGURATION PAR DÉFAUT ---
TARGET_BITRATE = "1M"      # Débit vidéo
AUDIO_BITRATE = "64k"      
EXTENSION_CIBLE = ".mov"
# Changement ici : utilisation du moteur matériel Apple
CODEC_VIDEO = "h264_videotoolbox"    

def compress_video(input_path, output_path, bitrate=TARGET_BITRATE):
    # Note : avec videotoolbox, on enlève "-preset" qui n'est pas reconnu
    command = [
        "ffmpeg", "-i", input_path,
        "-c:v", CODEC_VIDEO,
        "-b:v", bitrate,
        "-maxrate", bitrate,
        "-bufsize", "2M",
        # On peut ajouter '-profile:v', 'main' pour une compatibilité maximale
        "-c:a", "aac",
        "-b:a", AUDIO_BITRATE,
        "-ac", "1",
        "-movflags", "+faststart",
        output_path,
        "-y"
    ]
    try:
        # On retire capture_output=True pour voir la progression FFmpeg si besoin, 
        # ou on le garde pour un log propre.
        subprocess.run(command, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Erreur sur {input_path}: {e.stderr.decode()}")
        return False

def main():
    root_dir = os.getcwd()
    
    print("\n--- CONFIGURATION DE LA COMPRESSION (ACCÉLÉRATION M1/M4) ---")
    print("1. Créer des copies dans le dossier 'COMPRESSED_VIDEOS'")
    print("2. ÉCRASER les originaux (Remplace .mov par .mp4 et supprime le .mov)")
    
    choix = input("\nChoisissez une option (1 ou 2) : ").strip()

    if choix not in ["1", "2"]:
        print("Choix invalide. Fin du script.")
        return

    mode_ecraser = (choix == "2")
    output_base = os.path.join(root_dir, "COMPRESSED_VIDEOS")

    video_files = []
    for root, dirs, files in os.walk(root_dir):
        if "COMPRESSED_VIDEOS" in root:
            continue
        for file in files:
            if file.lower().endswith(EXTENSION_CIBLE):
                video_files.append(os.path.join(root, file))

    if not video_files:
        print(f"Aucun fichier {EXTENSION_CIBLE} trouvé dans {root_dir}")
        return

    print(f"\n🚀 Utilisation de {CODEC_VIDEO} sur Apple Silicon")
    print(f"Traitement de {len(video_files)} vidéos...\n")

    for i, input_path in enumerate(video_files, 1):
        if mode_ecraser:
            output_path = os.path.splitext(input_path)[0] + ".mp4"
        else:
            rel_path = os.path.relpath(input_path, root_dir)
            output_path = os.path.join(output_base, rel_path)
            output_path = os.path.splitext(output_path)[0] + ".mp4"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

        print(f"[{i}/{len(video_files)}] Compression de : {os.path.basename(input_path)}...", end="\r")
        
        if compress_video(input_path, output_path):
            new_size = os.path.getsize(output_path) / (1024*1024)
            print(f"[{i}/{len(video_files)}] ✅ {os.path.basename(input_path)} -> {new_size:.1f} Mo")
            
            if mode_ecraser:
                # Sécurité : on vérifie que le fichier de sortie est différent du nom d'entrée
                # et qu'il existe bien.
                if os.path.exists(output_path) and input_path != output_path:
                    os.remove(input_path)
        else:
            print(f"[{i}/{len(video_files)}] ❌ Échec de la compression pour {os.path.basename(input_path)}")

    print(f"\n--- Terminé ! ---")

if __name__ == "__main__":
    main()