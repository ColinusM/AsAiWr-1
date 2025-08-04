# PyInstaller macOS App Packaging Guide

## Basic PyInstaller Setup for macOS

### Installation and Configuration

```bash
# Install PyInstaller and dependencies
pip install pyinstaller
pip install --upgrade pyinstaller

# For macOS app bundling
pip install py2app  # Alternative option
pip install pyobjc-framework-Cocoa  # For native macOS integration
```

### Basic App Spec Creation

```python
# assemblyai_stt.spec - PyInstaller spec file
# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Get the directory containing this spec file
spec_root = Path(SPECPATH)
src_root = spec_root / 'src'

block_cipher = None

# Define all Python files to include
python_files = [
    str(src_root / 'main.py'),
    str(src_root / 'audio' / '__init__.py'),
    str(src_root / 'audio' / 'capture.py'),
    str(src_root / 'audio' / 'stream_handler.py'),
    str(src_root / 'ui' / '__init__.py'),
    str(src_root / 'ui' / 'popup_window.py'),
    str(src_root / 'ui' / 'settings_menu.py'),
    str(src_root / 'input' / '__init__.py'),
    str(src_root / 'input' / 'hotkey_handler.py'),
    str(src_root / 'input' / 'wake_word.py'),
    str(src_root / 'input' / 'text_inserter.py'),
    str(src_root / 'config' / '__init__.py'),
    str(src_root / 'config' / 'settings.py'),
    str(src_root / 'utils' / '__init__.py'),
    str(src_root / 'utils' / 'permissions.py'),
    str(src_root / 'utils' / 'error_handler.py'),
]

# Data files to include (icons, sounds, etc.)
datas = [
    (str(spec_root / 'assets' / 'icons'), 'assets/icons'),
    (str(spec_root / 'assets' / 'sounds'), 'assets/sounds'),
]

# Hidden imports for libraries that PyInstaller might miss
hiddenimports = [
    'assemblyai',
    'assemblyai.streaming.v3',
    'sounddevice',
    'pyautogui',
    'pyperclip', 
    'pynput',
    'pvporcupine',
    'tkinter',
    'tkinter.ttk',
    'queue',
    'threading',
    'websocket',
    'websocket._core',
    'websocket._app',
    'numpy',
    'numpy.core',
    'numpy.core._multiarray_umath',
    '_cffi_backend',
    'Cocoa',
    'Foundation',
    'PyObjCTools',
    'PyObjCTools.AppHelper',
]

a = Analysis(
    python_files,
    pathex=[str(spec_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',  # Exclude unnecessary packages
        'scipy',
        'pandas',
        'PIL',
        'IPython',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AssemblyAI-STT',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(spec_root / 'assets' / 'icons' / 'app_icon.icns'),  # App icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AssemblyAI-STT',
)

# Create macOS app bundle
app = BUNDLE(
    coll,
    name='AssemblyAI-STT.app',
    icon=str(spec_root / 'assets' / 'icons' / 'app_icon.icns'),
    bundle_identifier='com.assemblyai.stt.wrapper',
    info_plist={
        'CFBundleName': 'AssemblyAI STT',
        'CFBundleDisplayName': 'AssemblyAI Speech-to-Text',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleIdentifier': 'com.assemblyai.stt.wrapper',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.15',  # macOS Catalina minimum
        'NSMicrophoneUsageDescription': 'This app requires microphone access for speech-to-text transcription.',
        'NSAccessibilityUsageDescription': 'This app requires accessibility access to insert text into other applications.',
        'LSApplicationCategoryType': 'public.app-category.productivity',
        'CFBundleDocumentTypes': [],
        'CFBundleURLTypes': [],
        'NSAppleEventsUsageDescription': 'This app requires Apple Events access to control other applications.',
        'NSSystemAdministrationUsageDescription': 'This app requires system administration access for global hotkeys.',
    },
)
```

### Build Script

```bash
#!/bin/bash
# build_app.sh - Build script for macOS app

set -e  # Exit on any error

echo "Building AssemblyAI STT macOS App..."

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/
rm -rf dist/
rm -rf __pycache__/
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

# Verify requirements
echo "Installing/updating requirements..."
pip install -r requirements.txt

# Create app icon if it doesn't exist
if [ ! -f "assets/icons/app_icon.icns" ]; then
    echo "Creating app icon..."
    # You can use iconutil or other tools to create .icns from .png
    # iconutil -c icns assets/icons/app_icon.iconset
fi

# Build the app
echo "Building app with PyInstaller..."
pyinstaller assemblyai_stt.spec --clean --noconfirm

# Code signing (development only)
echo "Code signing app..."
APP_PATH="dist/AssemblyAI-STT.app"

if [ -d "$APP_PATH" ]; then
    # Sign with ad-hoc signature for development
    codesign --force --deep --sign - "$APP_PATH"
    echo "App signed with ad-hoc signature"
    
    # Verify the signature
    codesign --verify --verbose "$APP_PATH"
    
    # Check if app can be opened
    echo "Testing app launch..."
    open "$APP_PATH" --args --test-mode
    sleep 2
    pkill -f "AssemblyAI-STT" || true
    
    echo "Build completed successfully!"
    echo "App bundle created at: $APP_PATH"
    echo "Size: $(du -sh "$APP_PATH" | cut -f1)"
else
    echo "ERROR: App bundle not created"
    exit 1
fi
```

### Advanced Configuration

```python
# advanced_build_config.py - Advanced PyInstaller configuration

import os
import sys
import platform
from pathlib import Path

class MacOSBuildConfig:
    """Advanced configuration for macOS app building"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.dist_path = project_root / 'dist'
        self.build_path = project_root / 'build'
        
    def get_hidden_imports(self) -> list:
        """Get comprehensive list of hidden imports"""
        base_imports = [
            # AssemblyAI related
            'assemblyai',
            'assemblyai.streaming',
            'assemblyai.streaming.v3',
            'websocket',
            'websocket._core',
            'websocket._app',
            'websocket._handshake',
            'websocket._http',
            'websocket._logging',
            'websocket._socket',
            'websocket._utils',
            
            # Audio processing
            'sounddevice',
            'soundfile',
            '_soundfile',
            '_soundfile_data',
            'cffi',
            '_cffi_backend',
            'numpy',
            'numpy.core._multiarray_umath',
            'numpy.random._common',
            'numpy.random.bit_generator',
            'numpy.random._bounded_integers',
            
            # Wake word detection
            'pvporcupine',
            'pvporcupine._porcupine',
            
            # GUI and system integration
            'tkinter',
            'tkinter.ttk',
            'tkinter.font',
            'tkinter.messagebox',
            'pyautogui',
            'pyperclip',
            'pynput',
            'pynput.keyboard',
            'pynput.mouse',
            'pynput._util',
            'pynput._util.darwin',
            
            # macOS specific
            'Cocoa',
            'Foundation',
            'CoreFoundation',
            'PyObjCTools',
            'PyObjCTools.AppHelper',
            'objc',
            
            # Standard library modules that might be missed
            'queue',
            'threading',
            'multiprocessing',
            'json',
            'urllib',
            'urllib.request',
            'urllib.parse',
            'ssl',
            'certifi',
        ]
        
        return base_imports
        
    def get_data_files(self) -> list:
        """Get list of data files to include"""
        data_files = []
        
        # Include assets
        assets_dir = self.project_root / 'assets'
        if assets_dir.exists():
            for subdir in ['icons', 'sounds']:
                subdir_path = assets_dir / subdir
                if subdir_path.exists():
                    data_files.append((str(subdir_path), f'assets/{subdir}'))
                    
        # Include configuration files
        config_files = ['config.json', 'default_config.json']
        for config_file in config_files:
            config_path = self.project_root / config_file
            if config_path.exists():
                data_files.append((str(config_path), '.'))
                
        # Include certificates for SSL connections
        try:
            import certifi
            cert_path = certifi.where()
            data_files.append((cert_path, 'certifi'))
        except ImportError:
            pass
            
        return data_files
        
    def get_excludes(self) -> list:
        """Get list of modules to exclude from build"""
        return [
            'matplotlib',
            'scipy',
            'pandas',
            'IPython',
            'jupyter',
            'notebook',
            'sympy',
            'sphinx',
            'pytest',
            'setuptools',
            'pip',
            'wheel',
            'distutils',
        ]
        
    def get_binary_excludes(self) -> list:
        """Get list of binaries to exclude"""
        return [
            'libGL*',  # OpenGL libraries
            'libX11*', # X11 libraries (not needed on macOS)
            'libxcb*', # XCB libraries
        ]
        
    def get_upx_excludes(self) -> list:
        """Get list of files to exclude from UPX compression"""
        return [
            'vcruntime140.dll',  # Not relevant for macOS
            'python3*.dll',      # Not relevant for macOS
            'Qt5*',             # Qt libraries if present
        ]
        
    def create_info_plist(self) -> dict:
        """Create Info.plist content for macOS app"""
        return {
            'CFBundleName': 'AssemblyAI STT',
            'CFBundleDisplayName': 'AssemblyAI Speech-to-Text',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleIdentifier': 'com.assemblyai.stt.wrapper',
            'CFBundlePackageType': 'APPL',
            'CFBundleSignature': '????',
            'CFBundleExecutable': 'AssemblyAI-STT',
            'CFBundleIconFile': 'app_icon.icns',
            
            # System requirements
            'LSMinimumSystemVersion': '10.15',  # macOS Catalina
            'NSHighResolutionCapable': True,
            'LSRequiresNativeExecution': True,
            
            # Privacy permissions
            'NSMicrophoneUsageDescription': 'This app requires microphone access for speech-to-text transcription.',
            'NSAccessibilityUsageDescription': 'This app requires accessibility access to insert text into other applications.',
            'NSAppleEventsUsageDescription': 'This app needs to send keystrokes to other applications.',
            'NSSystemAdministrationUsageDescription': 'This app requires elevated access for global hotkeys.',
            
            # App categorization
            'LSApplicationCategoryType': 'public.app-category.productivity',
            
            # URL schemes (if needed)
            'CFBundleURLTypes': [],
            
            # Document types (if needed)
            'CFBundleDocumentTypes': [],
            
            # Background modes
            'LSBackgroundOnly': False,
            'LSUIElement': False,  # Set to True for menu bar only apps
            
            # Security settings
            'NSAppTransportSecurity': {
                'NSAllowsArbitraryLoads': False,
                'NSExceptionDomains': {
                    'api.assemblyai.com': {
                        'NSExceptionRequiresForwardSecrecy': False,
                        'NSExceptionMinimumTLSVersion': '1.2',
                        'NSExceptionAllowsInsecureHTTPLoads': False,
                        'NSIncludesSubdomains': True
                    }
                }
            },
        }
```

### Code Signing and Notarization

```bash
#!/bin/bash
# code_sign.sh - Code signing and notarization script

APP_NAME="AssemblyAI-STT"
APP_PATH="dist/${APP_NAME}.app"
DEVELOPER_ID="Your Developer ID"  # Replace with actual ID
TEAM_ID="Your Team ID"           # Replace with actual team ID

# Function to sign the app
sign_app() {
    echo "Signing app bundle..."
    
    # Sign all frameworks and libraries first
    find "$APP_PATH" -name "*.framework" -exec codesign --force --verify --verbose --sign "$DEVELOPER_ID" {} \;
    find "$APP_PATH" -name "*.dylib" -exec codesign --force --verify --verbose --sign "$DEVELOPER_ID" {} \;
    find "$APP_PATH" -name "*.so" -exec codesign --force --verify --verbose --sign "$DEVELOPER_ID" {} \;
    
    # Sign the main executable
    codesign --force --verify --verbose --sign "$DEVELOPER_ID" "$APP_PATH/Contents/MacOS/$APP_NAME"
    
    # Sign the entire app bundle
    codesign --force --verify --verbose --sign "$DEVELOPER_ID" --entitlements entitlements.plist "$APP_PATH"
    
    echo "App signing completed"
}

# Function for ad-hoc signing (development)
adhoc_sign() {
    echo "Ad-hoc signing for development..."
    codesign --force --deep --sign - "$APP_PATH"
    echo "Ad-hoc signing completed"
}

# Function to verify signature
verify_signature() {
    echo "Verifying signature..."
    codesign --verify --deep --strict --verbose=2 "$APP_PATH"
    spctl --assess --type execute --verbose "$APP_PATH"
}

# Function to create DMG
create_dmg() {
    echo "Creating DMG..."
    DMG_NAME="${APP_NAME}-v1.0.0.dmg"
    
    # Create temporary DMG directory
    mkdir -p "dmg_temp"
    cp -R "$APP_PATH" "dmg_temp/"
    
    # Create DMG
    hdiutil create -volname "$APP_NAME" -srcfolder "dmg_temp" -ov -format UDZO "dist/$DMG_NAME"
    
    # Cleanup
    rm -rf "dmg_temp"
    
    echo "DMG created: dist/$DMG_NAME"
}

# Function to notarize (requires Apple Developer account)
notarize_app() {
    echo "Notarizing app..."
    
    # Create ZIP for notarization
    cd dist
    zip -r "${APP_NAME}.zip" "${APP_NAME}.app"
    
    # Submit for notarization
    xcrun notarytool submit "${APP_NAME}.zip" \
        --apple-id "your-apple-id@example.com" \
        --team-id "$TEAM_ID" \
        --password "@keychain:notarization-password" \
        --wait
        
    # Staple the notarization
    xcrun stapler staple "${APP_NAME}.app"
    
    cd ..
    echo "Notarization completed"
}

# Main execution
if [ "$1" == "adhoc" ]; then
    adhoc_sign
elif [ "$1" == "release" ]; then
    sign_app
    verify_signature
    create_dmg
    # Uncomment for notarization:
    # notarize_app
else
    echo "Usage: $0 [adhoc|release]"
    echo "  adhoc   - Ad-hoc signing for development"
    echo "  release - Full signing and DMG creation"
fi
```

### Entitlements File

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- Required for microphone access -->
    <key>com.apple.security.device.microphone</key>
    <true/>
    
    <!-- Required for network access to AssemblyAI API -->
    <key>com.apple.security.network.client</key>
    <true/>
    
    <!-- Required for accessibility features -->
    <key>com.apple.security.automation.apple-events</key>
    <true/>
    
    <!-- Required for file system access -->
    <key>com.apple.security.files.user-selected.read-write</key>
    <true/>
    
    <!-- Required for preferences access -->
    <key>com.apple.security.files.user-selected.read-only</key>
    <true/>
    
    <!-- Disable library validation for PyInstaller -->
    <key>com.apple.security.cs.disable-library-validation</key>
    <true/>
    
    <!-- Allow unsigned executable memory (required for some Python modules) -->
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
</dict>
</plist>
```

### Distribution and Testing

```python
# test_distribution.py - Test the built app

import subprocess
import os
import time
from pathlib import Path

def test_app_bundle():
    """Test the built app bundle"""
    app_path = Path("dist/AssemblyAI-STT.app")
    
    if not app_path.exists():
        print("ERROR: App bundle not found")
        return False
        
    print(f"Testing app bundle: {app_path}")
    
    # Test 1: Bundle structure
    required_paths = [
        "Contents/Info.plist",
        "Contents/MacOS/AssemblyAI-STT",
        "Contents/Resources",
    ]
    
    for path in required_paths:
        full_path = app_path / path
        if not full_path.exists():
            print(f"ERROR: Missing required path: {path}")
            return False
            
    print("✓ Bundle structure is valid")
    
    # Test 2: Code signature
    try:
        result = subprocess.run([
            "codesign", "--verify", "--deep", "--strict", str(app_path)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Code signature is valid")
        else:
            print(f"WARNING: Code signature issue: {result.stderr}")
            
    except FileNotFoundError:
        print("WARNING: codesign not available for testing")
        
    # Test 3: Info.plist
    try:
        result = subprocess.run([
            "plutil", "-lint", str(app_path / "Contents/Info.plist")
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Info.plist is valid")
        else:
            print(f"ERROR: Info.plist is invalid: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("WARNING: plutil not available for testing")
        
    # Test 4: App launch test
    try:
        print("Testing app launch...")
        process = subprocess.Popen([
            "open", str(app_path), "--args", "--test-mode"
        ])
        
        time.sleep(3)  # Give app time to start
        
        # Check if app is running
        result = subprocess.run([
            "pgrep", "-f", "AssemblyAI-STT"
        ], capture_output=True)
        
        if result.returncode == 0:
            print("✓ App launched successfully")
            
            # Kill the test instance
            subprocess.run(["pkill", "-f", "AssemblyAI-STT"])
        else:
            print("WARNING: Could not detect running app")
            
    except Exception as e:
        print(f"ERROR: App launch test failed: {e}")
        return False
        
    print("All tests passed!")
    return True

if __name__ == "__main__":
    test_app_bundle()
```

## Key Implementation Notes

1. **Dependencies**: Include all required libraries in hiddenimports
2. **Data Files**: Bundle assets, icons, and configuration files
3. **Permissions**: Set proper Info.plist entries for microphone and accessibility
4. **Code Signing**: Use ad-hoc signing for development, proper certificates for distribution
5. **Testing**: Verify bundle structure, signatures, and app launch
6. **Size Optimization**: Exclude unnecessary modules to reduce app size
7. **Compatibility**: Set minimum macOS version appropriately