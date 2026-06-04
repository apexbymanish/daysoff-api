import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:daysoff_app/features/holidays/data/datasources/holiday_remote_data_source.dart';

class _MockDio extends Mock implements Dio {}

void main() {
  late _MockDio dio;
  late HolidayRemoteDataSource dataSource;

  setUp(() {
    dio = _MockDio();
    dataSource = HolidayRemoteDataSource(dio);
  });

  test('GETs /v1/holidays with country+year and maps the holidays array', () async {
    when(() => dio.get('/v1/holidays',
            queryParameters: {'country': 'KR', 'year': 2026}))
        .thenAnswer((_) async => Response(
              requestOptions: RequestOptions(path: '/v1/holidays'),
              statusCode: 200,
              data: {
                'country': 'KR',
                'year': 2026,
                'count': 2,
                'holidays': [
                  {'date': '2026-01-01', 'name': "New Year's Day", 'source': 's'},
                  {'date': '2026-09-25', 'name': 'Chuseok', 'source': 's'},
                ],
              },
            ));

    final dtos = await dataSource.fetchHolidays(country: 'KR', year: 2026);

    expect(dtos.length, 2);
    expect(dtos.first.name, "New Year's Day");
    expect(dtos.last.date, '2026-09-25');
    verify(() => dio.get('/v1/holidays',
        queryParameters: {'country': 'KR', 'year': 2026})).called(1);
  });
}
