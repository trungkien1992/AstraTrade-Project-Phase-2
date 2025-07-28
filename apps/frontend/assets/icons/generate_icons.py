#!/usr/bin/env python3
"""
AstraTrade App Icon Generator
Converts the SVG design to all required icon sizes for iOS and Android
"""

import os
import subprocess
from pathlib import Path

# Icon sizes for different platforms
ICON_SIZES = {
    # iOS sizes
    'ios': {
        'icon-1024.png': 1024,    # App Store
        'icon-180.png': 180,      # iPhone App Icon
        'icon-167.png': 167,      # iPad Pro
        'icon-152.png': 152,      # iPad
        'icon-120.png': 120,      # iPhone
        'icon-87.png': 87,        # iPhone Settings
        'icon-80.png': 80,        # iPad Settings
        'icon-76.png': 76,        # iPad
        'icon-58.png': 58,        # iPhone Settings
        'icon-40.png': 40,        # iPad Spotlight
        'icon-29.png': 29,        # iPhone Settings
        'icon-20.png': 20,        # iPad Notification
    },
    
    # Android sizes
    'android': {
        'ic_launcher-512.png': 512,   # Play Store
        'ic_launcher-192.png': 192,   # xxxhdpi
        'ic_launcher-144.png': 144,   # xxhdpi
        'ic_launcher-96.png': 96,     # xhdpi
        'ic_launcher-72.png': 72,     # hdpi
        'ic_launcher-48.png': 48,     # mdpi
    },
    
    # Adaptive icons (Android 8+)
    'adaptive': {
        'adaptive_foreground-432.png': 432,
        'adaptive_background-432.png': 432,
    }
}

def check_dependencies():
    """Check if required tools are installed"""
    try:
        subprocess.run(['inkscape', '--version'], 
                      capture_output=True, check=True)
        print("✓ Inkscape found")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Inkscape not found. Please install Inkscape to generate icons.")
        print("  macOS: brew install inkscape")
        print("  Ubuntu: sudo apt install inkscape")
        print("  Windows: Download from https://inkscape.org/")
        return False

def create_directories():
    """Create necessary directories"""
    dirs = ['ios', 'android', 'adaptive']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✓ Created directory: {dir_name}")

def generate_icon(svg_file, output_file, size, platform='ios'):
    """Generate a single icon from SVG"""
    try:
        if platform == 'adaptive' and 'background' in output_file:
            # For adaptive background, create a solid color version
            cmd = [
                'inkscape',
                '--export-png', output_file,
                '--export-width', str(size),
                '--export-height', str(size),
                '--export-background', '#7B2CBF',  # Primary color background
                '--export-background-opacity', '1.0',
                svg_file
            ]
        else:
            cmd = [
                'inkscape', 
                '--export-png', output_file,
                '--export-width', str(size),
                '--export-height', str(size),
                svg_file
            ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✓ Generated {output_file} ({size}x{size})")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to generate {output_file}: {e}")
        return False

def create_adaptive_background(size):
    """Create a simple background for adaptive icons"""
    background_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="bg" cx="50%" cy="30%" r="70%">
      <stop offset="0%" style="stop-color:#7B2CBF;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#3B82F6;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#06B6D4;stop-opacity:1" />
    </radialGradient>
  </defs>
  <rect width="{size}" height="{size}" fill="url(#bg)"/>
</svg>"""
    
    with open('adaptive_background.svg', 'w') as f:
        f.write(background_svg)
    
    return 'adaptive_background.svg'

def main():
    """Main function to generate all icons"""
    print("AstraTrade Icon Generator")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check if SVG exists
    svg_file = '../app_icon_design.svg'
    if not Path(svg_file).exists():
        print(f"✗ SVG file not found: {svg_file}")
        return
    
    # Create directories
    create_directories()
    
    # Generate icons for each platform
    total_icons = 0
    successful_icons = 0
    
    for platform, sizes in ICON_SIZES.items():
        print(f"\nGenerating {platform.upper()} icons...")
        
        for filename, size in sizes.items():
            total_icons += 1
            output_path = f"{platform}/{filename}"
            
            if platform == 'adaptive' and 'background' in filename:
                # Create special background SVG
                bg_svg = create_adaptive_background(size)
                if generate_icon(bg_svg, output_path, size, platform):
                    successful_icons += 1
                os.remove(bg_svg)  # Clean up temp file
            else:
                if generate_icon(svg_file, output_path, size, platform):
                    successful_icons += 1
    
    # Summary
    print(f"\nGeneration complete!")
    print(f"✓ {successful_icons}/{total_icons} icons generated successfully")
    
    if successful_icons < total_icons:
        print(f"✗ {total_icons - successful_icons} icons failed to generate")
    
    # Flutter integration instructions
    print(f"\nNext steps:")
    print(f"1. Copy iOS icons to ios/Runner/Assets.xcassets/AppIcon.appiconset/")
    print(f"2. Copy Android icons to android/app/src/main/res/mipmap-*/")
    print(f"3. Update pubspec.yaml with flutter_launcher_icons configuration")
    print(f"4. Run 'flutter pub get' and 'flutter pub run flutter_launcher_icons:main'")

if __name__ == "__main__":
    main()