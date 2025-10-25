#!/usr/bin/env bash
set -euo pipefail

# Usage: maven-invoke.sh [CMD] [OPTS]
# Example: ./maven-invoke.sh "clean package" "-B -DskipTests"

CMD="$1"
OPTS="${2-}"

if [[ -z "$CMD" ]]; then
  echo "ERROR: No Maven command/goals provided."
  exit 1
fi

# Locate mvn wrapper if present
MVN=$( [[ -x ./mvnw ]] && echo "./mvnw" || echo "mvn" )


# Split user-provided strings into arrays safely (word-splitting by shell)
# This prevents shell metacharacters from being interpreted by the shell when we exec the command.
read -ra CMD_ARR <<< "$CMD"
if [[ -n "$OPTS" ]]; then
  read -ra OPTS_ARR <<< "$OPTS"
else
  OPTS_ARR=()
fi

# Optional: basic validation - warn and exit on obviously dangerous tokens.
# (This is conservative; arrays already protect from shell injection, but
# this helps catch tokens with embedded newlines or control-characters.)
for token in "${CMD_ARR[@]}" "${OPTS_ARR[@]}"; do
  if [[ "$token" =~ [$'\n\r\t'] ]]; then
    echo "ERROR: Invalid whitespace/control characters in token: $token"
    exit 1
  fi
done

# Show the command we will run (safe expansion for readability)
echo "[INFO] Running: $MVN ${OPTS_ARR[*]} ${CMD_ARR[*]}"

# Exec maven with arrays (this prevents shell re-parsing of tokens)
"$MVN" "${OPTS_ARR[@]}" "${CMD_ARR[@]}"
