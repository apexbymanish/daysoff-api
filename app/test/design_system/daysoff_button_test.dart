import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:daysoff_app/design_system/widgets/daysoff_button.dart';

Widget _host(Widget child) => MaterialApp(home: Scaffold(body: child));

void main() {
  testWidgets('renders label and fires onPressed when enabled', (tester) async {
    var taps = 0;
    await tester.pumpWidget(_host(
      DaysOffButton(label: 'Get started', onPressed: () => taps++),
    ));
    expect(find.text('Get started'), findsOneWidget);
    await tester.tap(find.byType(DaysOffButton));
    expect(taps, 1);
  });

  testWidgets('disabled (null onPressed) does not fire', (tester) async {
    await tester.pumpWidget(_host(
      const DaysOffButton(label: 'Disabled', onPressed: null),
    ));
    await tester.tap(find.byType(DaysOffButton));
    expect(find.text('Disabled'), findsOneWidget); // no exception, no callback
  });
}
