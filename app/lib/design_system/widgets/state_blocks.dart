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
