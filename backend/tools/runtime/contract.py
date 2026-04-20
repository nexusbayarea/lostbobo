import os

CONTRACT = {
    "SOLVERS": {
        "MFEM (Structural)": {"url": os.getenv("SB_SOLVER_MFEM_URL"), "version": "4.6.0"},
        "SUNDIALS (Thermal)": {"url": os.getenv("SB_SOLVER_SUNDIALS_URL"), "version": "6.5.0"},
        "Mercury-Hybrid": {"url": os.getenv("SB_SOLVER_MERCURY_URL"), "version": "1.0.0"}
    },
    "GEOMETRIES": {
        "Heat Sink": {"url": os.getenv("SB_GEO_HEATSINK_URL")},
        "Turbine Blade": {"url": os.getenv("SB_GEO_TURBINE_URL")},
        "Pressure Vessel": {"url": os.getenv("SB_GEO_VESSEL_URL")}
    }
}
