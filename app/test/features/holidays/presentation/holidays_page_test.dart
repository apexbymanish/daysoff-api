import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';
import 'package:mocktail/mocktail.dart';
import 'package:fpdart/fpdart.dart';
import 'package:daysoff_app/core/error/failure.dart';
import 'package:daysoff_app/features/holidays/domain/entities/holiday.dart';
import 'package:daysoff_app/features/holidays/domain/repositories/holiday_repository.dart';
import 'package:daysoff_app/features/holidays/domain/usecases/get_holidays.dart';
import 'package:daysoff_app/features/holidays/presentation/controllers/holidays_controller.dart';
import 'package:daysoff_app/features/holidays/presentation/pages/holidays_page.dart';

class _MockRepo extends Mock implements HolidayRepository {}

void main() {
  setUp(() => Get.testMode = true);
  tearDown(Get.reset);

  Future<void> pumpWith(WidgetTester tester, _MockRepo repo) async {
    Get.put<HolidaysController>(HolidaysController(GetHolidays(repo)));
    await tester.pumpWidget(const GetMaterialApp(home: HolidaysPage()));
  }

  testWidgets('loaded state shows month header and a holiday row', (tester) async {
    final repo = _MockRepo();
    when(() => repo.getHolidays(country: 'KR', year: 2026)).thenAnswer((_) async =>
        Right([Holiday(date: DateTime(2026, 5, 5), name: "Children's Day", source: 's')]));
    await pumpWith(tester, repo);
    await tester.pumpAndSettle();
    expect(find.text('May'), findsOneWidget);
    expect(find.text("Children's Day"), findsOneWidget);
  });

  testWidgets('error state shows message and retry', (tester) async {
    final repo = _MockRepo();
    when(() => repo.getHolidays(country: 'KR', year: 2026))
        .thenAnswer((_) async => const Left(NetworkFailure()));
    await pumpWith(tester, repo);
    await tester.pumpAndSettle();
    expect(find.text('Retry'), findsOneWidget);
  });
}
