#!/bin/bash

# Loop through all arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -c)
      clients="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1. Correct usage: ./dev.sh -c <client amount>"
      exit 1
      ;;
  esac
done

# If no client argument has been set, start one client and server by default
if [ -z "$clients" ]; then
    python -m server.main 2>&1 | sed "s/^/[server-1] /" &
    python -m client.main 2>&1 | sed "s/^/[client-1] /" &
    wait
    exit
fi

python -m server.main 2>&1 | sed "s/^/[server-1] /" &
echo
for ((i=0; i < $clients; i++)); do
  python -m client.main 2>&1 | sed "s/^/[client-1] /" &
done

wait
