# Maple Tree Build Spec (from reference measurement)

Source: 参考图片.jpg (1536×687). Trunk zone measured on 2.2x enlargement of
left 42% of frame. All lengths normalized to visible trunk height Ht≈7m.

## Silhouette (view-plane, camera looks +Y)

Measured from extracted mask `renders/maple/ref_branches_silhouette.png`
(luminance+redness threshold, largest connected component).

Trunk centerline (x offset from base center, z up):

| z/Ht | x offset | radius/Ht | note |
|------|----------|-----------|------|
| 0.00 | 0.00     | 0.115     | base, flares into roots — dia 0.23 Ht |
| 0.15 | -0.05    | 0.100     | slight left lean |
| 0.35 | -0.10    | 0.088     | rising left |
| 0.52 | -0.145   | 0.082     | LEFT ELBOW — smooth convex bulge |
| 0.62 | -0.12    | 0.072     | |
| 0.72 | -0.07    | 0.060     | WAIST pinch (waist/base dia ≈ 0.64) |
| 0.82 | -0.02    | 0.072     | fork swells — limbs converge into mass |
| 0.92 | -0.06    | 0.058     | |
| 1.00 | -0.12    | 0.045     | top kinks LEFT into co-leader |

Left edge = one long convex arc base→elbow→top. Right edge concave between
elbow and waist. Fork zone = swollen dark mass, not a clean taper.

## Branch skeleton — FEW and LONG (foliage gives mass, not twigs)

1. **limbR (the signature limb)**: exits trunk right side at z≈0.68Ht,
   base r≈0.05Ht, sweeps RIGHT ~0.45Ht, gentle arc slightly down then up.
   Thickness ~2/3 of trunk radius at that height.
2. **coLeader**: trunk top continues up-LEFT steeply, r≈0.04Ht → exits
   top-left of crown.
3. **limbD**: drooping branch off trunk lower-left/inner at z≈0.45Ht,
   hangs down-left ~0.2Ht.
4. **limbBack**: rear/depth limb at fork zone going back-right.
5. **limbUp**: near-vertical from fork continuing to crown top.

Secondaries: 2-3 per main limb, spaced along length, long (not stubs).

## Surface

- Bark: smooth, near-black dark brown; sunlit faces pick up gold/moss sheen.
- Ridges: shallow longitudinal lobes only (StarSoft), twist ≤60°. NO rope look.
- Moss/lichen patch on upper-left trunk faces + pale rock at base-right.
- NO hollow (dropped per user).

## World placement (existing scene)

Base center ≈ (-4.4, 0, -0.2). Ht≈7.2m, crown top ≈ 9.5m.
