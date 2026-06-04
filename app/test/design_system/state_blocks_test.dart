import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:daysoff_app/design_system/widgets/state_blocks.dart';

Widget _host(Widget child) => MaterialApp(home: Scaffold(body: child));

void main() {
  testWidgets('EmptyState shows title, body and CTA that fires', (tester) async {
    var tapped = false;
    await tester.pumpWidget(_host(EmptyState(
      icon: Icons.event_busy,
      title: 'No more holidays this year.',
      body: 'Switch to 2027 to plan ahead.',
      ctaLabel: 'Go to 2027',
      onCta: () => tapped = true,
    )));
    expect(find.text('No more holidays this year.'), findsOneWidget);
    expect(find.text('Switch to 2027 to plan ahead.'), findsOneWidget);
    await tester.tap(find.text('Go to 2027'));
    expect(tapped, isTrue);
  });

  testWidgets('ErrorView shows message and retry', (tester) async {
    var retried = false;
    await tester.pumpWidget(_host(ErrorView(
      message: "Couldn't refresh holidays.",
      onRetry: () => retried = true,
    )));
    expect(find.text("Couldn't refresh holidays."), findsOneWidget);
    await tester.tap(find.text('Retry'));
    expect(retried, isTrue);
  });

  testWidgets('LoadingSkeleton renders the requested number of rows', (tester) async {
    await tester.pumpWidget(_host(const LoadingSkeleton(rows: 6)));
    expect(find.byKey(const ValueKey('skeleton-row')), findsNWidgets(6));
  });
}
