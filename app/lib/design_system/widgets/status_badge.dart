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
