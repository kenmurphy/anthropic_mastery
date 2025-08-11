#!/bin/bash
# Quick wrapper script for manual re-clustering

cd "$(dirname "$0")"

echo "Anthropic Mastery - Quick Re-Cluster"
echo "====================================="

# Check if Python script exists
if [ ! -f "manual_recluster.py" ]; then
    echo "Error: manual_recluster.py not found!"
    exit 1
fi

# If no arguments provided, show help
if [ $# -eq 0 ]; then
    echo "Usage: $0 [options]"
    echo ""
    echo "Quick commands:"
    echo "  $0 status          # Show clustering status"
    echo "  $0 run             # Run clustering (background method)"
    echo "  $0 api             # Run clustering via API"
    echo "  $0 reset           # Reset and re-cluster everything"
    echo "  $0 help            # Show detailed help"
    echo ""
    echo "For more options, run: python manual_recluster.py --help"
    exit 0
fi

# Handle quick commands
case "$1" in
    "status")
        python manual_recluster.py --status
        ;;
    "run")
        python manual_recluster.py --method background
        ;;
    "api")
        python manual_recluster.py --method api
        ;;
    "reset")
        python manual_recluster.py --method reset
        ;;
    "help")
        python manual_recluster.py --help
        ;;
    *)
        # Pass all arguments to the Python script
        python manual_recluster.py "$@"
        ;;
esac
