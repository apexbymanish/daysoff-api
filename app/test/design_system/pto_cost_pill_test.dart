import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:daysoff_app/design_system/widgets/pto_cost_pill.dart';

void main() {
  testWidgets('formats singular and plural PTO', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: Scaffold(body: PtoCostPill(cost: 1))));
    expect(find.text('1 PTO'), findsOneWidget);
  });

  testWidgets('zero PTO reads as Free', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: Scaffold(body: PtoCostPill(cost: 0))));
    expect(find.text('Free'), findsOneWidget);
  });
}
