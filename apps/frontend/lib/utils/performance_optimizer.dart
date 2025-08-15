import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';

/// Performance optimization utilities for smooth 60fps experience
class PerformanceOptimizer {
  static bool _isPerformanceLoggingEnabled = false;
  static final List<double> _frameTimes = [];
  static const int _maxFrameTimesSamples = 60;

  /// Enable performance logging for debugging
  static void enablePerformanceLogging() {
    _isPerformanceLoggingEnabled = true;
  }

  /// Log frame performance
  static void logFrameTime(Duration frameTime) {
    if (!_isPerformanceLoggingEnabled) return;

    _frameTimes.add(frameTime.inMicroseconds / 1000.0); // Convert to milliseconds
    
    if (_frameTimes.length > _maxFrameTimesSamples) {
      _frameTimes.removeAt(0);
    }

    // Log if frame time is too high (over 16.67ms for 60fps)
    if (frameTime.inMicroseconds > 16670) {
      debugPrint('⚠️ Slow frame detected: ${frameTime.inMicroseconds / 1000.0}ms');
    }
  }

  /// Get average FPS over recent frames
  static double getAverageFPS() {
    if (_frameTimes.isEmpty) return 0.0;
    
    final averageFrameTime = _frameTimes.reduce((a, b) => a + b) / _frameTimes.length;
    return 1000.0 / averageFrameTime; // Convert ms to FPS
  }

  /// Check if app is performing well (above 55 FPS)
  static bool isPerformingWell() {
    return getAverageFPS() > 55.0;
  }

  /// Optimize widget build performance
  static Widget optimizeRebuild({
    required Widget child,
    List<Object?>? dependencies,
  }) {
    return RepaintBoundary(
      child: dependencies != null
          ? Selector<Object?, Object?>(
              selector: (context, value) => dependencies.hashCode,
              builder: (context, value, child) => child!,
              child: child,
            )
          : child,
    );
  }

  /// Debounce function calls to prevent excessive rebuilds
  static Function debounce(Function func, Duration delay) {
    Timer? timer;
    return () {
      timer?.cancel();
      timer = Timer(delay, func as void Function());
    };
  }

  /// Throttle function calls to limit frequency
  static Function throttle(Function func, Duration interval) {
    DateTime? lastCall;
    return () {
      final now = DateTime.now();
      if (lastCall == null || now.difference(lastCall!) >= interval) {
        lastCall = now;
        func();
      }
    };
  }
}

/// Custom selector widget for granular rebuilds
class Selector<T, S> extends StatefulWidget {
  final S Function(BuildContext, T) selector;
  final Widget Function(BuildContext, S, Widget?) builder;
  final Widget? child;

  const Selector({
    super.key,
    required this.selector,
    required this.builder,
    this.child,
  });

  @override
  State<Selector<T, S>> createState() => _SelectorState<T, S>();
}

class _SelectorState<T, S> extends State<Selector<T, S>> {
  S? _selectedValue;

  @override
  Widget build(BuildContext context) {
    // This is a simplified selector - in a real app, you'd use Provider.of<T>()
    // For demo purposes, we'll just call the builder
    final newValue = widget.selector(context, null as T);
    
    if (_selectedValue != newValue) {
      _selectedValue = newValue;
    }

    return widget.builder(context, _selectedValue as S, widget.child);
  }
}

/// Performance-optimized list view for large datasets
class OptimizedListView extends StatelessWidget {
  final int itemCount;
  final Widget Function(BuildContext context, int index) itemBuilder;
  final ScrollPhysics? physics;
  final EdgeInsets? padding;
  final bool shrinkWrap;

  const OptimizedListView({
    super.key,
    required this.itemCount,
    required this.itemBuilder,
    this.physics,
    this.padding,
    this.shrinkWrap = false,
  });

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: itemCount,
      physics: physics,
      padding: padding,
      shrinkWrap: shrinkWrap,
      cacheExtent: 500.0, // Cache items for smoother scrolling
      itemBuilder: (context, index) {
        // Wrap each item in RepaintBoundary for better performance
        return RepaintBoundary(
          child: itemBuilder(context, index),
        );
      },
    );
  }
}

/// Performance-aware animation controller
class OptimizedAnimationController extends AnimationController {
  OptimizedAnimationController({
    required Duration duration,
    required TickerProvider vsync,
    Duration? reverseDuration,
    String? debugLabel,
    double lowerBound = 0.0,
    double upperBound = 1.0,
    AnimationBehavior animationBehavior = AnimationBehavior.normal,
  }) : super(
          duration: duration,
          reverseDuration: reverseDuration,
          debugLabel: debugLabel,
          lowerBound: lowerBound,
          upperBound: upperBound,
          vsync: vsync,
          animationBehavior: animationBehavior,
        );

  @override
  void addListener(VoidCallback listener) {
    // Throttle listener calls to prevent excessive rebuilds
    super.addListener(
      PerformanceOptimizer.throttle(
        listener,
        const Duration(milliseconds: 16), // ~60fps
      ) as VoidCallback,
    );
  }
}

/// Lazy loading widget for expensive content
class LazyBuilder extends StatefulWidget {
  final Widget Function(BuildContext context) builder;
  final Widget? placeholder;
  final bool shouldBuild;

  const LazyBuilder({
    super.key,
    required this.builder,
    this.placeholder,
    this.shouldBuild = true,
  });

  @override
  State<LazyBuilder> createState() => _LazyBuilderState();
}

class _LazyBuilderState extends State<LazyBuilder> {
  Widget? _builtWidget;
  bool _isBuilt = false;

  @override
  Widget build(BuildContext context) {
    if (!widget.shouldBuild) {
      return widget.placeholder ?? const SizedBox.shrink();
    }

    if (!_isBuilt) {
      // Build in the next frame to avoid blocking current frame
      SchedulerBinding.instance.addPostFrameCallback((_) {
        if (mounted) {
          setState(() {
            _builtWidget = widget.builder(context);
            _isBuilt = true;
          });
        }
      });

      return widget.placeholder ?? const SizedBox.shrink();
    }

    return _builtWidget!;
  }
}

/// Memory-efficient image widget
class OptimizedImage extends StatelessWidget {
  final String imageUrl;
  final double? width;
  final double? height;
  final BoxFit fit;
  final Widget? placeholder;
  final Widget? errorWidget;

  const OptimizedImage({
    super.key,
    required this.imageUrl,
    this.width,
    this.height,
    this.fit = BoxFit.cover,
    this.placeholder,
    this.errorWidget,
  });

  @override
  Widget build(BuildContext context) {
    return RepaintBoundary(
      child: Image.network(
        imageUrl,
        width: width,
        height: height,
        fit: fit,
        cacheWidth: width?.round(),
        cacheHeight: height?.round(),
        loadingBuilder: (context, child, loadingProgress) {
          if (loadingProgress == null) return child;
          
          return placeholder ?? 
              const Center(child: CircularProgressIndicator());
        },
        errorBuilder: (context, error, stackTrace) {
          return errorWidget ?? 
              const Icon(Icons.error, color: Colors.grey);
        },
      ),
    );
  }
}

/// Performance monitoring widget
class PerformanceMonitor extends StatefulWidget {
  final Widget child;
  final bool showOverlay;

  const PerformanceMonitor({
    super.key,
    required this.child,
    this.showOverlay = false,
  });

  @override
  State<PerformanceMonitor> createState() => _PerformanceMonitorState();
}

class _PerformanceMonitorState extends State<PerformanceMonitor> {
  late Timer _timer;
  double _currentFPS = 0.0;

  @override
  void initState() {
    super.initState();
    
    if (widget.showOverlay) {
      PerformanceOptimizer.enablePerformanceLogging();
      
      _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
        setState(() {
          _currentFPS = PerformanceOptimizer.getAverageFPS();
        });
      });
    }
  }

  @override
  void dispose() {
    _timer.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        widget.child,
        
        if (widget.showOverlay)
          Positioned(
            top: 50,
            right: 16,
            child: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: _currentFPS > 55 ? Colors.green : Colors.red,
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                'FPS: ${_currentFPS.toStringAsFixed(1)}',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
      ],
    );
  }
}

/// Extension methods for performance optimization
extension PerformanceExtensions on Widget {
  /// Wrap widget in RepaintBoundary for better performance
  Widget optimizeRepaints() {
    return RepaintBoundary(child: this);
  }

  /// Add performance monitoring
  Widget withPerformanceMonitoring({bool showOverlay = false}) {
    return PerformanceMonitor(
      showOverlay: showOverlay,
      child: this,
    );
  }

  /// Make widget build lazily
  Widget buildLazily({
    Widget? placeholder,
    bool shouldBuild = true,
  }) {
    return LazyBuilder(
      builder: (context) => this,
      placeholder: placeholder,
      shouldBuild: shouldBuild,
    );
  }
}

/// Timer extension for performance
extension Timer on int {
  Timer periodic(Duration period, void Function(Timer) callback) {
    return Timer.periodic(period, callback);
  }
}