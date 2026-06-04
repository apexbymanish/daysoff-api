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
