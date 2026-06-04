import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';
import 'package:daysoff_app/features/holidays/presentation/bindings/holidays_binding.dart';
import 'package:daysoff_app/features/holidays/presentation/controllers/holidays_controller.dart';

void main() {
  setUp(() => Get.testMode = true);
  tearDown(Get.reset);

  test('binding registers a resolvable HolidaysController', () {
    HolidaysBinding().dependencies();
    expect(Get.isRegistered<HolidaysController>(), isTrue);
    expect(Get.find<HolidaysController>(), isA<HolidaysController>());
  });
}
