import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:daysoff_app/core/error/failure.dart';
import 'package:daysoff_app/features/holidays/data/datasources/holiday_remote_data_source.dart';
import 'package:daysoff_app/features/holidays/data/models/holiday_dto.dart';
import 'package:daysoff_app/features/holidays/data/repositories/holiday_repository_impl.dart';

class _MockRemote extends Mock implements HolidayRemoteDataSource {}

void main() {
  late _MockRemote remote;
  late HolidayRepositoryImpl repo;

  setUp(() {
    remote = _MockRemote();
    repo = HolidayRepositoryImpl(remote);
  });

  test('maps DTOs to entities sorted by date on success', () async {
    when(() => remote.fetchHolidays(country: 'KR', year: 2026))
        .thenAnswer((_) async => const [
              HolidayDto(date: '2026-09-25', name: 'Chuseok', source: 's'),
              HolidayDto(date: '2026-01-01', name: "New Year's Day", source: 's'),
            ]);

    final result = await repo.getHolidays(country: 'KR', year: 2026);

    final list = result.getRight().toNullable()!;
    expect(list.first.date, DateTime(2026, 1, 1)); // sorted ascending
    expect(list.last.name, 'Chuseok');
  });

  test('connection error maps to NetworkFailure', () async {
    when(() => remote.fetchHolidays(country: 'KR', year: 2026)).thenThrow(
      DioException(
        requestOptions: RequestOptions(path: '/v1/holidays'),
        type: DioExceptionType.connectionError,
      ),
    );

    final result = await repo.getHolidays(country: 'KR', year: 2026);

    expect(result.isLeft(), isTrue);
    result.match((f) => expect(f, isA<NetworkFailure>()), (_) => fail('expected Left'));
  });

  test('non-connection error maps to ServerFailure', () async {
    when(() => remote.fetchHolidays(country: 'KR', year: 2026)).thenThrow(
      DioException(
        requestOptions: RequestOptions(path: '/v1/holidays'),
        type: DioExceptionType.badResponse,
      ),
    );

    final result = await repo.getHolidays(country: 'KR', year: 2026);

    result.match((f) => expect(f, isA<ServerFailure>()), (_) => fail('expected Left'));
  });
}
