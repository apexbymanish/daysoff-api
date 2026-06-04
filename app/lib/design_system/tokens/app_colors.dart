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
