# AstraTrade Flutter Typography Documentation

## Overview
AstraTrade uses a cosmic-themed typography system with two primary Google Fonts to create a futuristic, space-trading aesthetic. The typography follows a hierarchical structure from large titles to small captions, with consistent styling across all screens.

## Primary Font Families

### 1. GoogleFonts.orbitron()
- **Usage**: Titles, headings, app names, important labels, navigation items
- **Characteristics**: Futuristic, tech-inspired, geometric letterforms
- **Primary applications**: Brand identity, screen titles, button labels, data displays

### 2. GoogleFonts.rajdhani()
- **Usage**: Body text, descriptions, secondary content, captions
- **Characteristics**: Modern, readable, clean lines
- **Primary applications**: Descriptions, help text, secondary information

### 3. GoogleFonts.roboto() 
- **Usage**: Minimal usage for loading messages and system text
- **Characteristics**: Standard, highly readable
- **Primary applications**: System messages, fallback text

## Typography Hierarchy

### App-Level Theme Configuration (main.dart)
```dart
// Base text theme using Rajdhani
textTheme: GoogleFonts.rajdhaniTextTheme(ThemeData.dark().textTheme)

// AppBar title style using Orbitron
titleTextStyle: GoogleFonts.orbitron(
  fontSize: 20,
  fontWeight: FontWeight.bold,
  color: Colors.white,
)
```

## Screen-by-Screen Typography Analysis

### 1. Splash Screen (splash_screen.dart)
#### App Title
- **Font**: GoogleFonts.orbitron
- **Size**: 38px
- **Weight**: w900 (Extra Bold)
- **Color**: White with gradient shader mask
- **Letter Spacing**: 4px
- **Usage**: Main app name display

#### Tagline
- **Font**: GoogleFonts.rajdhani
- **Size**: 20px
- **Weight**: w600 (Semi Bold)
- **Color**: Cyan (#06B6D4)
- **Letter Spacing**: 2px
- **Effects**: Glow shadow

#### Loading Text
- **Font**: GoogleFonts.roboto
- **Size**: 15px
- **Weight**: Normal
- **Color**: White70
- **Letter Spacing**: 1px

### 2. Login Screen (login_screen.dart)
#### App Name
- **Font**: GoogleFonts.orbitron
- **Size**: 42px
- **Weight**: Bold
- **Color**: White with gradient shader
- **Letter Spacing**: 4px

#### Welcome Title
- **Font**: GoogleFonts.rajdhani
- **Size**: 20px
- **Weight**: w500 (Medium)
- **Color**: Cyan shade 300
- **Letter Spacing**: 1.5px

#### Subtitle
- **Font**: GoogleFonts.rajdhani
- **Size**: 16px
- **Weight**: Normal
- **Color**: Purple shade 300
- **Letter Spacing**: 1px

#### Demo Indicator
- **Font**: GoogleFonts.rajdhani
- **Size**: 14px
- **Weight**: w600 (Semi Bold)
- **Color**: Cyan shade 300
- **Letter Spacing**: 0.8px

#### Footer Credit
- **Font**: GoogleFonts.rajdhani
- **Size**: 14px
- **Weight**: w600 (Semi Bold)
- **Color**: Blue shade 300
- **Letter Spacing**: 0.5px

### 3. Main Hub Screen (main_hub_screen.dart)
#### Screen Title (AppBar)
- **Font**: GoogleFonts.orbitron
- **Size**: 16-20px (responsive)
- **Weight**: Bold
- **Letter Spacing**: 1.5px
- **Responsive**: Scales down on narrow screens

#### Cosmic Tier Display
- **Font**: GoogleFonts.orbitron
- **Size**: 18px
- **Weight**: Bold
- **Color**: White

#### Game Stats Values
- **Font**: GoogleFonts.orbitron
- **Size**: 20px
- **Weight**: Bold
- **Color**: Variable (cyan, purple, orange)

#### Game Stats Labels
- **Font**: GoogleFonts.rajdhani
- **Size**: 12px (suffix), 10px (label)
- **Weight**: w600 (suffix), Normal (label)
- **Color**: Color with opacity, grey shade 400

#### Section Headers
- **Font**: GoogleFonts.orbitron
- **Size**: 18-20px
- **Weight**: Bold
- **Color**: White

#### Market Pulse Data
- **Font**: GoogleFonts.orbitron
- **Size**: 14px
- **Weight**: Bold
- **Color**: Variable by context

#### Button Labels
- **Font**: GoogleFonts.orbitron
- **Size**: 12px
- **Weight**: Bold
- **Color**: White

#### Action Button Descriptions
- **Font**: GoogleFonts.rajdhani
- **Size**: 10px
- **Weight**: w500 (Medium)
- **Color**: White with opacity

#### Planet Health Status
- **Font**: GoogleFonts.rajdhani
- **Size**: 12px
- **Weight**: w600 (Semi Bold)
- **Color**: Variable by health status

#### Trade Statistics
- **Font**: GoogleFonts.orbitron (values), GoogleFonts.rajdhani (labels)
- **Size**: 16px (values), 10px (labels)
- **Weight**: Bold (values), Normal (labels)

#### Dialog Headers
- **Font**: GoogleFonts.orbitron
- **Size**: 16px
- **Weight**: Bold
- **Color**: Variable by context

#### Dialog Body Text
- **Font**: GoogleFonts.rajdhani
- **Size**: 12-14px
- **Weight**: Normal to w500
- **Color**: Grey shades

### 4. Trading Screen (trading_screen.dart)
#### App Title
- **Font**: Standard TextStyle (not Google Fonts)
- **Size**: Default
- **Weight**: Bold
- **Color**: White

#### Trading Pair Labels
- **Font**: Standard TextStyle
- **Size**: 14px (symbol), 12px (price), 11px (change)
- **Weight**: Bold (symbol), w600 (price), w500 (change)
- **Color**: Context-dependent

#### Market Overview
- **Font**: Standard TextStyle
- **Size**: 18px (header), 11px (titles), 16px (values)
- **Weight**: Bold (header, values), w500 (titles)

### 5. Navigation Bar (cosmic_navigation_bar.dart)
#### Navigation Labels
- **Font**: GoogleFonts.rajdhani
- **Size**: 11px
- **Weight**: Bold (active), w500 (inactive)
- **Color**: Purple (active), Grey shade 500 (inactive)

## Widget-Specific Typography Patterns

### Cosmic Market Pulse Widget
- **Pair Names**: GoogleFonts.orbitron, 12px, Bold
- **Prices**: GoogleFonts.orbitron, 14px, Bold
- **Changes**: GoogleFonts.rajdhani, 11-12px, w500-w600
- **Labels**: GoogleFonts.rajdhani, 10-12px, Normal

### Lumina Resource Widget
- **Values**: GoogleFonts.orbitron, 14-16px, Bold
- **Labels**: GoogleFonts.rajdhani, 10-12px, w500-w600
- **Descriptions**: GoogleFonts.rajdhani, 11-12px, Normal

### Social Sharing Widget
- **Headers**: GoogleFonts.orbitron, 16-18px, Bold
- **Content**: GoogleFonts.orbitron, 12-16px, Bold
- **Descriptions**: Standard text styles

### Notification Widget
- **Titles**: Standard TextStyle, 14-18px, Bold
- **Counts**: Standard TextStyle, 10px, Bold
- **Content**: Standard TextStyle, 12-16px, Variable weights

### Forge Parameters Overlay
- **Actions**: GoogleFonts.orbitron, 14px, Bold
- **Values**: GoogleFonts.orbitron, 16px, Bold
- **Labels**: GoogleFonts.rajdhani, 11-12px, w500

## Typography Constants (utils/constants.dart)

```dart
// Text Style Constants
static const double titleFontSize = 32.0;
static const double subtitleFontSize = 18.0;
static const double bodyFontSize = 16.0;
static const double captionFontSize = 14.0;
```

## Common Typography Patterns by Usage

### Large Titles (App Name, Screen Headers)
- **Font**: GoogleFonts.orbitron
- **Size**: 32-42px
- **Weight**: Bold to w900
- **Letter Spacing**: 2-4px
- **Effects**: Often with gradient shaders or glows

### Medium Headers (Section Titles)
- **Font**: GoogleFonts.orbitron
- **Size**: 18-20px
- **Weight**: Bold
- **Color**: White or theme colors

### Data Display (Stats, Values)
- **Font**: GoogleFonts.orbitron
- **Size**: 14-20px
- **Weight**: Bold
- **Color**: Context-dependent (cyan, purple, orange, green)

### Body Text (Descriptions, Help)
- **Font**: GoogleFonts.rajdhani
- **Size**: 12-16px
- **Weight**: Normal to w600
- **Color**: Grey shades or white

### Small Labels (Suffixes, Units)
- **Font**: GoogleFonts.rajdhani
- **Size**: 10-12px
- **Weight**: w500-w600
- **Color**: Reduced opacity versions of primary colors

### Button Text
- **Font**: GoogleFonts.orbitron
- **Size**: 12-16px
- **Weight**: Bold
- **Color**: White or theme colors

### Navigation Elements
- **Font**: GoogleFonts.rajdhani
- **Size**: 11-14px
- **Weight**: w500-Bold
- **Color**: Theme purple or grey

### Captions (Error Messages, System Text)
- **Font**: GoogleFonts.rajdhani or GoogleFonts.roboto
- **Size**: 10-14px
- **Weight**: Normal to w500
- **Color**: Grey shades

## Special Typography Effects

### Gradient Text Shaders
Used on splash screen and login screen for app name:
```dart
ShaderMask(
  shaderCallback: (bounds) => LinearGradient(
    colors: [Colors.purple.shade300, Colors.blue.shade300, Colors.cyan.shade300]
  ).createShader(bounds),
  child: Text(..., style: GoogleFonts.orbitron(...))
)
```

### Glow Effects
Used for emphasized text:
```dart
shadows: [
  Shadow(
    color: Colors.cyan.withOpacity(0.8),
    blurRadius: 10,
  ),
]
```

### Letter Spacing Variations
- **Tight**: 0.5-1px (small labels)
- **Normal**: 1-1.5px (body text)
- **Wide**: 2-4px (titles, brand text)

## Responsive Typography

### Dynamic Font Scaling (Main Hub Screen)
```dart
double fontSize = 20.0;
if (constraints.maxWidth < 300) {
  fontSize = 16.0;
} else if (constraints.maxWidth < 350) {
  fontSize = 18.0;
}
```

## Accessibility Considerations

1. **Contrast**: All text meets WCAG guidelines with high contrast against dark backgrounds
2. **Font Sizes**: Minimum 10px for captions, typically 12px+ for body text
3. **Font Weights**: Bold used for emphasis and hierarchy
4. **Letter Spacing**: Adequate spacing for readability

## Color Associations by Typography Usage

### Orbitron Font Colors
- **White**: Primary titles, headers
- **Cyan (#06B6D4)**: Trading data, positive values
- **Purple (#7B2CBF)**: Theme accents, navigation
- **Orange**: Experience points, warnings
- **Green**: Positive changes, success states
- **Red**: Negative changes, errors

### Rajdhani Font Colors
- **White**: Primary body text
- **Grey Shades**: Secondary text, labels
- **Cyan**: Accented body text
- **Purple**: Theme-related content

## Implementation Notes

1. **Performance**: Google Fonts are loaded once and reused throughout the app
2. **Consistency**: Use GoogleFonts.orbitron for data/titles, GoogleFonts.rajdhani for descriptions
3. **Fallbacks**: Standard TextStyle used in some legacy widgets (trading_screen.dart, notification_widget.dart)
4. **Theme Integration**: Typography integrates with the overall cosmic/space theme through font choices and effects

This typography system creates a cohesive, futuristic aesthetic that reinforces AstraTrade's cosmic trading theme while maintaining excellent readability and user experience.