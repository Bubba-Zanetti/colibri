@echo off
rem Qwen3.8-27B (GSQ-RCO IQ3_S + MTP) on the RTX 4090 via LM Studio.
rem OpenAI-compatible API: http://localhost:1234/v1   model: qwen-coder
set "LMS=%USERPROFILE%\.lmstudio\bin\lms.exe"
"%LMS%" unload --all >nul 2>&1
"%LMS%" load qwen3.8-27b-gsq-rco --gpu max -c 65536 --speculative-draft-mtp --identifier qwen-coder -y || goto :fail
"%LMS%" server start --port 1234 || goto :fail
echo.
echo Ready: http://localhost:1234/v1  (model "qwen-coder")
echo Run "%LMS%" unload --all to free the GPU.
pause
exit /b 0
:fail
echo Failed to start. Is another app (ComfyUI, colibri) using the GPU?
pause
exit /b 1
