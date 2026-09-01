# P14 public input geometries

The two XYZ files are the exact public source-proxy geometries used by the frozen P14 fixed-geometry endpoint. They are reconstructed from the monograph's published five-parameter descriptors; they are not the monograph's unpublished Cartesian coordinates.

- `source_proxy_G.xyz`: ordinary G descriptor geometry;
- `source_proxy_PLG.xyz`: PLG descriptor geometry;
- both use a fixed C-H distance of 1.080 Å because that coordinate was not reported in the source table;
- atom order is C1-C12 followed by H1-H6 and matches the checked-in processed JSON records.

The authoritative machine representation, including full-precision coordinates, is `../processed/p14_C12H6_source_level_fixed_geometry_v0.1.json`.
