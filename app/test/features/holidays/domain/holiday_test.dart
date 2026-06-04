import 'package:flutter_test/flutter_test.dart';
import 'package:daysoff_app/features/holidays/domain/entities/holiday.dart';

void main() {
  Holiday h(String iso) =>
      Holiday(date: DateTime.parse(iso), name: 'X', source: 's');

  test('weekday holiday is free (Children\'s Day 2026-05-05 is a Tuesday)', () {
    final c = h('2026-05-05');
    expect(c.date.weekday, DateTime.tuesday);
    expect(c.isOnWeekend(), isFalse);
    expect(c.status(), HolidayStatus.free);
  });

  test('weekend holiday is absorbed (2026-03-01 Independence Day is a Sunday)', () {
    final d = h('2026-03-01');
    expect(d.date.weekday, DateTime.sunday);
    expect(d.isOnWeekend(), isTrue);
    expect(d.status(), HolidayStatus.absorbed);
  });

  test('Chuseok 2026-09-26 (Saturday) is absorbed', () {
    expect(h('2026-09-26').status(), HolidayStatus.absorbed);
  });

  test('custom weekend set is honored (Fri/Sat off)', () {
    // 2026-10-09 Hangul Day is a Friday → absorbed when Fri is a weekend
    expect(h('2026-10-09').status({DateTime.friday, DateTime.saturday}),
        HolidayStatus.absorbed);
  });

  test('value equality by date+name+source', () {
    expect(h('2026-01-01'), equals(h('2026-01-01')));
  });
}
