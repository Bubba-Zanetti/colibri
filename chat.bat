@echo off
set "MODEL=C:\models\glm52_i4"
"%~dp0c\coli.cmd" chat --model "%MODEL%" --auto-tier %*
