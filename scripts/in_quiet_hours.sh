#!/usr/bin/env bash
# exit 0 if now (Asia/Calcutta) is inside POLICY schedule.quiet_hours (e.g. 22:00-07:00); else 1.
J=/home/box/jarvis
QH=$(grep -E '^\s*quiet_hours:' "$J/POLICY.yaml" | sed -E 's/.*"([0-9:]+-[0-9:]+)".*/\1/')
[[ "$QH" =~ ^([0-9]{2}):([0-9]{2})-([0-9]{2}):([0-9]{2})$ ]] || { echo "quiet_hours unset"; exit 1; }
s=$((10#${BASH_REMATCH[1]}*60+10#${BASH_REMATCH[2]})); e=$((10#${BASH_REMATCH[3]}*60+10#${BASH_REMATCH[4]}))
NOW=${JARVIS_NOW:-$(TZ=Asia/Kolkata date +%H:%M)}; n=$((10#${NOW%:*}*60+10#${NOW#*:}))
if (( s > e )); then (( n >= s || n < e )); else (( n >= s && n < e )); fi && { echo "quiet ($NOW in $QH)"; exit 0; }
echo "not quiet ($NOW, window $QH)"; exit 1
