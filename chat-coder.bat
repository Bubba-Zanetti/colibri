@echo off
set "MODEL=X:\models\qwen3_coder"
"%~dp0c\coli.cmd" chat --model "%MODEL%" --auto-tier %*
