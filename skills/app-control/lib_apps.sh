# Allowlist map: name -> binary. Mirrors POLICY.yaml apps_allowlist (only binaries present on this box).
declare -A APP_BIN=( [chrome]=google-chrome [terminal]=xfce4-terminal )
declare -A WORKSETS=( [work]="chrome terminal" )
app_bin(){ local b=${APP_BIN[$1]:-}; [ -n "$b" ] && command -v "$b" >/dev/null && echo "$b"; }
