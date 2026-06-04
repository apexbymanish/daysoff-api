import 'package:flutter_test/flutter_test.dart';
import 'package:daysoff_app/core/error/failure.dart';

void main() {
  test('failures carry a user-facing message and are matchable by type', () {
    const Failure f = NetworkFailure();
    expect(f, isA<NetworkFailure>());
    expect(f.message, isNotEmpty);

    final result = switch (const ServerFailure('boom')) {
      NetworkFailure() => 'net',
      ServerFailure(:final message) => message,
      CacheFailure() => 'cache',
      PermissionFailure() => 'perm',
    };
    expect(result, 'boom');
  });
}
