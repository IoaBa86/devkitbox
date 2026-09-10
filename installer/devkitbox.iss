; Inno Setup script for DevKitBox.
;
; Build the PyInstaller dist first, then compile this:
;   .venv\Scripts\pyinstaller installer\devkitbox.spec --noconfirm
;   ISCC installer\devkitbox.iss
;
; Output: installer\output\DevKitBox-Setup-<version>.exe

#define MyAppName "DevKitBox"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "DevKitBox"
#define MyAppURL "https://devkitbox.net"
#define MyAppExeName "DevKitBox.exe"

[Setup]
AppId={{8F3B2C6A-2B2C-4C7A-9D2E-6E6F5B6A6E7B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=..\LICENSE
OutputDir=output
OutputBaseFilename=DevKitBox-Setup-{#MyAppVersion}
SetupIconFile=..\assets\icons\app_icon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
; "unchecked" makes this box start unchecked in the interactive wizard —
; confirmed correct. It does NOT apply to /VERYSILENT runs that omit
; /TASKS: Inno selects all non-exclusive tasks by default there regardless
; of "unchecked" (a documented Inno quirk, confirmed empirically). Anyone
; scripting a silent install who wants no desktop icon must pass
; /TASKS="" (or /TASKS="!desktopicon") explicitly.
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\DevKitBox\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

; No [UninstallDelete] section: DevKitBox writes its SQLite DB and logs
; under %LOCALAPPDATA%\DevKitBox at runtime (see app/core/paths.py), which
; is outside {app} — Inno's automatic uninstall (removing exactly what
; [Files] installed) already leaves that user data untouched, as intended.
