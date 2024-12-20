#define MyAppName "VT2"
#define MyAppVersion "1.0"
#define MyAppPublisher "NxVx Inc"
#define MyAppURL "https://quizzsite.pythonanywhere.com"
#define MyAppExeName "ui.exe"
#define MyAppAssocName MyAppName + " File"
#define MyAppAssocExt ".txt"
#define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt

[Setup]
AppId={{A54C814B-F2EF-4BBB-A729-9EE469BE395A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableDirPage=no
DisableProgramGroupPage=no
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
ChangesAssociations=yes
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=C:\Users\Trash\VT2\license.txt
PrivilegesRequired=admin
OutputBaseFilename=vt-installer
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Components]
Name: "plbasic"; Description: "Installs Basic VT Plugin"; Types: full compact custom
Name: "plopensave"; Description: "Installs OpenSave VT Plugin"; Types: full custom
Name: "plopendir"; Description: "Installs OpenDir VT Plugin"; Types: full custom

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:\Users\Trash\VT2\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Trash\Documents\VT2\Plugins\Basic\*"; DestDir: "{userdocs}\VT2\Plugins\Basic"; Components: plbasic; Flags: ignoreversion recursesubdirs
Source: "C:\Users\Trash\Documents\VT2\Plugins\OpenSave\*"; DestDir: "{userdocs}\VT2\Plugins\OpenSave"; Components: plopensave; Flags: ignoreversion recursesubdirs
Source: "C:\Users\Trash\Documents\VT2\Plugins\OpenDir\*"; DestDir: "{userdocs}\VT2\Plugins\OpenDir"; Components: plopendir; Flags: ignoreversion recursesubdirs
Source: "C:\Users\Trash\VT2\dist\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs
Source: "C:\Users\Trash\VT2\dist\ui\*"; DestDir: "{app}\ui"; Flags: ignoreversion recursesubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Registry]
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocExt}\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppAssocKey}"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocName}"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".myp"; ValueData: ""

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

