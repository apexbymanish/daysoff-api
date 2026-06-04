import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:daysoff_app/features/holidays/domain/entities/holiday.dart';
import 'package:daysoff_app/features/holidays/presentation/widgets/holiday_detail_sheet.dart';

void main() {
  testWidgets('renders holiday name, full date and status', (tester) async {
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: HolidayDetailSheetBody(
          holiday: Holiday(date: DateTime(2026, 9, 25), name: 'Chuseok', source: 's'),
        ),
      ),
    ));
    expect(find.text('Chuseok'), findsOneWidget);
    expect(find.textContaining('Friday'), findsOneWidget); // 2026-09-25 is a Friday
    expect(find.textContaining('free'), findsOneWidget);
  });
}
