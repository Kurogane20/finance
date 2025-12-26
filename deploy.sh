#!/bin/bash

# Finance Dashboard - Quick Deploy Script
# Usage: ./deploy.sh [up|down|restart|logs|build]

set -e

ACTION=${1:-up}

case $ACTION in
    up)
        echo "🚀 Starting Finance Dashboard..."
        docker-compose up -d
        echo "✅ Application started!"
        echo "📍 Frontend: http://localhost"
        echo "📍 Backend: http://localhost:8000"
        ;;
    down)
        echo "🛑 Stopping Finance Dashboard..."
        docker-compose down
        echo "✅ Application stopped."
        ;;
    restart)
        echo "🔄 Restarting Finance Dashboard..."
        docker-compose restart
        echo "✅ Application restarted."
        ;;
    logs)
        docker-compose logs -f
        ;;
    build)
        echo "🔨 Building and starting Finance Dashboard..."
        docker-compose up -d --build
        echo "✅ Application built and started!"
        ;;
    *)
        echo "Usage: ./deploy.sh [up|down|restart|logs|build]"
        exit 1
        ;;
esac
