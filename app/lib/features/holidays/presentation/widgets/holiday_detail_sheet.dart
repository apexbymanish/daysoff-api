import 'package:flutter/material.dart';
import '../../../../design_system/tokens/app_spacing.dart';
import '../../../../design_system/widgets/daysoff_bottom_sheet.dart';
import '../../../../design_system/widgets/status_badge.dart';
import '../../domain/entities/holiday.dart';

const _weekdayFull = [
  '', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
];
const _monthFull = [
  '', 'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];

/// Pure body widget (testable without GetX). Shown via [showHolidayDetailSheet].
class HolidayDetailSheetBody extends StatelessWidget {
  const HolidayDetailSheetBody({super.key, required this.holiday});
  final Holiday holiday;

  @override
  Widget build(BuildContext context) {
    final d = holiday.date;
    final isFree = holiday.status() == HolidayStatus.free;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(holiday.name, style: Theme.of(context).textTheme.headlineLarge),
        const SizedBox(height: AppSpacing.sm),
        Text('${_weekdayFull[d.weekday]}, ${_monthFull[d.month]} ${d.day}, ${d.year}',
            style: Theme.of(context).textTheme.bodyLarge),
        const SizedBox(height: AppSpacing.lg),
        isFree ? const StatusBadge.free() : const StatusBadge.absorbed(),
        const SizedBox(height: AppSpacing.lg),
        Text(
          isFree
              ? 'Falls on a weekday — a day off.'
              : 'Falls on the weekend — absorbed.',
          style: Theme.of(context).textTheme.bodyMedium,
        ),
      ],
    );
  }
}

Future<void> showHolidayDetailSheet(Holiday holiday) {
  return showDaysOffBottomSheet<void>(
    title: 'Holiday',
    child: HolidayDetailSheetBody(holiday: holiday),
  );
}
