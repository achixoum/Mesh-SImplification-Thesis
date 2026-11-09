# Mesh Simplification Thesis

Small Python driver for simplifying TOSCA meshes with Quadric Error Metrics
(QEM), based on Garland and Heckbert's
[Surface Simplification Using Quadric Error Metrics (1997)](https://www.cs.cmu.edu/~garland/Papers/quadrics.pdf).

The implementation is [libigl's `igl.qslim`](https://github.com/libigl/libigl/blob/v2.6.0/include/igl/qslim.cpp),
accessed through its Python bindings to C++. It uses a manifold, edge-collapse
variant of QEM, including area-weighted plane quadrics. The paper's optional
contractions between disconnected vertices are not implemented by this backend.

Use Python 3.10 or newer:

```bash
python -m pip install -r requirements.txt
python main.py data/tosca/cat0.vert output/cat0_qem.off --faces 1000
```

Extract the TOSCA ASCII dataset locally first. Keep `cat0.vert` (XYZ coordinates)
and `cat0.tri` (one-based triangle indices) together; passing either filename loads
both. An existing `.off` mesh is also accepted. `--faces` is the desired number
of output triangles; the actual count is printed and can differ if no further
valid collapses are possible or a collapse removes multiple faces. The result
is saved as an `.off` mesh. Simplification changes vertex indexing and TOSCA's
original vertex correspondences are not preserved.
