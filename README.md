# AstraTrade Project

This is the official repository for the AstraTrade app—a cross-platform, gamified perpetuals trading application built with Flutter. This README provides the main documentation for the entire project.

## Project Overview
AstraTrade is a cross-platform, gamified perpetuals trading application built with Flutter that transforms complex blockchain trading mechanics into an intuitive, engaging cosmic experience.

Key features include:
- Seamless onboarding with Web3Auth social login (Google/Apple)
- Complete gamification system with XP, levels, achievements, and trading integration
- Real perpetual trading via Extended Exchange API
- Gasless transactions via AVNU paymaster integration
- Native mobile features including push notifications and haptic feedback
- Social features (clan/alliance system and friend challenges - planned)
- NFT rewards system (achievement-based collectibles - planned)

## Security Improvements
Recent security improvements have been made to the project:
- API keys are now loaded from environment variables instead of being hardcoded
- Created templates for secure local configuration files
- Updated documentation to reflect secure practices
- Enhanced smart contracts with improved functionality and security

See [Security Fixes Summary](docs/security/SECURITY_FIXES_SUMMARY.md) for detailed information.

## Getting Started

### Prerequisites
- Flutter SDK (3.8.1 or later)
- Dart SDK
- Python 3.9+
- Scarb 2.8.0
- Node.js (for some web features)

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/trungkien1992/AstraTrade-Project.git
   cd AstraTrade-Project
   ```
2. Install dependencies:
   ```bash
   flutter pub get
   ```
3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys
   ```
4. Compile smart contracts:
   ```bash
   cd apps/contracts
   scarb build
   ```
5. Run the app:
   - For mobile:
     ```bash
     flutter run
     ```
   - For web:
     ```bash
     flutter run -d chrome
     ```
   - For desktop:
     ```bash
     flutter run -d macos  # or windows, linux
     ```

### Smart Contract Development
1. Compile contracts:
   ```bash
   cd apps/contracts
   scarb build
   ```
2. Test contract compilation:
   ```bash
   cd /Users/admin/AstraTrade-Project
   python3 scripts/test_contracts_simple.py
   ```

### Configuration
- Update `lib/utils/constants.dart` for environment and branding settings.
- See `apps/frontend/CONFIGURATION.md` for detailed setup (Web3Auth, API endpoints, etc).

## Project Structure
```
├── apps/
│   ├── frontend/          # Flutter mobile application
│   ├── backend/           # FastAPI backend services
│   └── contracts/         # Cairo smart contracts
├── docs/                  # Comprehensive documentation
├── scripts/               # Deployment and testing scripts
└── tests/                 # Unit and integration tests
```

## Status
- **Current Version:** v1.0.0
- **Core features implemented:**
  - Mobile-first frontend using Flutter
  - Starknet.dart SDK integration
  - Gamified elements (XP, streaks, leaderboard)
  - Seamless onboarding (Web3Auth)
  - Gasless transactions via paymaster
  - Real perpetual trading via Extended Exchange API
  - Native mobile features
- **Security improvements:**
  - API keys secured using environment variables instead of hardcoding
  - Secure storage for sensitive user data
  - Comprehensive error handling and validation
- **Planned features:**
  - Social features (clan/alliance system and friend challenges)
  - NFT rewards system (achievement-based NFT collectibles)

## Documentation

See our organized [documentation](docs/README.md) for comprehensive information about the project. All documentation has been updated to reflect the current codebase status as of July 28, 2025.

## StarkWare Bounty Submission

For judges evaluating our StarkWare bounty submission, please see our dedicated [bounty submission package](bounty_submission/package_summary.md) which includes:
- [Bounty Submission README](BOUNTY_SUBMISSION_README.md)
- [Technical Overview for Bounty](docs/architecture/bounty_technical_overview.md)
- [Technical Achievements](bounty_submission/technical_achievements.md)
- [Video Demo Script](bounty_submission/video_demo_script.md)
- [Package Summary](bounty_submission/package_summary.md)

## License
MIT

---
For more details, see the in-app documentation or contact the project maintainer.