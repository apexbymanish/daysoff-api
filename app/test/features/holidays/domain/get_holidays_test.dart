import 'package:fpdart/fpdart.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:daysoff_app/core/error/failure.dart';
import 'package:daysoff_app/features/holidays/domain/entities/holiday.dart';
import 'package:daysoff_app/features/holidays/domain/repositories/holiday_repository.dart';
import 'package:daysoff_app/features/holidays/domain/usecases/get_holidays.dart';

class _MockRepo extends Mock implements HolidayRepository {}

void main() {
  late _MockRepo repo;
  late GetHolidays usecase;

  setUp(() {
    repo = _MockRepo();
    usecase = GetHolidays(repo);
  });

  final sample = [
    Holiday(date: DateTime(2026, 1, 1), name: "New Year's Day", source: 's'),
  ];

  test('delegates to repository and returns its Right result', () async {
    when(() => repo.getHolidays(country: 'KR', year: 2026))
        .thenAnswer((_) async => Right(sample));

    final result = await usecase(country: 'KR', year: 2026);

    expect(result, Right<Failure, List<Holiday>>(sample));
    verify(() => repo.getHolidays(country: 'KR', year: 2026)).called(1);
  });

  test('passes through a Left failure', () async {
    when(() => repo.getHolidays(country: 'KR', year: 2026))
        .thenAnswer((_) async => const Left(NetworkFailure()));

    final result = await usecase(country: 'KR', year: 2026);

    expect(result.isLeft(), isTrue);
  });
}
