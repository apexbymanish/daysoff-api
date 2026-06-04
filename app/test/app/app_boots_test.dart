import 'package:flutter_test/flutter_test.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:daysoff_app/main.dart';
import 'package:daysoff_app/design_system/widgets/daysoff_button.dart';
import 'package:daysoff_app/design_system/widgets/app_tab_bar.dart';

void main() {
  setUpAll(() {
    TestWidgetsFlutterBinding.ensureInitialized();
    GoogleFonts.config.allowRuntimeFetching = false;
  });

  testWidgets('app boots to the demo screen with theme, button and tab bar',
      (tester) async {
    await tester.pumpWidget(const DaysOffApp());
    await tester.pumpAndSettle();
    expect(find.text('daysoff'), findsOneWidget);
    expect(find.byType(DaysOffButton), findsWidgets);
    expect(find.byType(AppTabBar), findsOneWidget);
  });
}
