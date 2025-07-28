/// Application error types
enum ErrorType {
  network,
  authentication,
  validation,
  business,
  unknown
}

/// Custom application exception
class AppException implements Exception {
  final String message;
  final ErrorType type;
  final dynamic originalError;
  final StackTrace? stackTrace;

  const AppException(
    this.message, {
    this.type = ErrorType.unknown,
    this.originalError,
    this.stackTrace,
  });

  @override
  String toString() => 'AppException: $message';
}

/// Error handler utility
class ErrorHandler {
  static AppException handleError(dynamic error, [StackTrace? stackTrace]) {
    if (error is AppException) {
      return error;
    }

    if (error.toString().contains('SocketException') ||
        error.toString().contains('TimeoutException')) {
      return AppException(
        'Network connection failed',
        type: ErrorType.network,
        originalError: error,
        stackTrace: stackTrace,
      );
    }

    if (error.toString().contains('401') ||
        error.toString().contains('Unauthorized')) {
      return AppException(
        'Authentication failed',
        type: ErrorType.authentication,
        originalError: error,
        stackTrace: stackTrace,
      );
    }

    return AppException(
      error.toString(),
      type: ErrorType.unknown,
      originalError: error,
      stackTrace: stackTrace,
    );
  }
}
