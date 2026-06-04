import 'package:flutter_test/flutter_test.dart';
import 'package:daysoff_app/features/holidays/data/models/holiday_dto.dart';
import 'package:daysoff_app/features/holidays/domain/entities/holiday.dart';

void main() {
  test('fromJson parses the /v1/holidays record shape', () {
    final dto = HolidayDto.fromJson(const {
      'date': '2026-09-25',
      'name': 'Chuseok',
      'source': 'holidays-lib',
    });
    expect(dto.date, '2026-09-25');
    expect(dto.name, 'Chuseok');
    expect(dto.source, 'holidays-lib');
  });

  test('toEntity converts ISO date string to DateTime', () {
    final entity = HolidayDto.fromJson(const {
      'date': '2026-09-25',
      'name': 'Chuseok',
      'source': 'holidays-lib',
    }).toEntity();
    expect(entity, isA<Holiday>());
    expect(entity.date, DateTime(2026, 9, 25));
    expect(entity.name, 'Chuseok');
  });
}
