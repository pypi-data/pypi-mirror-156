Python Mu Packager Change Log
=============================

.. marker-start-of-change-log

.. towncrier release notes start

Pup 1.0.0a17 (2022-06-25)
-------------------------

Enhancements
^^^^^^^^^^^^

- ``pup`` can now collect some packaging paramenters -- icon-path, license-path, nice-name, and launch-module -- from the project's wheel metadata (warning: it's very very hackish!). (`#123 <https://github.com/mu-editor/pup/issues/123>`_)
- The tool used to build Linux AppImages is no longer hardcoded to a specific version/URL.
  It defaults to `<https://github.com/AppImage/AppImageKit/releases/download/13/appimagetool-x86_64.AppImage>`_ but can be overridden with the ``PUP_AIT_URL`` environment variable. (`#208 <https://github.com/mu-editor/pup/issues/208>`_)
- Linux AppImage filenames now include the packaged application's version. (`#209 <https://github.com/mu-editor/pup/issues/209>`_)
- Both macOS and Windows packaging now accept PNG files for icons.
  The native formats, respectively, ICNS and ICO, are still supported. (`#211 <https://github.com/mu-editor/pup/issues/211>`_)
- The packaged Python version can now be set with the ``--python-version`` CLI flag
  (if the ``PUP_PBS_URL`` environment variable is set, it takes precedence, however). (`#214 <https://github.com/mu-editor/pup/issues/214>`_)


Bug Fixes
^^^^^^^^^

- HTTP downloads now follow redirects. (`#225 <https://github.com/mu-editor/pup/issues/225>`_)


Other Changes
^^^^^^^^^^^^^

- The wheel generated during the metadata colletion stage
  is now kept under the build directory
  and used by the installation stage. (`#30 <https://github.com/mu-editor/pup/issues/30>`_)
- Updated direct ``pup`` dependencies. (`#220 <https://github.com/mu-editor/pup/issues/220>`_)


Pup 1.0.0a16 (2022-05-11)
-------------------------

Enhancements
^^^^^^^^^^^^

- Added support for Python 3.9 and 3.10, linking to the most recent Python Build Standalone release that works effortlessly.
  Also updated the Python Build Standalone releases for Python 3.8. (`#202 <https://github.com/mu-editor/pup/issues/202>`_)


Bug Fixes
^^^^^^^^^

- Fixed Linux AppDir packaging under Docker containers. (`#201 <https://github.com/mu-editor/pup/issues/201>`_)


Pup 1.0.0a15 (2022-03-21)
-------------------------

Bug Fixes
^^^^^^^^^

- Packaged applications are now launched with the ``-I`` Python CLI flag.
  This isolates them from the users' site packages directory and environment.
  Can be overridden with the new ``--launch-pyflag`` packaging option. (`#195 <https://github.com/mu-editor/pup/issues/195>`_)


Pup 1.0.0a14 (2021-11-02)
-------------------------

Bug Fixes
^^^^^^^^^

- Bundle Linux AppImage template with pup,
  otherwise packaging fails. (`#190 <https://github.com/mu-editor/pup/issues/190>`_)



Pup 1.0.0a13 (2021-11-01)
-------------------------

Enhancements
^^^^^^^^^^^^

- Preliminary support for x86-64 Linux AppImage packaging:
  requires ``--icon-path`` with a PNG image and,
  for now,
  sets the category to "Education" in the bundled ``.desktop`` file. (`#150 <https://github.com/mu-editor/pup/issues/150>`_)


Bug Fixes
^^^^^^^^^

- Packaging directly from PyPI now works.
  Up until now,
  the code wrongly took the source project to be
  a ``pip``-installable project on the filesystem. (`#137 <https://github.com/mu-editor/pup/issues/137>`_)
- The macOS binary launcher introduced in release 1.0.0a11
  failed on Apple Silicon systems.
  Now fixed. (`#185 <https://github.com/mu-editor/pup/issues/185>`_)


Pup 1.0.0a12 (2021-10-05)
-------------------------

Bug Fixes
^^^^^^^^^

- With the new binary launcher in release 1.0.0a11,
  macOS packaged applications are no longer backwards compatible:
  applications packaged in 10.15 do not launch on 10.14, for example.
  This is an attempt at fixing that. (`#177 <https://github.com/mu-editor/pup/issues/177>`_)


Pup 1.0.0a11 (2021-10-03)
-------------------------

Enhancements
^^^^^^^^^^^^

- The Windows MSI installer UI now includes auto-generated bitmaps
  displaying the packaged application icon. (`#103 <https://github.com/mu-editor/pup/issues/103>`_)
- The Windows MSI installation process
  can now launch the installed program when done.
  Limitation:
  only works if a license is included to be displayed and accepted,
  which serves the near-term use case for Mu Editor. (`#145 <https://github.com/mu-editor/pup/issues/145>`_)
- Documented how to attain Windows MSI per-machine installs. (`#151 <https://github.com/mu-editor/pup/issues/151>`_)
- macOS launcher is now a native executable, compiled at packaging time.
  This leads to a cleaner user experience when macOS asks if the application should be allowed to access files or other HW devices: with the previous bash-script based solution the user would be asked about ``/bin/bash``. Users are now asked about the proper application name.

  Additionally, the main menu should now display the correct application name, instead of ``pythonX.Y`` as before. (`#153 <https://github.com/mu-editor/pup/issues/153>`_)


Other Changes
^^^^^^^^^^^^^

- Windows MSI installation now adds a single top-level entry to the Start Menu,
  whereas before a directory containing the program launching entry was created:
  less is more. (`#147 <https://github.com/mu-editor/pup/issues/147>`_)
- Documented Windows MSI limitations regarding non-final PEP-440 versions,
  like ``1.1.0b2`` or ``1.1.0rc1``,
  and the implications it has on the end-user software upgrade process. (`#155 <https://github.com/mu-editor/pup/issues/155>`_)
- Updated the default Python Standalone 3.8 bundle from 3.8.5 to 3.8.11. (`#169 <https://github.com/mu-editor/pup/issues/169>`_)


Pup 1.0.0a10 (2021-07-04)
-------------------------

Bug Fixes
^^^^^^^^^

- Fixed macOS signing of bundled files to support Mu Editor 1.0.0b5 that ships Python wheels within a ZIP file. The signing process now recurses into both wheel and ZIP files. (`#156 <https://github.com/mu-editor/pup/issues/156>`_)


Other Changes
^^^^^^^^^^^^^

- macOS sign and notarize code cleanup: no need to reinvent ``shutil.which``. (`#141 <https://github.com/mu-editor/pup/issues/141>`_)


Pup 1.0.0a9 (2021-02-06)
------------------------

Enhancements
^^^^^^^^^^^^

- On macOS,
  ``pup`` now signs shared libraries
  bundled in wheel files
  that the application itself bundles,
  as is the case of the Mu Editor
  -- this is required for notarization. (`#140 <https://github.com/mu-editor/pup/issues/140>`_)


Bug Fixes
^^^^^^^^^

- An ``entitlements.plist`` file,
  required for the macOS signing process,
  is now bundled.
  Previous versions unintentionally failed to do that,
  preventing the successful signature
  and subsequent notarization
  of packaged applications on macOS. (`#138 <https://github.com/mu-editor/pup/issues/138>`_)


Pup 1.0.0a8 (2021-01-24)
------------------------

Enhancements
^^^^^^^^^^^^

- The Python Build Standalone package to be used can now be overridden via the ``PUP_PBS_URL`` environment variable -- for now this is a stop gap capability to support packaging 32-bit Windows applications using, for example, `<https://github.com/indygreg/python-build-standalone/releases/download/20200822/cpython-3.7.9-i686-pc-windows-msvc-shared-pgo-20200823T0159.tar.zst>`_. (`#125 <https://github.com/mu-editor/pup/issues/125>`_)


Bug Fixes
^^^^^^^^^

- macOS packaged applications failed running ``tkinter`` and ``turtle`` code when such code was running under a virtual environment -- much like what Mu Editor does. Now fixed. (`#122 <https://github.com/mu-editor/pup/issues/122>`_)
- macOS DMG creation failed when ``pup`` was installed into a virtual environment but invoked without activating it. Now fixed. (`#125 <https://github.com/mu-editor/pup/issues/125>`_)


Other Changes
^^^^^^^^^^^^^

- Changed the packaging sequence. (`#128 <https://github.com/mu-editor/pup/issues/128>`_)


Pup 1.0.0a7 (2021-01-10)
------------------------

Bug Fixes
^^^^^^^^^

- PyPI distributed ``pup`` failed miserably because it did not include all of its own bundled templates -- now fixed. (`#118 <https://github.com/mu-editor/pup/issues/118>`_)


Pup 1.0.0a6 (2021-01-06)
------------------------

Enhancements
^^^^^^^^^^^^

- The new ``--nice-name`` packaging option overrides the default application name,
  extracted from the distribution's metadata,
  with a more user-friendly name. (`#41 <https://github.com/mu-editor/pup/issues/41>`_)
- The packaging process can now use custom icons via the ``--icon-path`` option.
  Custom icons are used on macOS application bundles and DMG files,
  as well as on the Windows Start Menu and *Program and Features* entries. (`#90 <https://github.com/mu-editor/pup/issues/90>`_)
- An optional license agreement can now be provided with the ``--license-path`` option.
  It must be an ASCII-encoded text file that will be displayed to end-users,
  requiring their agreement before the installation can proceed. (`#91 <https://github.com/mu-editor/pup/issues/91>`_)
- The Windows packaging process
  can now sign the packaged binary ``.exe.``, ``.dll``, and ``.pyd`` files,
  as well as the final MSI file. (`#97 <https://github.com/mu-editor/pup/issues/97>`_)
- Updated the documentation and added a few entries to the "thanks" list. (`#108 <https://github.com/mu-editor/pup/issues/108>`_)


Bug Fixes
^^^^^^^^^

- Fixed a bug that prevented packaging non-signed Windows applications. (`#101 <https://github.com/mu-editor/pup/issues/101>`_)
- Fixed a bug that prevented macOS signing and notarization with the ``--nice-name`` option. (`#111 <https://github.com/mu-editor/pup/issues/111>`_)


Other Changes
^^^^^^^^^^^^^

- Updated versions of direct dependencies. (`#109 <https://github.com/mu-editor/pup/issues/109>`_)


Pup 1.0.0a5 (2020-12-08)
------------------------

Enhancements
^^^^^^^^^^^^

- Minmally usable macOS DMG files are now produced:
  no icons,
  no customization yet. (`#66 <https://github.com/mu-editor/pup/issues/66>`_)
- Minimally usable Windows MSI files are now produced.
  They are user-installable,
  do not include a GUI,
  and add a single Start Menu entry,
  for now,
  with no custom icon.
  Its implementation depends on the `WiX toolset <https://wixtoolset.org>`_,
  which is automatically downloaded and cached for subsequent usage. (`#82 <https://github.com/mu-editor/pup/issues/82>`_)
- Updated the documentation to reflect the new capabilities. (`#94 <https://github.com/mu-editor/pup/issues/94>`_)


Bug Fixes
^^^^^^^^^

- Running the Windows ``.vbs`` launcher from a directory other than the one containing it,
  in a CLI,
  no longer fails. (`#48 <https://github.com/mu-editor/pup/issues/48>`_)


Other Changes
^^^^^^^^^^^^^

- Updated PyPI classifiers: no longer planning but in alpha.
  For now we only support Python 3.7 and 3.8. (`#81 <https://github.com/mu-editor/pup/issues/81>`_)
- Some third party direct dependency versions were updated. (`#89 <https://github.com/mu-editor/pup/issues/89>`_)


Pup 1.0.0a4 (2020-11-18)
------------------------

Bug Fixes
^^^^^^^^^

- Fixed `pup` packaging so that the required cookiecutter templates are bundled. (`#77 <https://github.com/mu-editor/pup/issues/77>`_)


Pup 1.0.0a3 (2020-10-18)
------------------------

Enhancements
^^^^^^^^^^^^

- Resulting macOS application bundles are now signed and notarized.
  (`#43 <https://github.com/mu-editor/pup/issues/43>`_)
- Distributable artifacts now smaller.
  Many unneeded files and directory removed during the packaging process.
  (`#38 <https://github.com/mu-editor/pup/issues/38>`_)
- Subprocess output,
  like ``pip``'s,
  is now tracked and logged live.
  (`#32 <https://github.com/mu-editor/pup/issues/32>`_)

Bug Fixes
^^^^^^^^^

- macOS application bundles with names containing spaces now launch.
  (`#44 <https://github.com/mu-editor/pup/issues/44>`_)


Other Changes
^^^^^^^^^^^^^

- Renamed ``pup`` to *Pluggable Micro Packager*.
  (`#71 <https://github.com/mu-editor/pup/issues/71>`_)
- Added minimal usage documentation.
  (`#70 <https://github.com/mu-editor/pup/issues/70>`_)
- Updated development documentation.
  (`#68 <https://github.com/mu-editor/pup/issues/68>`_)
- Simpler log format when output is a TTY: no timestamps and no logger name.
  (`#52 <https://github.com/mu-editor/pup/issues/52>`_)
- Changed the default logging level to INFO.
  (`#58 <https://github.com/mu-editor/pup/issues/58>`_)
- Now logs exception tracebacks at CRITICAL level.
  (`#51 <https://github.com/mu-editor/pup/issues/51>`_)


Pup 1.0.0a2 (2020-09-16)
------------------------

- First release that actually does something.
  Minimal packaging to a relocatable directory works
  and includes a GUI clickable "thing" to launch the application --
  on macOS and Windows,
  for Python 3.7 and 3.8
  (`#34 <https://github.com/mu-editor/pup/issues/34>`_).



Pup 1.0.0a1 (2020-08-04)
------------------------

- ``pup`` exists as a CLI tool, is ``pip``-installable, and returns 42.

