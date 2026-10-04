@echo off
title Disk maintenance and cache cleanup

echo ===========================================================
echo System maintenance: cleaning up the caches and trash
echo ===========================================================
echo.

echo [1/5] Emptying the recycle bin...
REM Emptying the recycle bin.
REM NOTE: I am using SilentlyContinue because we don't need to have a confirmation for this.
PowerShell -NoProfile -Command "Clear-RecycleBin" -Force -ErrorAction SilentlyContinue
echo.

echo [2/5] Purging all the PIP caches...
REM Clearing out all the pip caches
pip cache purge
echo.

echo [3/5] Purging all the UV caches...
REM Clearing out all the uv caches
uv cache clean
echo.

echo [4/5] Purging all the Poetry caches...
REM Clearing out all the poetry caches
REM I am adding -n which means no-interaction, so that the script doesn't hang asking "Are you sure?"
poetry cache clear pypi --all -n
echo.

echo [5/5] Purging all the NPM caches...
REM Clearing out all the npm caches
npm cache clean --force
echo.

echo ===========================================================
echo Disk cleanup done.
echo ===========================================================
echo.

pause
