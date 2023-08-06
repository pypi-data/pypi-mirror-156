<h1 align="center">
<img src="https://raw.githubusercontent.com/TTitscher/bola/main/logo/bola.svg" width="300">
</h1><br>

Collection of sphere packing and meshing algorithms.

# Installation

~~~sh
pip3 install bola
~~~

The `c++` code requires the math library [`Eigen3`](https://eigen.tuxfamily.org) to be installed and a dependency of the python [`gmsh`](https://pypi.org/project/gmsh/) package is `libglu`. So, you may need to run (debian/ubuntu-based):

~~~sh
sudo apt update
sudo apt -y install libeigen3-dev libglu1
~~~

Alternatively, you can follow the steps of the [CI](./.github/workflows/ci.yml#L21-L35).

# Examples

Particle size according to `bola.psd.GradingCurve` (sieve lines):
~~~py
gc = bola.psd.GradingCurves.fuller(d_min=4., d_max=16)
box = (32.0, 32.0, 32.0)
radii = psd.sample_grading_curve(gc, V=0.5 * np.prod(box))
~~~
<h1 align="center">
<img src="https://raw.githubusercontent.com/TTitscher/bola/main/examples/gc.jpg" width="300">
</h1><br>

Initial packing using `bola.packing.rsa` (random sequential addition)
~~~py
spheres = bola.packing.rsa(radii, box)
~~~
<h1 align="center">
<img src="https://raw.githubusercontent.com/TTitscher/bola/main/examples/rsa.jpg" width="300">
</h1><br>

Maximize particle distance using `bola.packing.edmd` (event-driven molecular-dynamics)
~~~py
sim = bola.packing.edmd(box, spheres, growth_rate=0.1)
while sim.t() < 10.0:
    sim.process(100 * len(radii))
    sim.synchronize(True)
    print(packing.stats_string(sim))
distant_spheres = sim.spheres()
distant_spheres[:, 3] = radii # new centers, old radii
~~~
<h1 align="center">
<img src="https://raw.githubusercontent.com/TTitscher/bola/main/examples/edmd.jpg" width="300">
</h1><br>

Mesh via gmsh using `bola.mesh`
~~~py
bola.mesh.create(
    box, new_spheres, bola.mesh.GmshOptions(
        mesh_size_matrix=2.0, mesh_size_aggregates=2.0, out="mesh.xdmf")
)
~~~
<h1 align="center">
<img src="https://raw.githubusercontent.com/TTitscher/bola/main/examples/mesh.jpg" width="300">
</h1><br>

