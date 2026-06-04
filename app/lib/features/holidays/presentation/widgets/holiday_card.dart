import 'package:flutter/material.dart';
import '../../../../design_system/tokens/app_colors.dart';
import '../../../../design_system/tokens/app_spacing.dart';
import '../../../../design_system/widgets/status_badge.dart';
import '../../domain/entities/holiday.dart';

const _weekdayCaps = ['', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];

class HolidayCard extends StatelessWidget {
  const HolidayCard({super.key, required this.holiday, required this.onTap});

  final Holiday holiday;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final isFree = holiday.status() == HolidayStatus.free;
    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: AppSpacing.md),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            SizedBox(
              width: 56,
              child: Column(
                children: [
                  Text('${holiday.date.day}',
                      style: const TextStyle(
                          fontSize: 26, fontWeight: FontWeight.w600)),
                  Text(_weekdayCaps[holiday.date.weekday],
                      style: const TextStyle(
                          fontSize: 11, color: AppColors.onSurfaceVariant)),
                ],
              ),
            ),
            const SizedBox(width: AppSpacing.md),
            Expanded(
              child: Text(holiday.name,
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w500)),
            ),
            const SizedBox(width: AppSpacing.sm),
            isFree ? const StatusBadge.free() : const StatusBadge.absorbed(),
          ],
        ),
      ),
    );
  }
}
