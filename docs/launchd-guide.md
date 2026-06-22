# macOS launchd Guide

Use this when you want the digest to run on a Mac without n8n.

## Install

1. Copy the plist template:

```bash
cp launchd/com.example.top-journal-digest.plist ~/Library/LaunchAgents/com.example.top-journal-digest.plist
```

2. Edit every `/ABSOLUTE/PATH/TO/top-journal-daily-n8n-template` placeholder.

3. Create the output and log folders:

```bash
mkdir -p /ABSOLUTE/PATH/TO/top-journal-daily-n8n-template/out
mkdir -p /ABSOLUTE/PATH/TO/top-journal-daily-n8n-template/logs
```

4. Validate:

```bash
plutil -lint ~/Library/LaunchAgents/com.example.top-journal-digest.plist
```

5. Load:

```bash
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.example.top-journal-digest.plist
```

## Run Immediately

```bash
launchctl kickstart -k gui/$(id -u)/com.example.top-journal-digest
```

## Debug

```bash
launchctl print gui/$(id -u)/com.example.top-journal-digest
tail -n 100 /ABSOLUTE/PATH/TO/top-journal-daily-n8n-template/logs/launchd.err.log
```

## Uninstall

```bash
launchctl bootout gui/$(id -u)/com.example.top-journal-digest
rm ~/Library/LaunchAgents/com.example.top-journal-digest.plist
```

launchd has a minimal environment. If you need API keys or model settings, either export them from a wrapper script or add an `EnvironmentVariables` block to your private plist. Do not commit private plist files with real secrets.

