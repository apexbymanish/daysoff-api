import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:daysoff_app/design_system/widgets/daysoff_text_field.dart';

Widget _host(Widget child) => MaterialApp(home: Scaffold(body: child));

void main() {
  testWidgets('shows label and accepts input', (tester) async {
    final controller = TextEditingController();
    await tester.pumpWidget(_host(
      DaysOffTextField(label: 'Email', controller: controller),
    ));
    expect(find.text('Email'), findsOneWidget);
    await tester.enterText(find.byType(TextField), 'a@b.com');
    expect(controller.text, 'a@b.com');
  });

  testWidgets('error state shows error text and icon', (tester) async {
    await tester.pumpWidget(_host(
      const DaysOffTextField(label: 'Email', errorText: "We don't recognize that email."),
    ));
    expect(find.text("We don't recognize that email."), findsOneWidget);
    expect(find.byIcon(Icons.error_outline), findsOneWidget); // icon + text, not color alone
  });
}
