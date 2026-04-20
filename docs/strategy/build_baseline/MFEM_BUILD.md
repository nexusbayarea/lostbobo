# MFEM/SUNDIALS Portable Build Baseline

Build must be performed on **Ubuntu 20.04 (glibc 2.31)** to ensure portability.

## Artifacts
1. sundials.tar.gz
2. mfem.tar.gz
3. glvis.tar.gz

## Build Strategy
1. Build statically/shared with CMAKE_POSITION_INDEPENDENT_CODE=ON.
2. Use 'patchelf --set-rpath '$ORIGIN/../lib'' to ensure dynamic linking resolution.
3. Package only 'lib/' and 'include/' directories.

## Runtime Loading
Use the JIT loader in 'backend/tools/runtime/backends/loader.py' to extract assets to '.simhpc/runtime/'.
