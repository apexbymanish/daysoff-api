# daysoff Flutter App — Phase 1 (Foundation) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scaffold the Flutter app in `app/` with the Serene Efficiency theme, core plumbing (env, Dio client, Failure), and the reusable `design_system/` primitive widgets — all test-covered — plus a demo screen proving the theme and navigation work.

**Architecture:** Clean Architecture, feature-first. This phase builds only `core/` and `design_system/` (no features yet). GetX is used solely in the presentation/app-shell layer (`GetMaterialApp`, routing, `Get.bottomSheet`/`Get.dialog`). Tokens and widgets are pure Flutter with no business logic.

**Tech Stack:** Flutter (Dart 3), GetX, Dio, fpdart, google_fonts, get_storage; dev: flutter_test, mocktail, flutter_lints.

**Spec:** `docs/superpowers/specs/2026-06-04-daysoff-flutter-app-design.md`

**Prerequisite:** Flutter SDK ≥ 3.22 (Dart ≥ 3.4) installed and on PATH. Verify with `flutter --version` before Task 1. All commands run from the repo root unless noted; the Flutter project lives in `app/`.

**Note on the `withValues` API:** this plan uses `Color.withValues(alpha: x)` (Flutter ≥ 3.27). If your Flutter is older, substitute `withOpacity(x)`.

---

## File Structure (this phase)

```
app/
  pubspec.yaml
  analysis_options.yaml
  lib/
    main.dart                         # GetMaterialApp + theme + initial route
    app/
      app_routes.dart                 # route name constants
      app_pages.dart                  # GetPage list
    core/
      env.dart                        # API base URL (dart-define)
      error/failure.dart              # sealed Failure hierarchy
      network/dio_client.dart         # configured Dio
    design_system/
      app_theme.dart                  # light + dark ThemeData
      tokens/
        app_colors.dart
        app_typography.dart
        app_spacing.dart
        app_radii.dart
      widgets/
        daysoff_button.dart
        daysoff_text_field.dart
        segmented_toggle.dart
        status_badge.dart
        pto_cost_pill.dart
        state_blocks.dart             # EmptyState, LoadingSkeleton, ErrorView
        daysoff_bottom_sheet.dart     # base sheet + show helper
        daysoff_dialog.dart           # ConfirmDialog + show helper
        app_scaffold.dart
        app_tab_bar.dart
    features/
      demo/demo_page.dart             # throwaway: proves theme + nav (removed in Phase 2)
  test/
    core/env_test.dart
    core/failure_test.dart
    design_system/tokens_test.dart
    design_system/app_theme_test.dart
    design_system/daysoff_button_test.dart
    design_system/daysoff_text_field_test.dart
    design_system/segmented_toggle_test.dart
    design_system/status_badge_test.dart
    design_system/pto_cost_pill_test.dart
    design_system/state_blocks_test.dart
    design_system/app_tab_bar_test.dart
    app/app_boots_test.dart
```

---

## Task 1: Scaffold project + dependencies

**Files:**
- Create: `app/` (via `flutter create`)
- Modify: `app/pubspec.yaml`, `app/analysis_options.yaml`
- Modify: `.gitignore` (root)

- [ ] **Step 1: Create the Flutter project**

Run from repo root:
```bash
flutter create --org com.daysoff --project-name daysoff_app --platforms ios,android app
```
Expected: `app/` created with `lib/main.dart`, `test/`, platform folders.

- [ ] **Step 2: Replace `app/pubspec.yaml` dependency section**

Set the `dependencies`/`dev_dependencies` to exactly:
```yaml
name: daysoff_app
description: "daysoff — maximize your time off."
publish_to: 'none'
version: 0.1.0+1

environment:
  sdk: ">=3.4.0 <4.0.0"

dependencies:
  flutter:
    sdk: flutter
  get: ^4.6.6
  dio: ^5.7.0
  fpdart: ^1.1.0
  google_fonts: ^6.2.1
  get_storage: ^2.1.1

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^4.0.0
  mocktail: ^1.0.4

flutter:
  uses-material-design: true
```

- [ ] **Step 3: Install deps**

Run: `cd app && flutter pub get`
Expected: "Got dependencies!" with no version-solve errors.

- [ ] **Step 4: Confirm the default test passes (baseline)**

The default `flutter create` adds `app/test/widget_test.dart` referencing a counter app. Delete it so the suite is clean:
```bash
rm app/test/widget_test.dart
```
Run: `cd app && flutter test`
Expected: "No tests found." or passes with 0 tests (clean baseline).

- [ ] **Step 5: Ignore build artifacts**

Append to the root `.gitignore`:
```
# Flutter app
app/.dart_tool/
app/build/
app/.flutter-plugins
app/.flutter-plugins-dependencies
app/ios/Pods/
app/**/GeneratedPluginRegistrant.*
```

- [ ] **Step 6: Commit**
```bash
git add app .gitignore
git commit -m "feat(app): scaffold Flutter project with core deps"
```

---

## Task 2: Design tokens (colors, spacing, radii, typography)

**Files:**
- Create: `app/lib/design_system/tokens/app_colors.dart`, `app_spacing.dart`, `app_radii.dart`, `app_typography.dart`
- Test: `app/test/design_system/tokens_test.dart`

- [ ] **Step 1: Write the failing test**

`app/test/design_system/tokens_test.dart`:
```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:daysoff_app/design_system/tokens/app_colors.dart';
import 'package:daysoff_app/design_system/tokens/app_spacing.dart';
import 'package:daysoff_app/design_system/tokens/app_radii.dart';

void main() {
  test('brand colors match Serene Efficiency hex values', () {
    expect(AppColors.primary, const Color(0xFF1A4D4E));
    expect(AppColors.sage, const Color(0xFF8E9775));
    expect(AppColors.sand, const Color(0xFFE9C46A));
    expect(AppColors.koreaRed, const Color(0xFFCD2E3A));
  });

  test('spacing follows the 4px grid', () {
    expect(AppSpacing.xs, 4);
    expect(AppSpacing.lg, 16);
    expect(AppSpacing.xl, 32);
  });

  test('radii expose pill and card values', () {
    expect(AppRadii.lg, 16);
    expect(AppRadii.pill, 9999);
  });
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd app && flutter test test/design_system/tokens_test.dart`
Expected: FAIL — `Target of URI doesn't exist` / undefined `AppColors`.

- [ ] **Step 3: Implement the tokens**

`app/lib/design_system/tokens/app_colors.dart`:
```dart
import 'package:flutter/material.dart';

/// Serene Efficiency palette. Never reference raw hex in feature code.
class AppColors {
  AppColors._();

  // Brand
  static const Color primary = Color(0xFF1A4D4E); // deep teal
  static const Color primaryStrong = Color(0xFF003637);
  static const Color secondary = Color(0xFF5C6BC0); // soft indigo
  static const Color sage = Color(0xFF8E9775); // PTO / off-day
  static const Color sand = Color(0xFFE9C46A); // free-day accent
  static const Color koreaRed = Color(0xFFCD2E3A);
  static const Color koreaBlue = Color(0xFF0047A0);

  // Neutrals — light
  static const Color surface = Color(0xFFF8F9FA);
  static const Color surfaceContainer = Color(0xFFEDEEEF);
  static const Color onSurface = Color(0xFF191C1D);
  static const Color onSurfaceVariant = Color(0xFF404848);
  static const Color outline = Color(0xFF707978);

  // Neutrals — dark
  static const Color surfaceDark = Color(0xFF0B0D0E);
  static const Color surfaceContainerDark = Color(0xFF14171A);
  static const Color onSurfaceDark = Color(0xFFF0F1F2);

  // Semantic
  static const Color error = Color(0xFFBA1A1A);
}
```

`app/lib/design_system/tokens/app_spacing.dart`:
```dart
class AppSpacing {
  AppSpacing._();
  static const double xs = 4;
  static const double sm = 8;
  static const double md = 12;
  static const double lg = 16;
  static const double xl = 32;
  static const double gutter = 12;
  static const double containerMargin = 20;
}
```

`app/lib/design_system/tokens/app_radii.dart`:
```dart
class AppRadii {
  AppRadii._();
  static const double sm = 4;
  static const double md = 12;
  static const double lg = 16;
  static const double xl = 24;
  static const double pill = 9999;
}
```

`app/lib/design_system/tokens/app_typography.dart`:
```dart
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTypography {
  AppTypography._();

  static TextStyle get displayNumeral => GoogleFonts.manrope(
      fontSize: 48, fontWeight: FontWeight.w700, height: 1.0, letterSpacing: -0.96);
  static TextStyle get headlineLg =>
      GoogleFonts.manrope(fontSize: 24, fontWeight: FontWeight.w700, height: 1.33);
  static TextStyle get headlineMd =>
      GoogleFonts.manrope(fontSize: 20, fontWeight: FontWeight.w600, height: 1.4);
  static TextStyle get bodyLg =>
      GoogleFonts.manrope(fontSize: 17, fontWeight: FontWeight.w400, height: 1.53);
  static TextStyle get bodySm =>
      GoogleFonts.manrope(fontSize: 14, fontWeight: FontWeight.w400, height: 1.43);
  static TextStyle get labelCaps => GoogleFonts.jetBrainsMono(
      fontSize: 12, fontWeight: FontWeight.w500, height: 1.33, letterSpacing: 0.6);
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd app && flutter test test/design_system/tokens_test.dart`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**
```bash
git add app/lib/design_system/tokens app/test/design_system/tokens_test.dart
git commit -m "feat(app): add Serene Efficiency design tokens"
```

---

## Task 3: AppTheme (light + dark)

**Files:**
- Create: `app/lib/design_system/app_theme.dart`
- Test: `app/test/design_system/app_theme_test.dart`

- [ ] **Step 1: Write the failing test**

`app/test/design_system/app_theme_test.dart`:
```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:daysoff_app/design_system/app_theme.dart';
import 'package:daysoff_app/design_system/tokens/app_colors.dart';

void main() {
  test('light theme uses teal primary and light surface', () {
    final t = AppTheme.light;
    expect(t.useMaterial3, isTrue);
    expect(t.colorScheme.brightness, Brightness.light);
    expect(t.colorScheme.primary, AppColors.primary);
    expect(t.scaffoldBackgroundColor, AppColors.surface);
  });

  test('dark theme is near-black', () {
    final t = AppTheme.dark;
    expect(t.colorScheme.brightness, Brightness.dark);
    expect(t.scaffoldBackgroundColor, AppColors.surfaceDark);
  });
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd app && flutter test test/design_system/app_theme_test.dart`
Expected: FAIL — undefined `AppTheme`.

- [ ] **Step 3: Implement AppTheme**

`app/lib/design_system/app_theme.dart`:
```dart
import 'package:flutter/material.dart';
import 'tokens/app_colors.dart';
import 'tokens/app_typography.dart';

class AppTheme {
  AppTheme._();

  static ThemeData get light => _build(Brightness.light);
  static ThemeData get dark => _build(Brightness.dark);

  static ThemeData _build(Brightness brightness) {
    final isDark = brightness == Brightness.dark;
    final scheme = ColorScheme.fromSeed(
      seedColor: AppColors.primary,
      brightness: brightness,
      primary: AppColors.primary,
      secondary: AppColors.secondary,
      surface: isDark ? AppColors.surfaceDark : AppColors.surface,
      error: AppColors.error,
    );
    final onColor = isDark ? AppColors.onSurfaceDark : AppColors.onSurface;
    return ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      scaffoldBackgroundColor: scheme.surface,
      textTheme: TextTheme(
        displayLarge: AppTypography.displayNumeral,
        headlineLarge: AppTypography.headlineLg,
        headlineMedium: AppTypography.headlineMd,
        bodyLarge: AppTypography.bodyLg,
        bodyMedium: AppTypography.bodySm,
        labelSmall: AppTypography.labelCaps,
      ).apply(bodyColor: onColor, displayColor: onColor),
    );
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd app && flutter test test/design_system/app_theme_test.dart`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**
```bash
git add app/lib/design_system/app_theme.dart app/test/design_system/app_theme_test.dart
git commit -m "feat(app): add light + dark AppTheme from tokens"
```

---

## Task 4: DaysOffButton

**Files:**
- Create: `app/lib/design_system/widgets/daysoff_button.dart`
- Test: `app/test/design_system/daysoff_button_test.dart`

- [ ] **Step 1: Write the failing test**

`app/test/design_system/daysoff_button_test.dart`:
```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:daysoff_app/design_system/widgets/daysoff_button.dart';

Widget _host(Widget child) => MaterialApp(home: Scaffold(body: child));

void main() {
  testWidgets('renders label and fires onPressed when enabled', (tester) async {
    var taps = 0;
    await tester.pumpWidget(_host(
      DaysOffButton(label: 'Get started', onPressed: () => taps++),
    ));
    expect(find.text('Get started'), findsOneWidget);
    await tester.tap(find.byType(DaysOffButton));
    expect(taps, 1);
  });

  testWidgets('disabled (null onPressed) does not fire', (tester) async {
    await tester.pumpWidget(_host(
      const DaysOffButton(label: 'Disabled', onPressed: null),
    ));
    await tester.tap(find.byType(DaysOffButton));
    expect(find.text('Disabled'), findsOneWidget); // no exception, no callback
  });
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd app && flutter test test/design_system/daysoff_button_test.dart`
Expected: FAIL — undefined `DaysOffButton`.

- [ ] **Step 3: Implement the widget**

`app/lib/design_system/widgets/daysoff_button.dart`:
```dart
import 'package:flutter/material.dart';
import '../tokens/app_colors.dart';
import '../tokens/app_radii.dart';
import '../tokens/app_spacing.dart';

enum DaysOffButtonVariant { primary, secondary }

class DaysOffButton extends StatelessWidget {
  const DaysOffButton({
    super.key,
    required this.label,
    required this.onPressed,
    this.variant = DaysOffButtonVariant.primary,
    this.icon,
  });

  final String label;
  final VoidCallback? onPressed; // null => disabled
  final DaysOffButtonVariant variant;
  final IconData? icon;

  bool get _enabled => onPressed != null;

  @override
  Widget build(BuildContext context) {
    final isPrimary = variant == DaysOffButtonVariant.primary;
    final bg = !_enabled
        ? AppColors.outline.withValues(alpha: 0.18)
        : (isPrimary ? AppColors.sage : Colors.transparent);
    final fg = !_enabled
        ? AppColors.onSurfaceVariant
        : (isPrimary ? Colors.white : AppColors.primary);
    return SizedBox(
      height: 48,
      width: double.infinity,
      child: Material(
        color: bg,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppRadii.xl),
          side: isPrimary
              ? BorderSide.none
              : BorderSide(
                  color: _enabled ? AppColors.primary : AppColors.outline,
                  width: 1.5),
        ),
        child: InkWell(
          borderRadius: BorderRadius.circular(AppRadii.xl),
          onTap: onPressed,
          child: Center(
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                if (icon != null) ...[
                  Icon(icon, size: 18, color: fg),
                  const SizedBox(width: AppSpacing.sm),
                ],
                Text(label,
                    style: TextStyle(
                        color: fg, fontWeight: FontWeight.w600, fontSize: 16)),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd app && flutter test test/design_system/daysoff_button_test.dart`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**
```bash
git add app/lib/design_system/widgets/daysoff_button.dart app/test/design_system/daysoff_button_test.dart
git commit -m "feat(app): add DaysOffButton (primary/secondary/disabled)"
```

---

## Task 5: DaysOffTextField

**Files:**
- Create: `app/lib/design_system/widgets/daysoff_text_field.dart`
- Test: `app/test/design_system/daysoff_text_field_test.dart`

- [ ] **Step 1: Write the failing test**

`app/test/design_system/daysoff_text_field_test.dart`:
```dart
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd app && flutter test test/design_system/daysoff_text_field_test.dart`
Expected: FAIL — undefined `DaysOffTextField`.

- [ ] **Step 3: Implement the widget**

`app/lib/design_system/widgets/daysoff_text_field.dart`:
```dart
import 'package:flutter/material.dart';
import '../tokens/app_colors.dart';
import '../tokens/app_radii.dart';
import '../tokens/app_spacing.dart';

class DaysOffTextField extends StatelessWidget {
  const DaysOffTextField({
    super.key,
    required this.label,
    this.controller,
    this.obscureText = false,
    this.errorText,
    this.keyboardType,
  });

  final String label;
  final TextEditingController? controller;
  final bool obscureText;
  final String? errorText;
  final TextInputType? keyboardType;

  bool get _hasError => errorText != null;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: Theme.of(context).textTheme.labelSmall),
        const SizedBox(height: AppSpacing.xs),
        TextField(
          controller: controller,
          obscureText: obscureText,
          keyboardType: keyboardType,
          decoration: InputDecoration(
            isDense: true,
            enabledBorder: UnderlineInputBorder(
              borderSide: BorderSide(
                  color: _hasError ? AppColors.error : AppColors.outline),
            ),
            focusedBorder: UnderlineInputBorder(
              borderSide: BorderSide(
                  color: _hasError ? AppColors.error : AppColors.primary,
                  width: 2),
            ),
          ),
        ),
        if (_hasError) ...[
          const SizedBox(height: AppSpacing.xs),
          Row(
            children: [
              const Icon(Icons.error_outline, size: 14, color: AppColors.error),
              const SizedBox(width: AppSpacing.xs),
              Expanded(
                child: Text(errorText!,
                    style: const TextStyle(color: AppColors.error, fontSize: 12)),
              ),
            ],
          ),
        ],
      ],
    );
  }
}
```
(`AppRadii` imported for consistency with sibling widgets; safe if unused-lint is off — if `flutter_lints` flags it, remove the import.)

- [ ] **Step 4: Run test to verify it passes**

Run: `cd app && flutter test test/design_system/daysoff_text_field_test.dart`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**
```bash
git add app/lib/design_system/widgets/daysoff_text_field.dart app/test/design_system/daysoff_text_field_test.dart
git commit -m "feat(app): add DaysOffTextField with error state"
```

---

## Task 6: SegmentedToggle

**Files:**
- Create: `app/lib/design_system/widgets/segmented_toggle.dart`
- Test: `app/test/design_system/segmented_toggle_test.dart`

- [ ] **Step 1: Write the failing test**

`app/test/design_system/segmented_toggle_test.dart`:
```dart
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd app && flutter test test/design_system/segmented_toggle_test.dart`
Expected: FAIL — undefined `SegmentedToggle`.

- [ ] **Step 3: Implement the widget**

`app/lib/design_system/widgets/segmented_toggle.dart`:
```dart
import 'package:flutter/material.dart';
import '../tokens/app_colors.dart';
import '../tokens/app_radii.dart';
import '../tokens/app_spacing.dart';

class SegmentedToggle extends StatelessWidget {
  const SegmentedToggle({
    super.key,
    required this.segments,
    required this.selectedIndex,
    required this.onChanged,
  });

  final List<String> segments;
  final int selectedIndex;
  final ValueChanged<int> onChanged;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AppSpacing.xs),
      decoration: BoxDecoration(
        color: AppColors.surfaceContainer,
        borderRadius: BorderRadius.circular(AppRadii.pill),
      ),
      child: Row(
        children: [
          for (var i = 0; i < segments.length; i++)
            Expanded(
              child: GestureDetector(
                onTap: () => onChanged(i),
                child: Container(
                  height: 40,
                  alignment: Alignment.center,
                  decoration: BoxDecoration(
                    color: i == selectedIndex ? Colors.white : Colors.transparent,
                    borderRadius: BorderRadius.circular(AppRadii.pill),
                  ),
                  child: Text(
                    segments[i],
                    style: TextStyle(
                      fontWeight:
                          i == selectedIndex ? FontWeight.w600 : FontWeight.w400,
                      color: i == selectedIndex
                          ? AppColors.primary
                          : AppColors.onSurfaceVariant,
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd app && flutter test test/design_system/segmented_toggle_test.dart`
Expected: PASS (1 test).

- [ ] **Step 5: Commit**
```bash
git add app/lib/design_system/widgets/segmented_toggle.dart app/test/design_system/segmented_toggle_test.dart
git commit -m "feat(app): add SegmentedToggle"
```

---

## Task 7: StatusBadge + PtoCostPill

**Files:**
- Create: `app/lib/design_system/widgets/status_badge.dart`, `app/lib/design_system/widgets/pto_cost_pill.dart`
- Test: `app/test/design_system/status_badge_test.dart`, `app/test/design_system/pto_cost_pill_test.dart`

- [ ] **Step 1: Write the failing tests**

`app/test/design_system/status_badge_test.dart`:
```dart
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
```

`app/test/design_system/pto_cost_pill_test.dart`:
```dart
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd app && flutter test test/design_system/status_badge_test.dart test/design_system/pto_cost_pill_test.dart`
Expected: FAIL — undefined `StatusBadge` / `PtoCostPill`.

- [ ] **Step 3: Implement the widgets**

`app/lib/design_system/widgets/status_badge.dart`:
```dart
import 'package:flutter/material.dart';
import '../tokens/app_colors.dart';
import '../tokens/app_radii.dart';
import '../tokens/app_spacing.dart';

class StatusBadge extends StatelessWidget {
  const StatusBadge({super.key, required this.label, required this.icon, required this.color});

  const StatusBadge.free({super.key})
      : label = 'free',
        icon = Icons.wb_sunny_outlined,
        color = AppColors.sand;

  const StatusBadge.absorbed({super.key})
      : label = 'absorbed',
        icon = Icons.nightlight_outlined,
        color = AppColors.outline;

  final String label;
  final IconData icon;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 14, color: color),
        const SizedBox(width: AppSpacing.xs),
        Text(label, style: TextStyle(fontSize: 11, color: color, fontWeight: FontWeight.w500)),
      ],
    );
  }
}
```

`app/lib/design_system/widgets/pto_cost_pill.dart`:
```dart
import 'package:flutter/material.dart';
import '../tokens/app_colors.dart';
import '../tokens/app_radii.dart';
import '../tokens/app_spacing.dart';

class PtoCostPill extends StatelessWidget {
  const PtoCostPill({super.key, required this.cost});
  final int cost;

  @override
  Widget build(BuildContext context) {
    final Color bg;
    if (cost == 0) {
      bg = AppColors.sand;
    } else if (cost <= 2) {
      bg = AppColors.sage;
    } else {
      bg = AppColors.outline;
    }
    final label = cost == 0 ? 'Free' : '$cost PTO';
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: AppSpacing.md, vertical: AppSpacing.xs),
      decoration: BoxDecoration(
        color: bg.withValues(alpha: 0.22),
        borderRadius: BorderRadius.circular(AppRadii.pill),
      ),
      child: Text(label,
          style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AppColors.onSurface)),
    );
  }
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd app && flutter test test/design_system/status_badge_test.dart test/design_system/pto_cost_pill_test.dart`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**
```bash
git add app/lib/design_system/widgets/status_badge.dart app/lib/design_system/widgets/pto_cost_pill.dart app/test/design_system/status_badge_test.dart app/test/design_system/pto_cost_pill_test.dart
git commit -m "feat(app): add StatusBadge + PtoCostPill (icon+label encoding)"
```

---

## Task 8: State blocks (EmptyState, LoadingSkeleton, ErrorView)

**Files:**
- Create: `app/lib/design_system/widgets/state_blocks.dart`
- Test: `app/test/design_system/state_blocks_test.dart`

- [ ] **Step 1: Write the failing test**

`app/test/design_system/state_blocks_test.dart`:
```dart
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd app && flutter test test/design_system/state_blocks_test.dart`
Expected: FAIL — undefined `EmptyState`/`ErrorView`/`LoadingSkeleton`.

- [ ] **Step 3: Implement the widgets**

`app/lib/design_system/widgets/state_blocks.dart`:
```dart
import 'package:flutter/material.dart';
import '../tokens/app_colors.dart';
import '../tokens/app_radii.dart';
import '../tokens/app_spacing.dart';
import 'daysoff_button.dart';

class EmptyState extends StatelessWidget {
  const EmptyState({
    super.key,
    required this.icon,
    required this.title,
    required this.body,
    this.ctaLabel,
    this.onCta,
  });

  final IconData icon;
  final String title;
  final String body;
  final String? ctaLabel;
  final VoidCallback? onCta;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.xl),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 40, color: AppColors.onSurfaceVariant),
            const SizedBox(height: AppSpacing.lg),
            Text(title,
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.headlineMedium),
            const SizedBox(height: AppSpacing.sm),
            Text(body,
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.bodyLarge),
            if (ctaLabel != null && onCta != null) ...[
              const SizedBox(height: AppSpacing.xl),
              DaysOffButton(label: ctaLabel!, onPressed: onCta),
            ],
          ],
        ),
      ),
    );
  }
}

class ErrorView extends StatelessWidget {
  const ErrorView({super.key, required this.message, required this.onRetry});
  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.xl),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.cloud_off, size: 36, color: AppColors.error),
            const SizedBox(height: AppSpacing.lg),
            Text(message,
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.bodyLarge),
            const SizedBox(height: AppSpacing.lg),
            DaysOffButton(
              label: 'Retry',
              variant: DaysOffButtonVariant.secondary,
              onPressed: onRetry,
            ),
          ],
        ),
      ),
    );
  }
}

class LoadingSkeleton extends StatelessWidget {
  const LoadingSkeleton({super.key, this.rows = 6});
  final int rows;

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      padding: const EdgeInsets.all(AppSpacing.containerMargin),
      itemCount: rows,
      separatorBuilder: (_, __) => const SizedBox(height: AppSpacing.md),
      itemBuilder: (_, __) => Container(
        key: const ValueKey('skeleton-row'),
        height: 72,
        decoration: BoxDecoration(
          color: AppColors.surfaceContainer,
          borderRadius: BorderRadius.circular(AppRadii.lg),
        ),
      ),
    );
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd app && flutter test test/design_system/state_blocks_test.dart`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**
```bash
git add app/lib/design_system/widgets/state_blocks.dart app/test/design_system/state_blocks_test.dart
git commit -m "feat(app): add EmptyState/ErrorView/LoadingSkeleton blocks"
```

---

## Task 9: Reusable bottom sheet + confirm dialog

**Files:**
- Create: `app/lib/design_system/widgets/daysoff_bottom_sheet.dart`, `app/lib/design_system/widgets/daysoff_dialog.dart`
- Test: `app/test/design_system/state_blocks_test.dart` is unrelated; add cases inside the two widget files' own tests below.
- Test: `app/test/design_system/daysoff_sheet_dialog_test.dart`

- [ ] **Step 1: Write the failing test**

`app/test/design_system/daysoff_sheet_dialog_test.dart`:
```dart
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd app && flutter test test/design_system/daysoff_sheet_dialog_test.dart`
Expected: FAIL — undefined `DaysOffBottomSheet`/`ConfirmDialog`.

- [ ] **Step 3: Implement the widgets + show helpers**

`app/lib/design_system/widgets/daysoff_bottom_sheet.dart`:
```dart
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../tokens/app_colors.dart';
import '../tokens/app_radii.dart';
import '../tokens/app_spacing.dart';

/// Base bottom sheet body used by every sheet in the app.
class DaysOffBottomSheet extends StatelessWidget {
  const DaysOffBottomSheet({super.key, required this.title, required this.child});
  final String title;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AppSpacing.containerMargin),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(AppRadii.xl)),
      ),
      child: SafeArea(
        top: false,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: 36,
                height: 4,
                decoration: BoxDecoration(
                  color: AppColors.outline.withValues(alpha: 0.4),
                  borderRadius: BorderRadius.circular(AppRadii.pill),
                ),
              ),
            ),
            const SizedBox(height: AppSpacing.lg),
            Text(title, style: Theme.of(context).textTheme.headlineMedium),
            const SizedBox(height: AppSpacing.md),
            child,
          ],
        ),
      ),
    );
  }
}

/// Presentation-layer helper (GetX). Shows any content as a daysoff sheet.
Future<T?> showDaysOffBottomSheet<T>({required String title, required Widget child}) {
  return Get.bottomSheet<T>(
    DaysOffBottomSheet(title: title, child: child),
    isScrollControlled: true,
    backgroundColor: Colors.transparent,
  );
}
```

`app/lib/design_system/widgets/daysoff_dialog.dart`:
```dart
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../tokens/app_colors.dart';
import '../tokens/app_radii.dart';
import '../tokens/app_spacing.dart';
import 'daysoff_button.dart';

class ConfirmDialog extends StatelessWidget {
  const ConfirmDialog({
    super.key,
    required this.title,
    required this.message,
    required this.confirmLabel,
    required this.onConfirm,
    this.destructive = true,
  });

  final String title;
  final String message;
  final String confirmLabel;
  final VoidCallback onConfirm;
  final bool destructive;

  @override
  Widget build(BuildContext context) {
    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppRadii.xl)),
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.containerMargin),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: Theme.of(context).textTheme.headlineMedium),
            const SizedBox(height: AppSpacing.sm),
            Text(message, style: Theme.of(context).textTheme.bodyLarge),
            const SizedBox(height: AppSpacing.lg),
            SizedBox(
              height: 48,
              width: double.infinity,
              child: FilledButton(
                style: FilledButton.styleFrom(
                  backgroundColor: destructive ? AppColors.error : AppColors.sage,
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(AppRadii.xl)),
                ),
                onPressed: onConfirm,
                child: Text(confirmLabel),
              ),
            ),
            const SizedBox(height: AppSpacing.sm),
            DaysOffButton(
              label: 'Cancel',
              variant: DaysOffButtonVariant.secondary,
              onPressed: () => Get.back<void>(),
            ),
          ],
        ),
      ),
    );
  }
}

Future<void> showConfirmDialog({
  required String title,
  required String message,
  required String confirmLabel,
  required VoidCallback onConfirm,
  bool destructive = true,
}) {
  return Get.dialog<void>(ConfirmDialog(
    title: title,
    message: message,
    confirmLabel: confirmLabel,
    onConfirm: onConfirm,
    destructive: destructive,
  ));
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd app && flutter test test/design_system/daysoff_sheet_dialog_test.dart`
Expected: PASS (2 tests). (Tests render the widgets directly, so no `GetMaterialApp` is required; the `show*` helpers are exercised later in the app shell.)

- [ ] **Step 5: Commit**
```bash
git add app/lib/design_system/widgets/daysoff_bottom_sheet.dart app/lib/design_system/widgets/daysoff_dialog.dart app/test/design_system/daysoff_sheet_dialog_test.dart
git commit -m "feat(app): add reusable DaysOffBottomSheet + ConfirmDialog"
```

---

## Task 10: AppScaffold + AppTabBar

**Files:**
- Create: `app/lib/design_system/widgets/app_scaffold.dart`, `app/lib/design_system/widgets/app_tab_bar.dart`
- Test: `app/test/design_system/app_tab_bar_test.dart`

- [ ] **Step 1: Write the failing test**

`app/test/design_system/app_tab_bar_test.dart`:
```dart
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd app && flutter test test/design_system/app_tab_bar_test.dart`
Expected: FAIL — undefined `AppTabBar`.

- [ ] **Step 3: Implement the widgets**

`app/lib/design_system/widgets/app_tab_bar.dart`:
```dart
import 'package:flutter/material.dart';
import '../tokens/app_colors.dart';

class AppTabBar extends StatelessWidget {
  const AppTabBar({super.key, required this.currentIndex, required this.onTap});
  final int currentIndex;
  final ValueChanged<int> onTap;

  @override
  Widget build(BuildContext context) {
    return NavigationBar(
      selectedIndex: currentIndex,
      onDestinationSelected: onTap,
      backgroundColor: Theme.of(context).colorScheme.surface,
      indicatorColor: AppColors.sage.withValues(alpha: 0.25),
      destinations: const [
        NavigationDestination(
            icon: Icon(Icons.calendar_today_outlined),
            selectedIcon: Icon(Icons.calendar_today),
            label: 'Holidays'),
        NavigationDestination(
            icon: Icon(Icons.event_available_outlined),
            selectedIcon: Icon(Icons.event_available),
            label: 'Plan'),
        NavigationDestination(
            icon: Icon(Icons.settings_outlined),
            selectedIcon: Icon(Icons.settings),
            label: 'Settings'),
      ],
    );
  }
}
```

`app/lib/design_system/widgets/app_scaffold.dart`:
```dart
import 'package:flutter/material.dart';

/// Standard screen scaffold: optional title app bar, body, optional tab bar.
class AppScaffold extends StatelessWidget {
  const AppScaffold({
    super.key,
    required this.body,
    this.title,
    this.bottomNavigationBar,
    this.actions,
  });

  final Widget body;
  final String? title;
  final Widget? bottomNavigationBar;
  final List<Widget>? actions;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: title == null
          ? null
          : AppBar(title: Text(title!), actions: actions),
      body: SafeArea(child: body),
      bottomNavigationBar: bottomNavigationBar,
    );
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd app && flutter test test/design_system/app_tab_bar_test.dart`
Expected: PASS (1 test).

- [ ] **Step 5: Commit**
```bash
git add app/lib/design_system/widgets/app_scaffold.dart app/lib/design_system/widgets/app_tab_bar.dart app/test/design_system/app_tab_bar_test.dart
git commit -m "feat(app): add AppScaffold + AppTabBar (3-tab)"
```

---

## Task 11: Core — env, Failure, Dio client

**Files:**
- Create: `app/lib/core/env.dart`, `app/lib/core/error/failure.dart`, `app/lib/core/network/dio_client.dart`
- Test: `app/test/core/env_test.dart`, `app/test/core/failure_test.dart`

- [ ] **Step 1: Write the failing tests**

`app/test/core/env_test.dart`:
```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:daysoff_app/core/env.dart';

void main() {
  test('apiBaseUrl defaults to the deployed Fly URL', () {
    expect(Env.apiBaseUrl, 'https://daysoff-api.fly.dev');
  });
}
```

`app/test/core/failure_test.dart`:
```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:daysoff_app/core/error/failure.dart';

void main() {
  test('failures carry a user-facing message and are matchable by type', () {
    const Failure f = NetworkFailure();
    expect(f, isA<NetworkFailure>());
    expect(f.message, isNotEmpty);

    final result = switch (const ServerFailure('boom')) {
      NetworkFailure() => 'net',
      ServerFailure(:final message) => message,
      CacheFailure() => 'cache',
      PermissionFailure() => 'perm',
    };
    expect(result, 'boom');
  });
}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd app && flutter test test/core/env_test.dart test/core/failure_test.dart`
Expected: FAIL — undefined `Env` / `Failure`.

- [ ] **Step 3: Implement core**

`app/lib/core/env.dart`:
```dart
class Env {
  Env._();
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'https://daysoff-api.fly.dev',
  );
}
```

`app/lib/core/error/failure.dart`:
```dart
/// Domain-level failures. Data sources throw exceptions; repositories map
/// those to one of these for the presentation layer to render.
sealed class Failure {
  const Failure(this.message);
  final String message;
}

class NetworkFailure extends Failure {
  const NetworkFailure([super.message = 'Check your connection and try again.']);
}

class ServerFailure extends Failure {
  const ServerFailure([super.message = 'Something went wrong on our end.']);
}

class CacheFailure extends Failure {
  const CacheFailure([super.message = 'Could not read saved data.']);
}

class PermissionFailure extends Failure {
  const PermissionFailure([super.message = 'Permission denied.']);
}
```

`app/lib/core/network/dio_client.dart`:
```dart
import 'package:dio/dio.dart';
import '../env.dart';

/// Configured Dio for the /v1 API. Inject `DioClient().raw` into data sources.
class DioClient {
  DioClient([Dio? dio]) : raw = dio ?? Dio() {
    raw.options
      ..baseUrl = Env.apiBaseUrl
      ..connectTimeout = const Duration(seconds: 15)
      ..receiveTimeout = const Duration(seconds: 20)
      ..headers = {'Accept': 'application/json'};
  }

  final Dio raw;
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd app && flutter test test/core/env_test.dart test/core/failure_test.dart`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**
```bash
git add app/lib/core app/test/core
git commit -m "feat(app): add core env, Failure hierarchy, Dio client"
```

---

## Task 12: App shell — routes, GetMaterialApp, demo screen

**Files:**
- Create: `app/lib/app/app_routes.dart`, `app/lib/app/app_pages.dart`, `app/lib/features/demo/demo_page.dart`
- Modify: `app/lib/main.dart`
- Test: `app/test/app/app_boots_test.dart`

- [ ] **Step 1: Write the failing test**

`app/test/app/app_boots_test.dart`:
```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:daysoff_app/main.dart';
import 'package:daysoff_app/design_system/widgets/daysoff_button.dart';
import 'package:daysoff_app/design_system/widgets/app_tab_bar.dart';

void main() {
  testWidgets('app boots to the demo screen with theme, button and tab bar',
      (tester) async {
    await tester.pumpWidget(const DaysOffApp());
    await tester.pumpAndSettle();
    expect(find.text('daysoff'), findsOneWidget);
    expect(find.byType(DaysOffButton), findsWidgets);
    expect(find.byType(AppTabBar), findsOneWidget);
  });
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd app && flutter test test/app/app_boots_test.dart`
Expected: FAIL — undefined `DaysOffApp`.

- [ ] **Step 3: Implement routes, pages, demo, and main**

`app/lib/app/app_routes.dart`:
```dart
abstract class AppRoutes {
  static const demo = '/demo';
}
```

`app/lib/features/demo/demo_page.dart`:
```dart
import 'package:flutter/material.dart';
import '../../design_system/widgets/app_scaffold.dart';
import '../../design_system/widgets/app_tab_bar.dart';
import '../../design_system/widgets/daysoff_button.dart';
import '../../design_system/widgets/segmented_toggle.dart';
import '../../design_system/widgets/daysoff_dialog.dart';
import '../../design_system/tokens/app_spacing.dart';

/// Throwaway screen proving theme + components + nav. Removed in Phase 2.
class DemoPage extends StatefulWidget {
  const DemoPage({super.key});
  @override
  State<DemoPage> createState() => _DemoPageState();
}

class _DemoPageState extends State<DemoPage> {
  int _seg = 0;
  int _tab = 0;

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      title: 'daysoff',
      bottomNavigationBar:
          AppTabBar(currentIndex: _tab, onTap: (i) => setState(() => _tab = i)),
      body: Padding(
        padding: const EdgeInsets.all(AppSpacing.containerMargin),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SegmentedToggle(
              segments: const ['Timeline', 'Calendar'],
              selectedIndex: _seg,
              onChanged: (i) => setState(() => _seg = i),
            ),
            const SizedBox(height: AppSpacing.xl),
            DaysOffButton(
              label: 'Confirm dialog demo',
              onPressed: () => showConfirmDialog(
                title: 'Sign out?',
                message: 'You can sign back in anytime.',
                confirmLabel: 'Sign out',
                onConfirm: () {},
              ),
            ),
          ],
        ),
      ),
    );
  }
}
```

`app/lib/app/app_pages.dart`:
```dart
import 'package:get/get.dart';
import '../features/demo/demo_page.dart';
import 'app_routes.dart';

abstract class AppPages {
  static final pages = [
    GetPage(name: AppRoutes.demo, page: () => const DemoPage()),
  ];
}
```

`app/lib/main.dart` (replace entire file):
```dart
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'app/app_pages.dart';
import 'app/app_routes.dart';
import 'design_system/app_theme.dart';

void main() => runApp(const DaysOffApp());

class DaysOffApp extends StatelessWidget {
  const DaysOffApp({super.key});

  @override
  Widget build(BuildContext context) {
    return GetMaterialApp(
      title: 'daysoff',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      darkTheme: AppTheme.dark,
      themeMode: ThemeMode.system,
      initialRoute: AppRoutes.demo,
      getPages: AppPages.pages,
    );
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd app && flutter test test/app/app_boots_test.dart`
Expected: PASS (1 test).

- [ ] **Step 5: Run the full suite + analyzer**

Run: `cd app && flutter analyze && flutter test`
Expected: analyzer reports no issues; all tests pass.

- [ ] **Step 6: Commit**
```bash
git add app/lib/main.dart app/lib/app app/lib/features/demo app/test/app/app_boots_test.dart
git commit -m "feat(app): boot GetMaterialApp with theme, routing, demo screen"
```

---

## Phase 1 self-review

- **Spec coverage (foundation slice):** Flutter scaffold ✓ (T1); GetX app shell ✓ (T12); Clean-arch `core/` env+Failure+Dio ✓ (T11); reusable `design_system/` tokens ✓ (T2) + theme ✓ (T3) + widgets Button/TextField/SegmentedToggle/StatusBadge/PtoCostPill/state-blocks/BottomSheet/Dialog/Scaffold/TabBar ✓ (T4–T10); light+dark theme ✓ (T3); accessibility icon+label encoding ✓ (T5,T7). Feature domain/data layers intentionally deferred to Phase 2 (this phase has no API features yet).
- **Placeholder scan:** none — every widget/test has full code.
- **Type consistency:** `DaysOffButtonVariant.{primary,secondary}` used consistently (T4, T8, T9, T10); `AppColors`/`AppSpacing`/`AppRadii` names match across all widgets; `DaysOffApp` defined in T12 and referenced by its test.
- **Deferred to feature phases (not gaps):** HolidayCard, BreakCard, DayRibbon, BudgetSlider, ReminderRow, SandwichCard, UpsellBanner, UndoToast — these encode entity/feature semantics and are built in the phases that own them, reusing these primitives.

## Done when
`cd app && flutter analyze && flutter test` is clean, the app launches
(`cd app && flutter run`) to the demo screen showing the themed segmented
toggle, button, confirm dialog, and 3-tab bar in both light and dark mode.
