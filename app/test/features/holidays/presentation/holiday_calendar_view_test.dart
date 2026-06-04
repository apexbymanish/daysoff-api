import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:daysoff_app/features/holidays/domain/entities/holiday.dart';
import 'package:daysoff_app/features/holidays/presentation/widgets/holiday_calendar_view.dart';

void main() {
  testWidgets('shows the first holiday\'s month and marks its day', (tester) async {
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: HolidayCalendarView(holidays: [
          Holiday(date: DateTime(2026, 5, 5), name: "Children's Day", source: 's'),
        ]),
      ),
    ));
    expect(find.text('May 2026'), findsOneWidget);
    // Day cell "5" rendered as a holiday-marked cell.
    expect(find.byKey(const ValueKey('holiday-day-2026-05-05')), findsOneWidget);
  });
}
