try:
    import open3d as o3d
    HAS_OPEN3D = True
except ImportError:
    HAS_OPEN3D = False
import numpy as np
import trimesh
from .geometry import Mesh

def downsample_mesh(mesh: Mesh, n_points: int) -> Mesh:
    """Downsample a mesh to approximately N vertices using vertex clustering or simple sampling."""
    # trimesh.sample.sample_surface is good for point clouds
    # For a mesh, we can use simplify or just return a point cloud as a Mesh proxy
    points, face_indices = trimesh.sample.sample_surface(mesh._mesh, n_points)
    # Wrap sampled points in a new Trimesh object (as a point cloud)
    pcd_mesh = trimesh.Trimesh(vertices=points)
    return Mesh(pcd_mesh)

def compute_fpfh(mesh: Mesh, radius_normal: float = 0.1, radius_feature: float = 0.25) -> np.ndarray:
    """
    Compute Fast Point Feature Histograms (FPFH) for the given mesh.
    Falls back to a simple vertex-density/curvature proxy if Open3D is missing.
    """
    if HAS_OPEN3D:
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(mesh.vertices)
        pcd.estimate_normals(
            search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=radius_normal, max_nn=30)
        )
        fpfh = o3d.pipelines.registration.compute_fpfh_feature(
            pcd,
            o3d.geometry.KDTreeSearchParamHybrid(radius=radius_feature, max_nn=100)
        )
        return np.asarray(fpfh.data).T
    else:
        # Fallback: simple geometric descriptor (e.g. vertex distance from center + normal proxy)
        vertices = mesh.vertices
        center = np.mean(vertices, axis=0)
        dist = np.linalg.norm(vertices - center, axis=1)
        
        # Simple normal estimate proxy if faces exist
        normals = np.zeros_like(vertices)
        if hasattr(mesh._mesh, 'vertex_normals'):
             normals = mesh._mesh.vertex_normals
             
        # Pad to 33 dimensions: [dist, norm_x, norm_y, norm_z, 0, ...]
        features = np.zeros((len(vertices), 33))
        features[:, 0] = dist
        if normals.shape == vertices.shape:
            features[:, 1:4] = normals
        return features
