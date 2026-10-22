@echo off
set "MODEL=X:\models\qwen3_coder"
"%~dp0c\coli.cmd" serve --model "%MODEL%" --port 8081 --auto-tier %*
