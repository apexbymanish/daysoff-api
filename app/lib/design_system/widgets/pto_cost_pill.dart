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
          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AppColors.onSurface)),
    );
  }
}
