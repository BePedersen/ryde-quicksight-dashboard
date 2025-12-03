#!/bin/bash
set -e

echo "🚀 Setting up Ryde QuickSight Dashboard..."

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check for Node.js
if ! command -v npm &> /dev/null; then
    echo "❌ Node.js and npm are required but not installed."
    exit 1
fi

# Setup backend
echo ""
echo "📦 Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -q -r requirements.txt
echo "✅ Backend ready!"

# Setup frontend
echo ""
echo "📦 Setting up frontend..."
cd ../frontend
npm install --legacy-peer-deps
echo "✅ Frontend ready!"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start development:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend && source venv/bin/activate && python app.py"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend && npm run dev"
echo ""
echo "Then visit:"
echo "  Backend: http://localhost:5000"
echo "  Frontend: http://localhost:5173"
echo ""
echo "To build for production:"
echo "  cd frontend && npm run build"
echo "  cd ../backend && python app.py"
echo "  Visit http://localhost:5000"
