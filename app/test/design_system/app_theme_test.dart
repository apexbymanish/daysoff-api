import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:daysoff_app/design_system/app_theme.dart';
import 'package:daysoff_app/design_system/tokens/app_colors.dart';

void main() {
  setUpAll(() {
    TestWidgetsFlutterBinding.ensureInitialized();
    GoogleFonts.config.allowRuntimeFetching = false;
  });

  testWidgets('light theme uses teal primary and light surface', (tester) async {
    final t = AppTheme.light;
    expect(t.useMaterial3, isTrue);
    expect(t.colorScheme.brightness, Brightness.light);
    expect(t.colorScheme.primary, AppColors.primary);
    expect(t.scaffoldBackgroundColor, AppColors.surface);
  });

  testWidgets('dark theme is near-black', (tester) async {
    final t = AppTheme.dark;
    expect(t.colorScheme.brightness, Brightness.dark);
    expect(t.scaffoldBackgroundColor, AppColors.surfaceDark);
  });
}
