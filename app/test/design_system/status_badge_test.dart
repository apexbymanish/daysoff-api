import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:daysoff_app/design_system/widgets/status_badge.dart';

void main() {
  testWidgets('free badge shows label and an icon (not color alone)', (tester) async {
    await tester.pumpWidget(const MaterialApp(
      home: Scaffold(body: StatusBadge.free()),
    ));
    expect(find.text('free'), findsOneWidget);
    expect(find.byIcon(Icons.wb_sunny_outlined), findsOneWidget);
  });

  testWidgets('absorbed badge shows label and moon icon', (tester) async {
    await tester.pumpWidget(const MaterialApp(
      home: Scaffold(body: StatusBadge.absorbed()),
    ));
    expect(find.text('absorbed'), findsOneWidget);
    expect(find.byIcon(Icons.nightlight_outlined), findsOneWidget);
  });
}
