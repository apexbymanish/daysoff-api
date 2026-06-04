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
