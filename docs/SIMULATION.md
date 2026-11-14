# Simulation bench

The editor can run without a model folder from a real machine. The simulated parts are boxes and spheres of random size, drawn from a fixed seed and written to disk as binary STL. Their volume is known in closed form, so the bench can say what every operation must leave true. The real operations of the editor (move, rotate, scale, add, replace, remove, restore, empty the trash, the light copy, the mesh check, the comparison, the GLB for the viewer) run on them, and then the parts are injured the way files get injured.

## Run it

```
python -m pytest -q tests/test_simulation_bench.py
```

## What the scenarios check

| Scenario | What it shows |
|----------|---------------|
| twenty generated parts | closed, without degenerate faces, with the volume they have in closed form |
| ten parts moved and turned at random | the volume and the sizes are kept, the part is still a good mesh, and moving it back gives the volume back |
| a move without a rotation | the box is shifted by exactly the move |
| a scale | the volume changes by the cube and the box by the factor |
| four changes to one part, then its removal | each change leaves the previous version in the trash, the last version comes back and an existing part is never overwritten |
| emptying the trash | only when confirmed, and into an archive |
| names that lead out of the folder | refused by every operation |
| a scale of zero, negative, not a number or too large, a move that is not a number | refused and the part is untouched |
| the light copy at four ratios | it never grows, never leaves the box, loses triangles in step with the ratio, and a ratio of one or more changes nothing |
| the light copy on disk | a new file; the part is not changed |
| a hole, faces turned inside out, a number that is not a number, a repeated face, a flat face, a part in metres, an empty mesh | the check sees each one |
| files cut short at six places, garbage | not a part, never saved over a good one |
| the GLB for the viewer | it carries the triangles of the part and the box of the part |
| the same seed twice, another seed | the same parts, and really different ones |

The workflow named "Simulation bench" runs the bench on every change, so the simulated path has its own visible job.

## What it cannot show

How the editor behaves with the parts of a real model, with real meshes of real machines and real mistakes of real people, needs the model. The status of the repository therefore stays at "simulated" for the hardware row until a person has run the service on the bench.
