#!/bin/bash

# AstraTrade Bounty Submission Demo Script
# This script helps judges quickly run and evaluate the AstraTrade implementation

echo "🚀 AstraTrade Bounty Submission Demo"
echo "====================================="
echo ""
echo "This script will guide you through the key components of our submission."
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."
if ! command -v flutter &> /dev/null; then
    echo "❌ Flutter is not installed. Please install Flutter SDK."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python3."
    exit 1
fi

if ! command -v scarb &> /dev/null; then
    echo "❌ Scarb is not installed. Please install Scarb 2.8.0."
    exit 1
fi

echo "✅ All prerequisites are installed"
echo ""

# Show repository structure
echo "📂 Repository Structure:"
echo "------------------------"
echo "bounty_submission/"
echo "├── flutter_app/          # Flutter mobile application"
echo "├── cairo_contracts/      # Cairo smart contracts"
echo "├── documentation/        # Comprehensive documentation"
echo "├── BOUNTY_SUBMISSION_README.md  # Main submission document"
echo "└── demo_script.sh        # This demo script"
echo ""

# Show Flutter app structure
echo "📱 Flutter App Structure:"
echo "-------------------------"
cd /Users/admin/AstraTrade-Project/apps/frontend
find lib -type d | head -10
echo "... (showing first 10 directories)"
echo ""

# Show smart contract structure
echo "계약 Cairo Smart Contracts:"
echo "---------------------------"
cd /Users/admin/AstraTrade-Project/apps/contracts
ls -la
echo ""

# Show contract compilation
echo "🔨 Smart Contract Compilation:"
echo "------------------------------"
cd /Users/admin/AstraTrade-Project/apps/contracts
scarb build
echo ""

# Show documentation
echo "📚 Key Documentation:"
echo "---------------------"
echo "1. BOUNTY_SUBMISSION_README.md - Main submission document"
echo "2. docs/architecture/bounty_technical_overview.md - Technical overview focused on bounty requirements"
echo "3. docs/security/SECURITY_FIXES_SUMMARY.md - Security improvements"
echo "4. docs/smart_contracts/README.md - Smart contract documentation"
echo ""

# Show how to run the app
echo "🏃 How to Run the Application:"
echo "------------------------------"
echo "1. cd /Users/admin/AstraTrade-Project/apps/frontend"
echo "2. flutter pub get"
echo "3. Create .env file with your API keys (see .env.example)"
echo "4. flutter run"
echo ""
echo "Note: For a full demo, you'll need Extended Exchange API keys and a Starknet wallet."
echo ""

echo "🎉 Demo script completed!"
echo "For any questions, please contact Peter Nguyen (@0xpeternguyen)"