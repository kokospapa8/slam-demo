import os
import subprocess
import sys

def extract_frames(video_path, output_dir, fps=5):
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    frame_pattern = os.path.join(output_dir, f"{base_name}_%04d.png")
    cmd = ["ffmpeg", "-i", video_path, "-vf", f"fps={fps}", frame_pattern]
    subprocess.run(cmd, check=True)

def run_colmap_pipeline(image_dir, output_dir):
    db_path = os.path.join(output_dir, "database.db")
    sparse_dir = os.path.join(output_dir, "sparse")
    dense_dir = os.path.join(output_dir, "dense")

    os.makedirs(sparse_dir, exist_ok=True)
    os.makedirs(dense_dir, exist_ok=True)

    def run_colmap(args):
        subprocess.run(["colmap"] + args, check=True)

    # 1. Feature Extraction
    run_colmap(["feature_extractor", "--database_path", db_path, "--image_path", image_dir])

    # 2. Feature Matching
    run_colmap(["exhaustive_matcher", "--database_path", db_path])

    # 3. Sparse Reconstruction
    run_colmap(["mapper", "--database_path", db_path, "--image_path", image_dir, "--output_path", sparse_dir])

    mapper_output_dir = os.path.join(sparse_dir, "0")

    # 4. Undistort Images
    run_colmap([
        "image_undistorter",
        "--image_path", image_dir,
        "--input_path", mapper_output_dir,
        "--output_path", dense_dir,
        "--output_type", "COLMAP"
    ])

    # 5. Dense Stereo Matching
    run_colmap(["patch_match_stereo", "--workspace_path", dense_dir])

    # 6. Dense Fusion
    run_colmap(["stereo_fusion", "--workspace_path", dense_dir, "--output_path", os.path.join(dense_dir, "fused.ply")])

def main():
    input_folder = sys.argv[1] if len(sys.argv) > 1 else "input"
    colmap_output = "output"
    frame_output = os.path.join(colmap_output, "frames")
    os.makedirs(frame_output, exist_ok=True)

    print("1️⃣ Extracting frames from all MP4 files in", input_folder)
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".mp4"):
            video_path = os.path.join(input_folder, filename)
            extract_frames(video_path, frame_output)

    print("2️⃣ Running COLMAP SLAM pipeline...")
    run_colmap_pipeline(frame_output, colmap_output)

    print("✅ SLAM processing complete. Output saved to:", colmap_output)

if __name__ == "__main__":
    main()
