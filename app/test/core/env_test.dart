import 'package:flutter_test/flutter_test.dart';
import 'package:daysoff_app/core/env.dart';

void main() {
  test('apiBaseUrl defaults to the deployed Fly URL', () {
    expect(Env.apiBaseUrl, 'https://daysoff-api.fly.dev');
  });
}
