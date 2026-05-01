# Changelog

All notable changes to gs_utils will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.4.0] - 2026-05-01

### 🎯 Major Change: Focused on Google APIs

**Breaking Changes**:
- Removed `window_controler` module (Windows-specific, unrelated to Google APIs)
- Removed `time_tracker` decorator (generic utility, not Google-specific)

**Rationale**:
- Clear library identity: "Python wrapper for Google APIs"
- Better target audience: Google API users
- Reduced dependencies: removed `pyautogui`, `pywinauto`
- Improved discoverability and SEO

### Changed - Library Identity
- **New positioning**: "Simple and powerful Python wrapper for Google APIs"
- **Core focus**: Google Drive + Google Sheets (with more Google services coming)
- **Removed**: Generic utilities and platform-specific features
- **Updated**: Package description, keywords, and documentation

### Removed
- `gs_utils.decorators` module
- `gs_utils.window_controler` module  
- Dependencies: `pyautogui>=0.9.50`, `pywinauto>=0.6.8`

### Documentation
- Rebranded README with clear value proposition
- Updated examples focused on Google API use cases
- Improved comparison with alternatives (gspread, PyDrive2)
- Clearer roadmap for future Google services

### Migration Guide
**If you were using removed features:**
- `time_tracker`: Use standard Python timing libraries (e.g., `time`, `timeit`)
- `window_controler`: Use `pyautogui` or `pywinauto` directly

**All Google API features remain unchanged and fully compatible.**

---

## [0.3.0] - 2026-05-01

### Added - Config System
- **Flexible configuration system** with 4-level priority
  - Code > Environment Variables > Config File > Default
- Support for environment variables (`GS_UTILS_*`)
- Optional YAML config file (`.gs_utils_config.yaml`)
- Config class with singleton pattern
- 12 comprehensive config tests

### Changed
- `GoogleBaseManager` now supports config system
- `labs_modules.secret_key` dependency is now optional
- Added new parameters: `delegate_email`, `discord_webhook`
- Improved error messages with config setup instructions

### Configuration Options
```bash
# Environment Variables
GS_UTILS_JSON_FOLDER        # JSON key folder path
GS_UTILS_DELEGATE_EMAIL     # G Suite delegation email
GS_UTILS_MAX_RETRIES        # API retry count
GS_UTILS_DISCORD_WEBHOOK    # Discord webhook URL
```

### Testing
- **29 tests passing** (100%)
- Added 12 config system tests
- Verified external environment compatibility
- All 3 configuration methods validated

---

## [0.2.0] - 2026-05-01

### Added - Package Infrastructure
- Complete pip-installable package setup
- MIT License
- `requirements.txt` and `requirements-dev.txt`
- `pyproject.toml` for modern Python packaging (PEP 518)
- pytest configuration with 17 tests
- GitHub Actions CI/CD workflows
- Deployment script (`scripts/deploy.py`)

### Documentation
- **GOOGLE_API_SETUP.md**: Complete Google API setup guide
- **DEPLOYMENT.md**: PyPI deployment guide
- **QUICKSTART.md**: Quick start guide
- **.gs_utils_config.yaml.example**: Config template

### Improved - Error Handling
- Friendly error messages for missing JSON folder
- Friendly error messages for missing JSON files
- Step-by-step setup instructions in errors
- Security warnings in error messages
- 6 authentication error tests

### Features
- Google Drive management (`GoogleDriveManager`)
- Google Sheets management (`GoogleSheetManager`)
- Time tracking decorator (`@time_tracker`)
- Utility functions for Google API
- Windows automation functions

---

## [0.1.0] - 2025-01-01 (Initial)

### Added - Core Functionality
- Basic package structure
- `GoogleBaseManager` class
- `GoogleDriveManager` class
- `GoogleSheetManager` class
- `time_tracker` decorator
- Window automation utilities
- Basic documentation

---

## Development History

### Key Achievements

**Infrastructure (v0.2.0)**
- Transformed from simple script to professional package
- Full PyPI deployment readiness
- Comprehensive testing (17 → 29 tests)
- CI/CD automation

**User Experience (v0.2.0 & v0.3.0)**
- Friendly error messages with emojis and box drawing
- Multiple configuration methods
- Clear documentation hierarchy
- Security best practices

**Code Quality**
- Modular structure (`google/` subfolder)
- Comprehensive test coverage
- Type hints and docstrings
- PEP 518 compliance

### Testing Statistics
- **Total Tests**: 29 (100% passing)
- **Test Categories**:
  - Basic functionality: 11 tests
  - Config system: 12 tests
  - Auth error handling: 6 tests
- **External Environment**: Verified ✅
- **Priority System**: Validated ✅

### Package Metrics
- **Python Support**: 3.7 - 3.12
- **Dependencies**: 7 runtime, 4 dev
- **File Structure**: Modular and clean
- **Documentation**: Complete

---

## Migration Notes

### Upgrading to 0.3.0 from 0.2.0

**No breaking changes!** All existing code continues to work.

#### New Features Available

**Environment Variables (Recommended)**
```bash
export GS_UTILS_JSON_FOLDER="/path/to/credentials"
export GS_UTILS_DELEGATE_EMAIL="user@domain.com"
```

**Config File (Optional)**
```yaml
# .gs_utils_config.yaml
google:
  json_folder: "/path/to/credentials"
  delegate_email: "user@domain.com"
```

**Code Parameters (New)**
```python
from gs_utils import GoogleDriveManager

manager = GoogleDriveManager(
    json_folder='/custom/path',
    delegate_email='user@domain.com',
    discord_webhook='https://...'
)
```

### Upgrading to 0.2.0 from 0.1.0

- Install: `pip install gs_utils` (or `pip install -e .` for dev)
- Setup JSON keys in `.secret/` folder
- See GOOGLE_API_SETUP.md for details

---

## Credits

**Author**: geunsu-son (손근수)  
**AI Assistant**: Claude Sonnet 4 (Cursor Cloud Agent)  
**License**: MIT

---

## Links

- **GitHub**: https://github.com/geunsu-son/gs_utils
- **PyPI**: https://pypi.org/project/gs_utils/ (after deployment)
- **Issues**: https://github.com/geunsu-son/gs_utils/issues
- **Documentation**: See README.md and GOOGLE_API_SETUP.md
