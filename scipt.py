#NoTrayIcon
#NoEnv
#Persistent
#SingleInstance Force
SetBatchLines -1
SetKeyDelay -1
SetMouseDelay -1
SetDefaultMouseSpeed 0
SetWinDelay -1
SetControlDelay -1
SendMode Input
CoordMode Pixel, Screen

; ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TriggerKey       := "{key_hold}"
TriggerKey2      := "{key_hold2}"
ShootKey         := "{shoot_key}"
isRestart := ZBIKBIR123
play_start_sound := true

Hotkey, {key_toggle}, ToggleHoldMode
Hotkey, {key_spray}, SprayMode
Hotkey, {key_crouch}, CrouchMode
Hotkey, {key_pause}, PauseMode
Hotkey, {key_exit}, ExitScript

HoldMode        := True
Paused          := False
Color            := {color_value}
Variation        := 2

MonitorIndex     := {monitor_index}
SysGet, Mon, Monitor, %MonitorIndex%

MinClickDelay    := 0
MaxClickDelay    := 1
ExtraSleepAfter  := 0
RandomExtraSleep := false

BoxSize          := 25
ScanLeft         := MonLeft + (MonRight - MonLeft)//2 - BoxSize
ScanRight        := MonLeft + (MonRight - MonLeft)//2 + BoxSize
ScanTop          := MonTop + (MonBottom - MonTop)// 2 - BoxSize - 10
ScanBottom       := MonTop + (MonBottom - MonTop)//2 + BoxSize + 5

ShowScanBox      := {ShowScanBox}
ScanBoxColor     := "{ScanBoxColor}"
ScanBoxThickness := {ScanBoxThickness}

PlaySounds       := {PlaySounds}
; ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if (isRestart) {
    if (PlaySounds) {
        SoundBeep 300, 700
    }
    ToolTip Set fire key to: "%ShootKey%", 0, 0
    SetTimer RemoveTT, -3000
    play_start_sound := false
}

Menu Tray, NoStandard
Menu Tray, Add, Restart Script, Restart
Menu Tray, Add, Exit, ExitScript

if (PlaySounds and play_start_sound) {
SoundBeep, 200, 200
SoundBeep, 300, 200
SoundBeep, 400, 200
}
ShowScanOverlay()

SetTimer CheckTrigger, 1
return

Crouch() { 
    SendInput, { {crouch_key} Down} 
}
CrouchRelease() {
    SendInput, { {crouch_key} Up} 
}

ToggleHoldMode:
    HoldMode := !HoldMode
    ToolTip % HoldMode ? "HOLD MODE" : "ALWAYS ON MODE", 0, 0
    if (PlaySounds) {
    SoundBeep HoldMode ? 400 : 200, 80
    }
    SetTimer RemoveTT, -1800
return

SprayMode:
    if (letscrouch) {
        letscrouch := false
        ToolTip CROUCH SPRAY OFF, 0, 36
        SetTimer RemoveTT, -1800
    }
    spray := !spray
    if (PlaySounds) {
    SoundBeep spray ? 400 : 200, 80
    }
    ToolTip % spray ? "SPRAY MODE ON" : "SPRAY MODE OFF", 0, 18
    if (!letscrouch) {
        Sleep, 600
    }
    SetTimer RemoveTT, -1800
return

CrouchMode:
    if (spray) {
        spray := false
        ToolTip SPRAY MODE OFF, 0, 18
        SetTimer RemoveTT, -1800
    }
    letscrouch := !letscrouch
    if (PlaySounds) {
    SoundBeep letscrouch ? 400 : 200, 80
    }
    ToolTip % letscrouch ? "CROUCH SPRAY ON" : "CROUCH SPRAY OFF", 0, 36
    if (!spray) {
        Sleep, 600
    }
    SetTimer RemoveTT, -1800
return

PauseMode:
    Paused := !Paused
    if (Paused) {
        SetTimer CheckTrigger, Off
        if (PlaySounds) {
        SoundBeep 350, 100
        }
        ToolTip PAUSED, 0, 54
    } else {
        SetTimer CheckTrigger, 1
        if (PlaySounds) {
        SoundBeep 450, 100
        }
        ToolTip RESUMED, 0, 54
    }
    SetTimer RemoveTT, -1800
return

RemoveTT:
    ToolTip
return

ExitScript:
    if (PlaySounds) {
    SoundBeep, 400, 200
    SoundBeep, 300, 200
    SoundBeep, 200, 200
    }
    ExitApp
return

Restart:
    if (PlaySounds) {
    SoundBeep, 400, 200
    SoundBeep, 200, 200
    }
    Sleep 180
    Reload
return

CheckTrigger:
    if (!Paused && (GetKeyState(TriggerKey, "P") || GetKeyState(TriggerKey2, "P") || !HoldMode)) {
        Shoot()
    }
return

Shoot() {
    global
    PixelSearch px, py, ScanLeft, ScanTop, ScanRight, ScanBottom, %Color%, %Variation%, Fast RGB
    if (ErrorLevel = 0) {
    If !GetKeyState(ShootKey, "P") {
        Random delay, %MinClickDelay%, %MaxClickDelay%
        Sleep %delay%

        SendInput, {%ShootKey% Down} 

        if (spray) {
            Sleep % 50 + Random(20, 60)
        }
        if (!letscrouch) {
            Sleep % 5 + Random(0, 5)
        } else {
            Crouch()
            Sleep % 50 + Random(20, 60)
            CrouchRelease()
        }

        SendInput, {%ShootKey% Up} 
        
        Random extra, 10, 30
        if (RandomExtraSleep)
            extra += Random(-10, 20)
        Sleep % extra + ExtraSleepAfter
    }
}
return
}

Random(min, max) {
    Random val, min, max
    return val
}

ShowScanOverlay() {
    global ScanLeft, ScanRight, ScanTop, ScanBottom
         , ScanBoxColor, ScanBoxThickness, ShowScanBox
    if (!ShowScanBox)
        return
    w := ScanRight - ScanLeft
    h := ScanBottom - ScanTop
    Gui, ScanBox:Destroy
    Gui, ScanBox:New, +AlwaysOnTop +ToolWindow -Caption +E0x20 +LastFound
    Gui, ScanBox:Color, 000000
    WinSet, TransColor, 000000 255
    Gui, ScanBox:Add, Progress, % "x0 y0 w" w " h" ScanBoxThickness " Background" ScanBoxColor " Disabled"
    Gui, ScanBox:Add, Progress, % "x0 y" (h - ScanBoxThickness) " w" w " h" ScanBoxThickness " Background" ScanBoxColor " Disabled"
    Gui, ScanBox:Add, Progress, % "x0 y0 w" ScanBoxThickness " h" h " Background" ScanBoxColor " Disabled"
    Gui, ScanBox:Add, Progress, % "x" (w - ScanBoxThickness) " y0 w" ScanBoxThickness " h" h " Background" ScanBoxColor " Disabled"
    Gui, ScanBox:Show, x%ScanLeft% y%ScanTop% w%w% h%h% NoActivate
    WinSet, Redraw,, ahk_id %GuiHwnd%
    WinSet, AlwaysOnTop, On, ahk_id %GuiHwnd%
}