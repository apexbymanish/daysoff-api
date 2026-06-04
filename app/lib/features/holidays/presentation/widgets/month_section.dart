import 'package:flutter/material.dart';
import '../../../../design_system/tokens/app_spacing.dart';
import '../../domain/entities/holiday.dart';
import 'holiday_card.dart';

class MonthSection extends StatelessWidget {
  const MonthSection({
    super.key,
    required this.month,
    required this.holidays,
    required this.onTapHoliday,
  });

  final String month;
  final List<Holiday> holidays;
  final ValueChanged<Holiday> onTapHoliday;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(top: AppSpacing.lg, bottom: AppSpacing.xs),
          child: Text(month, style: Theme.of(context).textTheme.headlineMedium),
        ),
        const Divider(height: 1),
        for (final h in holidays) HolidayCard(holiday: h, onTap: () => onTapHoliday(h)),
      ],
    );
  }
}
