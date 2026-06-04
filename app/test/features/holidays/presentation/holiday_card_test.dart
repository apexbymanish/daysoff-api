import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:daysoff_app/features/holidays/domain/entities/holiday.dart';
import 'package:daysoff_app/features/holidays/presentation/widgets/holiday_card.dart';

Widget _host(Widget child) => MaterialApp(home: Scaffold(body: child));

void main() {
  testWidgets('free holiday shows day numeral, weekday, name and "free"',
      (tester) async {
    await tester.pumpWidget(_host(HolidayCard(
      holiday: Holiday(date: DateTime(2026, 5, 5), name: "Children's Day", source: 's'),
      onTap: () {},
    )));
    expect(find.text('5'), findsOneWidget);
    expect(find.text('TUE'), findsOneWidget);
    expect(find.text("Children's Day"), findsOneWidget);
    expect(find.text('free'), findsOneWidget);
  });

  testWidgets('absorbed holiday shows "absorbed"', (tester) async {
    await tester.pumpWidget(_host(HolidayCard(
      holiday: Holiday(date: DateTime(2026, 3, 1), name: 'Independence Movement Day', source: 's'),
      onTap: () {},
    )));
    expect(find.text('absorbed'), findsOneWidget);
  });

  testWidgets('tapping the card fires onTap', (tester) async {
    var tapped = false;
    await tester.pumpWidget(_host(HolidayCard(
      holiday: Holiday(date: DateTime(2026, 5, 5), name: "Children's Day", source: 's'),
      onTap: () => tapped = true,
    )));
    await tester.tap(find.byType(HolidayCard));
    expect(tapped, isTrue);
  });
}
