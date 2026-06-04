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
