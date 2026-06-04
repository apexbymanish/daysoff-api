import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';
import 'package:daysoff_app/main.dart';
import 'package:daysoff_app/design_system/widgets/app_tab_bar.dart';

void main() {
  tearDown(Get.reset);

  testWidgets('app boots to the Holidays screen shell', (tester) async {
    await tester.runAsync(() async {
      await tester.pumpWidget(const DaysOffApp());
      await tester.pump(); // let first frame build (data load is async/failing offline)
    });
    expect(find.textContaining('Holidays'), findsWidgets);
    expect(find.byType(AppTabBar), findsOneWidget);
  });
}
