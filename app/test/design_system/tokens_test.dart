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
