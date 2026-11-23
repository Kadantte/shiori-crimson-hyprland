#!/usr/bin/env bash
# Deliberately on-demand: no background nvidia-smi polling, preserving idle P8 power.
set -euo pipefail
if ! command -v nvidia-smi >/dev/null 2>&1; then
  notify-send 'Shiori · GPU' 'NVIDIA utilities not available.'
  exit 0
fi
report="$(nvidia-smi --query-gpu=name,pstate,power.draw,temperature.gpu,utilization.gpu,memory.used --format=csv,noheader,nounits 2>/dev/null | head -1)" || true
if [[ -z "$report" ]]; then
  notify-send 'Shiori · GPU' 'Could not read GPU status.'
else
  IFS=, read -r name pstate watts temp util vram <<< "$report"
  message="$(printf "%s\nPower state: %s · %s W\nGPU: %s°C · %s%% load\nVRAM: %s MiB" "$name" "$pstate" "$watts" "$temp" "$util" "$vram")"
  notify-send -t 6000 'Shiori · NVIDIA status' "$message"
fi
