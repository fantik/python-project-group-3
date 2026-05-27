@ECHO OFF

set LC_ALL=en_US.UTF-8
set LANG=en_US.UTF-8
set SPHINXBUILD=uv run --group docs sphinx-build
set SOURCEDIR=source
set BUILDDIR=build

if "%1" == "" goto help

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR%
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR%

:end
