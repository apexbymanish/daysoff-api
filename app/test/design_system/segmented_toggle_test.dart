import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:daysoff_app/design_system/widgets/segmented_toggle.dart';

Widget _host(Widget child) => MaterialApp(home: Scaffold(body: child));

void main() {
  testWidgets('renders segments and reports tapped index', (tester) async {
    int? selected;
    await tester.pumpWidget(_host(
      SegmentedToggle(
        segments: const ['Timeline', 'Calendar'],
        selectedIndex: 0,
        onChanged: (i) => selected = i,
      ),
    ));
    expect(find.text('Timeline'), findsOneWidget);
    expect(find.text('Calendar'), findsOneWidget);
    await tester.tap(find.text('Calendar'));
    expect(selected, 1);
  });
}
