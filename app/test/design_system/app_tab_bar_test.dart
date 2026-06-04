import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:daysoff_app/design_system/widgets/app_tab_bar.dart';

void main() {
  testWidgets('shows exactly 3 tabs and reports taps', (tester) async {
    int? tapped;
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        bottomNavigationBar: AppTabBar(
          currentIndex: 0,
          onTap: (i) => tapped = i,
        ),
      ),
    ));
    expect(find.text('Holidays'), findsOneWidget);
    expect(find.text('Plan'), findsOneWidget);
    expect(find.text('Settings'), findsOneWidget);
    await tester.tap(find.text('Plan'));
    expect(tapped, 1);
  });
}
