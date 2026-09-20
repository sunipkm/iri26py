# SPDX-FileCopyrightText: 2023 Sunip K. Mukherjee
#
# SPDX-License-Identifier: Apache-2.0

project('iri26py', 'c',
  version: run_command(
    [
      find_program('python3', 'python', required: true), 
      '-m', 
      'setuptools_scm',
    ],
    check: true
  ).stdout().strip(),
  license: 'BSD-3',
  meson_version: '>=0.64.0',
  default_options : ['warning_level=2'],
)

add_languages('fortran')

fs = import('fs')
fc = meson.get_compiler('fortran')

# On Windows with MinGW gfortran, extension modules can fail to import if
# libgfortran/libgcc runtime DLLs are not on PATH. Link these runtimes
# statically into the .pyd to avoid external DLL lookup at import time.
win_static_runtime_link_args = []
if host_machine.system() == 'windows' and fc.get_id() == 'gcc'
  foreach arg : ['-static-libgfortran', '-static-libgcc', '-static-libquadmath']
    if fc.has_link_argument(arg)
      win_static_runtime_link_args += [arg]
    endif
  endforeach
endif

py_mod = import('python')
py = py_mod.find_installation(pure: false)
py_dep = py.dependency()

install_dir = join_paths(py.get_install_dir(), 'iri26py')

if host_machine.system() == 'windows' and fc.get_id() == 'gcc'
  # Bundle MinGW runtime DLLs into the wheel so the extension can be
  # imported without requiring compiler runtime directories on PATH.
  runtime_dll_names = [
    'libgfortran-5.dll',
    'libquadmath-0.dll',
    'libgcc_s_seh-1.dll',
    'libwinpthread-1.dll',
  ]
  found_runtime_dll_names = []

  gfortran_prog = find_program(
    [
      'gfortran',
      'x86_64-w64-mingw32-gfortran',
      'x86_64-w64-mingw32ucrt-gfortran',
      'x86_64-w64-mingw32-clang-gfortran',
    ],
    required : false,
  )
  if gfortran_prog.found()
    gfortran_bin_dir = run_command(py,
      [
        '-c',
        'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve().parent)',
        gfortran_prog.full_path(),
      ],
      check : true
    ).stdout().strip()

    foreach dll_name : runtime_dll_names
      dll_path = join_paths(gfortran_bin_dir, dll_name)
      if fs.is_file(dll_path)
        install_data(dll_path, install_dir : install_dir)
        found_runtime_dll_names += [dll_name]
      endif
    endforeach
  endif

  # Fallback for some toolchains where gfortran executable name/path differs.
  fallback_runtime_dll_paths = run_command(py,
    [
      '-c',
      'import os, pathlib; names = ["libgfortran-5.dll", "libquadmath-0.dll", "libgcc_s_seh-1.dll", "libwinpthread-1.dll"]; found = []; path_dirs = [pathlib.Path(p) for p in os.environ.get("PATH", "").split(os.pathsep) if p];\nfor name in names:\n  p = next((d / name for d in path_dirs if (d / name).is_file()), None)\n  if p is not None: found.append(str(p))\nprint("\\n".join(found))',
    ],
    check : false
  ).stdout().strip().split('\n')

  foreach dll_path : fallback_runtime_dll_paths
    if dll_path != '' and fs.is_file(dll_path)
      dll_name = run_command(py,
        [
          '-c',
          'import os, sys; print(os.path.basename(sys.argv[1]))',
          dll_path,
        ],
        check : true
      ).stdout().strip()
      if runtime_dll_names.contains(dll_name) and not found_runtime_dll_names.contains(dll_name)
        install_data(dll_path, install_dir : install_dir)
        found_runtime_dll_names += [dll_name]
      endif
    endif
  endforeach

  if found_runtime_dll_names.length() != runtime_dll_names.length()
    missing_runtime_dll_names = []
    foreach dll_name : runtime_dll_names
      if not found_runtime_dll_names.contains(dll_name)
        missing_runtime_dll_names += [dll_name]
      endif
    endforeach
    error('Missing required MinGW runtime DLL(s) for Windows wheel: ' + missing_runtime_dll_names.join(', ') + '. Ensure the MinGW gfortran bin directory is on PATH.')
  endif
endif

fortran_srcs = [
  'src/IRI2026/dfp.f90',
  'src/IRI2026/cira.f',
  'src/IRI2026/igrf.f',
  'src/IRI2026/iridreg.f',
  'src/IRI2026/iriflip.f',
  'src/IRI2026/irifun.f',
  'src/IRI2026/irisub.f',
  'src/IRI2026/iritec.f',
  'src/IRI2026/rocdrift.f',
]

py.install_sources(
    'src/iri26py/__init__.py',
    'src/iri26py/base.py',
    'src/iri26py/download.py',
    'src/iri26py/settings.py',
    'src/iri26py/utils.py',
    subdir: 'iri26py',
    pure: false,
)

install_subdir(
    'src/IRI2026/data',
    install_dir: install_dir,
    strip_directory: false,
)

iri26_static = static_library('iri26',
  fortran_srcs,
  fortran_args : ['-cpp', '-march=native', '-ffast-math', '-std=legacy'],
  install : false,
)

incdir_numpy = run_command(py,
  [
    '-c',
    'import numpy; print(numpy.get_include())'
  ],
  check: true
).stdout().strip()

incdir_f2py = run_command(py,
    ['-c', 'import numpy.f2py; print(numpy.f2py.get_include())'],
    check : true
).stdout().strip()

fortshim_srcs = [
  'src/IRI2026/irishim.f90',
]

fortshim_tgt = custom_target('iri26shimmodule.c',
  input : fortshim_srcs,
  output : ['iri26shimmodule.c', 'iri26shim-f2pywrappers.f'],
  command : [py, '-m', 'numpy.f2py', '@INPUT@', '-m', 'iri26shim', '--lower']
)

inc_np = include_directories(incdir_numpy, incdir_f2py)

py.extension_module('iri26shim',
  fortshim_srcs + [fortshim_tgt],
  incdir_f2py / 'fortranobject.c',
  include_directories: inc_np,
  dependencies : py_dep,
  link_with: [iri26_static],
  install : true,
  install_dir: install_dir
)