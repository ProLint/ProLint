#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "libgromacs" for configuration "Release"
set_property(TARGET libgromacs APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(libgromacs PROPERTIES
  IMPORTED_LINK_INTERFACE_LIBRARIES_RELEASE "/usr/local/cuda/lib64/libcudart_static.a;-lpthread;dl;/usr/lib/x86_64-linux-gnu/librt.so;/usr/local/cuda/lib64/stubs/libnvidia-ml.so;/home/besian/anaconda3/lib/libz.so;dl;rt;m;gmxfftw;/home/besian/anaconda3/lib/libmkl_intel_lp64.so;/home/besian/anaconda3/lib/libmkl_intel_thread.so;/home/besian/anaconda3/lib/libmkl_core.so;/home/besian/anaconda3/lib/libiomp5.so;/home/besian/anaconda3/lib/libmkl_intel_lp64.so;/home/besian/anaconda3/lib/libmkl_intel_thread.so;/home/besian/anaconda3/lib/libmkl_core.so;/home/besian/anaconda3/lib/libiomp5.so;-lpthread;-lm;-lpthread;-fopenmp"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libgromacs.so.2.4.0"
  IMPORTED_SONAME_RELEASE "libgromacs.so.2"
  )

list(APPEND _IMPORT_CHECK_TARGETS libgromacs )
list(APPEND _IMPORT_CHECK_FILES_FOR_libgromacs "${_IMPORT_PREFIX}/lib/libgromacs.so.2.4.0" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
