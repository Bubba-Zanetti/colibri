@echo off
set "MODEL=C:\models\glm52_i4"
"%~dp0c\coli.cmd" web --model "%MODEL%" --port 8080 --auto-tier %*
