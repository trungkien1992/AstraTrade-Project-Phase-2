import 'package:flutter/material.dart';

/// Responsive design helper utilities
/// Provides consistent breakpoints and adaptive layouts
class ResponsiveHelper {
  // Standard breakpoints for responsive design
  static const double mobileBreakpoint = 600;
  static const double tabletBreakpoint = 900;
  static const double desktopBreakpoint = 1200;
  static const double largeDesktopBreakpoint = 1600;

  /// Get the current device type based on screen width
  static DeviceType getDeviceType(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    
    if (width < mobileBreakpoint) {
      return DeviceType.mobile;
    } else if (width < tabletBreakpoint) {
      return DeviceType.tablet;
    } else if (width < largeDesktopBreakpoint) {
      return DeviceType.desktop;
    } else {
      return DeviceType.largeDesktop;
    }
  }

  /// Check if current device is mobile
  static bool isMobile(BuildContext context) {
    return MediaQuery.of(context).size.width < mobileBreakpoint;
  }

  /// Check if current device is tablet
  static bool isTablet(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    return width >= mobileBreakpoint && width < tabletBreakpoint;
  }

  /// Check if current device is desktop
  static bool isDesktop(BuildContext context) {
    return MediaQuery.of(context).size.width >= tabletBreakpoint;
  }

  /// Get responsive padding based on device type
  static EdgeInsets getResponsivePadding(BuildContext context) {
    if (isMobile(context)) {
      return const EdgeInsets.all(16.0);
    } else if (isTablet(context)) {
      return const EdgeInsets.all(24.0);
    } else {
      return const EdgeInsets.all(32.0);
    }
  }

  /// Get responsive font size
  static double getResponsiveFontSize(BuildContext context, double baseFontSize) {
    final deviceType = getDeviceType(context);
    
    switch (deviceType) {
      case DeviceType.mobile:
        return baseFontSize;
      case DeviceType.tablet:
        return baseFontSize * 1.1;
      case DeviceType.desktop:
        return baseFontSize * 1.2;
      case DeviceType.largeDesktop:
        return baseFontSize * 1.3;
    }
  }

  /// Get adaptive column count for grid layouts
  static int getAdaptiveColumns(BuildContext context, {int baseColumns = 2}) {
    final deviceType = getDeviceType(context);
    
    switch (deviceType) {
      case DeviceType.mobile:
        return baseColumns;
      case DeviceType.tablet:
        return (baseColumns * 1.5).round();
      case DeviceType.desktop:
        return baseColumns * 2;
      case DeviceType.largeDesktop:
        return baseColumns * 3;
    }
  }

  /// Get responsive icon size
  static double getResponsiveIconSize(BuildContext context, double baseSize) {
    final deviceType = getDeviceType(context);
    
    switch (deviceType) {
      case DeviceType.mobile:
        return baseSize;
      case DeviceType.tablet:
        return baseSize * 1.2;
      case DeviceType.desktop:
        return baseSize * 1.4;
      case DeviceType.largeDesktop:
        return baseSize * 1.6;
    }
  }

  /// Get maximum content width for better readability on large screens
  static double getMaxContentWidth(BuildContext context) {
    final deviceType = getDeviceType(context);
    
    switch (deviceType) {
      case DeviceType.mobile:
      case DeviceType.tablet:
        return double.infinity;
      case DeviceType.desktop:
        return 800;
      case DeviceType.largeDesktop:
        return 1000;
    }
  }

  /// Get responsive card constraints
  static BoxConstraints getCardConstraints(BuildContext context) {
    final deviceType = getDeviceType(context);
    
    switch (deviceType) {
      case DeviceType.mobile:
        return const BoxConstraints(
          minHeight: 120,
          maxWidth: double.infinity,
        );
      case DeviceType.tablet:
        return const BoxConstraints(
          minHeight: 140,
          maxWidth: 400,
        );
      case DeviceType.desktop:
        return const BoxConstraints(
          minHeight: 160,
          maxWidth: 450,
        );
      case DeviceType.largeDesktop:
        return const BoxConstraints(
          minHeight: 180,
          maxWidth: 500,
        );
    }
  }

  /// Get responsive button size
  static Size getButtonSize(BuildContext context, ButtonSize buttonSize) {
    final deviceType = getDeviceType(context);
    final scaleFactor = _getScaleFactor(deviceType);
    
    switch (buttonSize) {
      case ButtonSize.small:
        return Size(120 * scaleFactor, 36 * scaleFactor);
      case ButtonSize.medium:
        return Size(160 * scaleFactor, 48 * scaleFactor);
      case ButtonSize.large:
        return Size(200 * scaleFactor, 56 * scaleFactor);
      case ButtonSize.extraLarge:
        return Size(240 * scaleFactor, 64 * scaleFactor);
    }
  }

  static double _getScaleFactor(DeviceType deviceType) {
    switch (deviceType) {
      case DeviceType.mobile:
        return 1.0;
      case DeviceType.tablet:
        return 1.1;
      case DeviceType.desktop:
        return 1.2;
      case DeviceType.largeDesktop:
        return 1.3;
    }
  }
}

/// Device types for responsive design
enum DeviceType {
  mobile,
  tablet,
  desktop,
  largeDesktop,
}

/// Button sizes for responsive scaling
enum ButtonSize {
  small,
  medium,
  large,
  extraLarge,
}

/// Responsive layout builder widget
class ResponsiveBuilder extends StatelessWidget {
  final Widget Function(BuildContext context, DeviceType deviceType) builder;
  final Widget? mobile;
  final Widget? tablet;
  final Widget? desktop;
  final Widget? largeDesktop;

  const ResponsiveBuilder({
    super.key,
    required this.builder,
    this.mobile,
    this.tablet,
    this.desktop,
    this.largeDesktop,
  });

  @override
  Widget build(BuildContext context) {
    final deviceType = ResponsiveHelper.getDeviceType(context);

    // Use specific layouts if provided
    switch (deviceType) {
      case DeviceType.mobile:
        if (mobile != null) return mobile!;
        break;
      case DeviceType.tablet:
        if (tablet != null) return tablet!;
        break;
      case DeviceType.desktop:
        if (desktop != null) return desktop!;
        break;
      case DeviceType.largeDesktop:
        if (largeDesktop != null) return largeDesktop!;
        break;
    }

    // Fallback to builder function
    return builder(context, deviceType);
  }
}

/// Responsive scaffold that adapts layout based on screen size
class ResponsiveScaffold extends StatelessWidget {
  final Widget body;
  final PreferredSizeWidget? appBar;
  final Widget? drawer;
  final Widget? endDrawer;
  final Widget? floatingActionButton;
  final FloatingActionButtonLocation? floatingActionButtonLocation;
  final Color? backgroundColor;
  final bool extendBodyBehindAppBar;
  final bool extendBody;

  const ResponsiveScaffold({
    super.key,
    required this.body,
    this.appBar,
    this.drawer,
    this.endDrawer,
    this.floatingActionButton,
    this.floatingActionButtonLocation,
    this.backgroundColor,
    this.extendBodyBehindAppBar = false,
    this.extendBody = false,
  });

  @override
  Widget build(BuildContext context) {
    final maxWidth = ResponsiveHelper.getMaxContentWidth(context);
    final responsivePadding = ResponsiveHelper.getResponsivePadding(context);

    return Scaffold(
      appBar: appBar,
      drawer: drawer,
      endDrawer: endDrawer,
      floatingActionButton: floatingActionButton,
      floatingActionButtonLocation: floatingActionButtonLocation,
      backgroundColor: backgroundColor,
      extendBodyBehindAppBar: extendBodyBehindAppBar,
      extendBody: extendBody,
      body: Center(
        child: ConstrainedBox(
          constraints: BoxConstraints(maxWidth: maxWidth),
          child: Padding(
            padding: responsivePadding,
            child: body,
          ),
        ),
      ),
    );
  }
}

/// Responsive grid view that adapts column count based on screen size
class ResponsiveGridView extends StatelessWidget {
  final List<Widget> children;
  final int baseColumns;
  final double mainAxisSpacing;
  final double crossAxisSpacing;
  final double childAspectRatio;
  final ScrollPhysics? physics;

  const ResponsiveGridView({
    super.key,
    required this.children,
    this.baseColumns = 2,
    this.mainAxisSpacing = 8.0,
    this.crossAxisSpacing = 8.0,
    this.childAspectRatio = 1.0,
    this.physics,
  });

  @override
  Widget build(BuildContext context) {
    final columns = ResponsiveHelper.getAdaptiveColumns(
      context,
      baseColumns: baseColumns,
    );

    return GridView.builder(
      physics: physics,
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: columns,
        mainAxisSpacing: mainAxisSpacing,
        crossAxisSpacing: crossAxisSpacing,
        childAspectRatio: childAspectRatio,
      ),
      itemCount: children.length,
      itemBuilder: (context, index) => children[index],
    );
  }
}

/// Responsive text widget that scales font size based on device
class ResponsiveText extends StatelessWidget {
  final String text;
  final double baseFontSize;
  final FontWeight? fontWeight;
  final Color? color;
  final TextAlign? textAlign;
  final int? maxLines;
  final TextOverflow? overflow;

  const ResponsiveText(
    this.text, {
    super.key,
    required this.baseFontSize,
    this.fontWeight,
    this.color,
    this.textAlign,
    this.maxLines,
    this.overflow,
  });

  @override
  Widget build(BuildContext context) {
    final responsiveFontSize = ResponsiveHelper.getResponsiveFontSize(
      context,
      baseFontSize,
    );

    return Text(
      text,
      style: TextStyle(
        fontSize: responsiveFontSize,
        fontWeight: fontWeight,
        color: color,
      ),
      textAlign: textAlign,
      maxLines: maxLines,
      overflow: overflow,
    );
  }
}