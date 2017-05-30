SqlIaaSExtensionDeployer.exe verify
msiexec /qn /i SqlIaaSExtension.msi
REG ADD HKLM\SOFTWARE\Microsoft\SqlIaaSExtension\CurrentVersion /v InstallMode /t REG_DWORD /d 0 /f