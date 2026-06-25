#!/bin/sh

echo "🤖 SmartHR AI Boot Sequence Initiated..."

# Check if Ollama daemon engine is discoverable on host ports
if command -v ollama >/dev/null 2>&1; then
    echo "🧠 Verifying local generative workspace model binaries..."
    # Asynchronously pull models in the background to avoid blocking server boot loops
    ollama pull tinyllama > /dev/null 2>&1 &
else
    echo "⚠️ Ollama engine not exposed natively inside context, continuing to core engines."
fi

# Execute main process worker bound to container tasks (FastAPI/Uvicorn)
exec "$@"