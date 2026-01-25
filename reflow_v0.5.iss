[Setup]
AppName=Reflow Studio
AppVersion=0.5
DefaultDirName={code:GetDefaultDrive}\Reflow-Studio
DefaultGroupName=Reflow Studio
UninstallDisplayIcon={app}\ReflowStudio.exe
Compression=lzma2/ultra64
SolidCompression=yes
OutputDir=D:\New folder\Reflow-Studio\Installer_Output
OutputBaseFilename=Reflow_Studio_v0.5_Setup

[Files]
; The Main Executable and manually packed libraries
Source: "D:\New folder\Reflow-Studio\dist\ReflowStudio_App\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; The Models Folder
Source: "D:\New folder\Reflow-Studio\models\*"; DestDir: "{app}\models"; Flags: ignoreversion recursesubdirs createallsubdirs
; The Install Guide
Source: "D:\New folder\Reflow-Studio\INSTALL_GUIDE.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Reflow Studio"; Filename: "{app}\ReflowStudio.exe"
Name: "{commondesktop}\Reflow Studio"; Filename: "{app}\Run_Reflow_Studio.bat"; IconFilename: "{app}\ReflowStudio.exe"

[Run]
Filename: "{app}\Run_Reflow_Studio.bat"; Description: "{cm:LaunchProgram,Reflow Studio}"; Flags: nowait postinstall skipifsilent

[Code]
// --- OLLAMA CHECK LOGIC ---
procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Check if ollama is in PATH by trying to get version
    if not Exec('cmd.exe', '/c ollama --version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) or (ResultCode <> 0) then
    begin
       if MsgBox('Ollama (Local LLM) was not detected.' + #13#10 + #13#10 + 'Ollama is required for Reflow Studio to process scripts. Would you like to open the download page now?', mbConfirmation, MB_YESNO) = IDYES then
       begin
         ShellExec('open', 'https://ollama.com/download', '', '', SW_SHOWNORMAL, ewNoWait, ResultCode);
       end;
    end;
  end;
end;

// Helper to prioritize D: drive
function GetDefaultDrive(Param: String): String;
begin
  if DirExists('D:\') then
    Result := 'D:\Reflow-Studio'
  else
    Result := ExpandConstant('{pf}\Reflow-Studio');
end;