import open3d as o3d
import numpy as np
import struct
import os

def read_cameras_bin(path):
    cameras = {}
    with open(path, "rb") as f:
        while True:
            data = f.read(24)
            if not data:
                break
            camera_id, model_id, width, height = struct.unpack("<iiii", data[:16])
            num_params = {0: 3, 1: 4, 2: 4, 3: 5, 4: 8}.get(model_id, 4)
            params = struct.unpack("<" + "d" * num_params, f.read(8 * num_params))
            cameras[camera_id] = {
                "model_id": model_id,
                "width": width,
                "height": height,
                "params": params
            }
    return cameras

def read_images_bin(path):
    images = {}
    with open(path, "rb") as f:
        while True:
            header = f.read(64)
            if not header or len(header) < 64:
                break
            image_id, qw, qx, qy, qz, tx, ty, tz, cam_id = struct.unpack("<idddddddi", header)
            R = quat_to_rot_matrix(np.array([qw, qx, qy, qz]))
            t = np.array([tx, ty, tz]).reshape((3, 1))
            pose = np.hstack((R, t))
            name = b""
            while True:
                c = f.read(1)
                if c == b"\n":
                    break
                name += c
            num_points2D = struct.unpack("<Q", f.read(8))[0]
            f.read(num_points2D * 2 * 8)  # Skip 2D points
            images[image_id] = {"pose": pose, "cam_id": cam_id, "name": name.decode()}
    return images

def quat_to_rot_matrix(q):
    w, x, y, z = q
    return np.array([
        [1 - 2*y*y - 2*z*z, 2*x*y - 2*z*w,     2*x*z + 2*y*w],
        [2*x*y + 2*z*w,     1 - 2*x*x - 2*z*z, 2*y*z - 2*x*w],
        [2*x*z - 2*y*w,     2*y*z + 2*x*w,     1 - 2*x*x - 2*y*y]
    ])

def create_camera_frustum(pose, scale=0.5):
    frustum = np.array([
        [0, 0, 0],
        [1, 1, 2],
        [-1, 1, 2],
        [-1, -1, 2],
        [1, -1, 2]
    ]) * scale
    world_frustum = (pose[:3, :3] @ frustum.T + pose[:3, 3:4]).T
    lines = [[0,1],[0,2],[0,3],[0,4],[1,2],[2,3],[3,4],[4,1]]
    colors = [[1, 0, 0] for _ in lines]
    frustum_obj = o3d.geometry.LineSet()
    frustum_obj.points = o3d.utility.Vector3dVector(world_frustum)
    frustum_obj.lines = o3d.utility.Vector2iVector(lines)
    frustum_obj.colors = o3d.utility.Vector3dVector(colors)
    return frustum_obj

def main():
    base_dir = "output2"
    dense_path = os.path.join(base_dir, "dense/fused.ply")
    image_dir = os.path.join(base_dir, "frames")  # where frame_0001.png, etc. are
    colmap_sparse = os.path.join(base_dir, "sparse/1")

    print("Loading point cloud...")
    pcd = o3d.io.read_point_cloud(dense_path)

    print("Loading COLMAP poses...")
    images = read_images_bin(os.path.join(colmap_sparse, "images.bin"))
    cameras = read_cameras_bin(os.path.join(colmap_sparse, "cameras.bin"))

    print(f"Loaded {len(images)} images")

    # Collect geometries to show
    geometries = [pcd]
    for img in images.values():
        pose = img["pose"]
        geometries.append(create_camera_frustum(pose))

    print("Launching visualizer...")
    o3d.visualization.draw_geometries(geometries,
        window_name="Dense Point Cloud + Camera Poses",
        point_show_normal=False,
        mesh_show_wireframe=False,
        mesh_show_back_face=True
    )

if __name__ == "__main__":
    main()