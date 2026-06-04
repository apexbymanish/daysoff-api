import 'package:fpdart/fpdart.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:daysoff_app/core/error/failure.dart';
import 'package:daysoff_app/features/holidays/domain/entities/holiday.dart';
import 'package:daysoff_app/features/holidays/domain/repositories/holiday_repository.dart';
import 'package:daysoff_app/features/holidays/domain/usecases/get_holidays.dart';
import 'package:daysoff_app/features/holidays/presentation/controllers/holidays_controller.dart';

class _MockRepo extends Mock implements HolidayRepository {}

void main() {
  late _MockRepo repo;
  late GetHolidays usecase;

  setUp(() {
    repo = _MockRepo();
    usecase = GetHolidays(repo);
  });

  final feb = [
    Holiday(date: DateTime(2026, 2, 17), name: 'Korean New Year', source: 's'),
    Holiday(date: DateTime(2026, 5, 5), name: "Children's Day", source: 's'),
  ];

  test('load(): loading -> loaded and groups by month', () async {
    when(() => repo.getHolidays(country: 'KR', year: 2026))
        .thenAnswer((_) async => Right(feb));
    final c = HolidaysController(usecase);

    await c.load();

    expect(c.status.value, HolidaysViewStatus.loaded);
    expect(c.holidays.length, 2);
    expect(c.holidaysByMonth.keys.toList(), ['February', 'May']);
    expect(c.holidaysByMonth['February']!.single.name, 'Korean New Year');
  });

  test('load(): empty list -> empty status', () async {
    when(() => repo.getHolidays(country: 'KR', year: 2026))
        .thenAnswer((_) async => const Right<Failure, List<Holiday>>([]));
    final c = HolidaysController(usecase);

    await c.load();

    expect(c.status.value, HolidaysViewStatus.empty);
  });

  test('load(): failure -> error status with message', () async {
    when(() => repo.getHolidays(country: 'KR', year: 2026))
        .thenAnswer((_) async => const Left(NetworkFailure()));
    final c = HolidaysController(usecase);

    await c.load();

    expect(c.status.value, HolidaysViewStatus.error);
    expect(c.errorMessage.value, isNotEmpty);
  });

  test('toggleView flips calendar/timeline', () {
    final c = HolidaysController(usecase);
    expect(c.isCalendarView.value, isFalse);
    c.toggleView();
    expect(c.isCalendarView.value, isTrue);
  });
}
