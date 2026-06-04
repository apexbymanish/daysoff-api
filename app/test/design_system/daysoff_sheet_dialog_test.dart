import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:daysoff_app/design_system/widgets/daysoff_bottom_sheet.dart';
import 'package:daysoff_app/design_system/widgets/daysoff_dialog.dart';

Widget _host(Widget child) => MaterialApp(home: Scaffold(body: child));

void main() {
  testWidgets('DaysOffBottomSheet renders title and child', (tester) async {
    await tester.pumpWidget(_host(
      const DaysOffBottomSheet(
        title: 'Your weekend',
        child: Text('pills go here'),
      ),
    ));
    expect(find.text('Your weekend'), findsOneWidget);
    expect(find.text('pills go here'), findsOneWidget);
  });

  testWidgets('ConfirmDialog fires confirm callback', (tester) async {
    var confirmed = false;
    await tester.pumpWidget(_host(
      ConfirmDialog(
        title: 'Sign out?',
        message: 'You can sign back in anytime.',
        confirmLabel: 'Sign out',
        onConfirm: () => confirmed = true,
      ),
    ));
    expect(find.text('Sign out?'), findsOneWidget);
    await tester.tap(find.text('Sign out'));
    expect(confirmed, isTrue);
  });
}
