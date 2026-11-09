"""Simplify a TOSCA triangle mesh using libigl's QEM implementation."""

import argparse
from pathlib import Path

import igl
import numpy as np


def load_mesh(path):
    """Read a TOSCA .vert/.tri pair (one-based faces), or an OFF mesh."""
    if path.suffix.lower() in {".vert", ".tri"}:
        vertices = np.loadtxt(path.with_suffix(".vert"), ndmin=2)
        faces = np.loadtxt(path.with_suffix(".tri"), dtype=np.int64, ndmin=2) - 1
    elif path.suffix.lower() == ".off":
        vertices, faces = igl.read_triangle_mesh(str(path))
    else:
        raise ValueError("Input must be a TOSCA .vert/.tri pair or an .off file.")

    if vertices.ndim != 2 or vertices.shape[1] != 3 or not len(vertices):
        raise ValueError("Vertices must be a non-empty N x 3 array.")
    if faces.ndim != 2 or faces.shape[1] != 3 or not len(faces):
        raise ValueError("Faces must be a non-empty M x 3 array of triangles.")
    if not np.isfinite(vertices).all():
        raise ValueError("Vertex coordinates must be finite.")
    if faces.min() < 0 or faces.max() >= len(vertices):
        raise ValueError("Invalid face index; TOSCA .tri indices must be one-based.")
    if np.any(np.diff(np.sort(faces, axis=1), axis=1) == 0):
        raise ValueError("A triangle cannot repeat a vertex index.")
    if not igl.is_edge_manifold(faces)[0] or not np.all(igl.is_vertex_manifold(faces)):
        raise ValueError("libigl QEM requires a manifold triangle mesh.")
    return vertices, faces


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="TOSCA .vert, .tri, or .off file")
    parser.add_argument("output", type=Path, help="Simplified .off file")
    parser.add_argument("--faces", type=int, required=True, help="Target triangle count")
    args = parser.parse_args()

    if args.output.suffix.lower() != ".off":
        parser.error("Output must have an .off extension.")
    if args.output.resolve() == args.input.resolve():
        parser.error("Input and output must be different files.")

    try:
        vertices, faces = load_mesh(args.input)
        if not 0 < args.faces < len(faces):
            parser.error(f"--faces must be between 1 and {len(faces) - 1}.")

        # QSlim accumulates plane quadrics and contracts edges using quadric error.
        simplified_vertices, simplified_faces, _, _ = igl.qslim(
            vertices, faces, args.faces
        )
        if not len(simplified_faces):
            raise RuntimeError("QEM did not produce a mesh.")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        if not igl.writeOFF(str(args.output), simplified_vertices, simplified_faces):
            raise OSError(f"Could not write {args.output}.")
    except (OSError, ValueError, RuntimeError) as error:
        parser.error(str(error))

    print(
        f"Vertices: {len(vertices)} -> {len(simplified_vertices)}; "
        f"faces: {len(faces)} -> {len(simplified_faces)}; saved {args.output}"
    )
    if len(simplified_faces) > args.faces:
        print("Target face count was not reached; saved the available simplification.")


if __name__ == "__main__":
    main()
