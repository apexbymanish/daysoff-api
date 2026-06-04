import 'package:flutter/material.dart';
import '../../../../design_system/tokens/app_colors.dart';
import '../../../../design_system/tokens/app_radii.dart';
import '../../../../design_system/tokens/app_spacing.dart';
import '../../domain/entities/holiday.dart';

const _monthFull = [
  '', 'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];

/// A simple single-month grid. Starts on the month of the first holiday and
/// lets the user page month-to-month. Holiday days are marked (peach=free,
/// grey=absorbed) with a label, never color alone.
class HolidayCalendarView extends StatefulWidget {
  const HolidayCalendarView({super.key, required this.holidays});
  final List<Holiday> holidays;

  @override
  State<HolidayCalendarView> createState() => _HolidayCalendarViewState();
}

class _HolidayCalendarViewState extends State<HolidayCalendarView> {
  late DateTime _month; // first day of the visible month

  @override
  void initState() {
    super.initState();
    final first = widget.holidays.isEmpty ? DateTime.now() : widget.holidays.first.date;
    _month = DateTime(first.year, first.month);
  }

  Holiday? _holidayOn(int day) {
    for (final h in widget.holidays) {
      if (h.date.year == _month.year && h.date.month == _month.month && h.date.day == day) {
        return h;
      }
    }
    return null;
  }

  @override
  Widget build(BuildContext context) {
    final daysInMonth = DateTime(_month.year, _month.month + 1, 0).day;
    final leadingBlanks = DateTime(_month.year, _month.month, 1).weekday - 1; // Mon=0
    final cells = <Widget>[
      for (var i = 0; i < leadingBlanks; i++) const SizedBox.shrink(),
      for (var day = 1; day <= daysInMonth; day++) _dayCell(day),
    ];
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            IconButton(
              onPressed: () => setState(
                  () => _month = DateTime(_month.year, _month.month - 1)),
              icon: const Icon(Icons.chevron_left),
            ),
            Text('${_monthFull[_month.month]} ${_month.year}',
                style: Theme.of(context).textTheme.headlineMedium),
            IconButton(
              onPressed: () => setState(
                  () => _month = DateTime(_month.year, _month.month + 1)),
              icon: const Icon(Icons.chevron_right),
            ),
          ],
        ),
        Expanded(
          child: GridView.count(
            crossAxisCount: 7,
            padding: const EdgeInsets.all(AppSpacing.sm),
            children: cells,
          ),
        ),
      ],
    );
  }

  Widget _dayCell(int day) {
    final holiday = _holidayOn(day);
    if (holiday == null) {
      return Center(child: Text('$day'));
    }
    final isFree = holiday.status() == HolidayStatus.free;
    final iso =
        '${_month.year.toString().padLeft(4, '0')}-${_month.month.toString().padLeft(2, '0')}-${day.toString().padLeft(2, '0')}';
    return Container(
      key: ValueKey('holiday-day-$iso'),
      margin: const EdgeInsets.all(AppSpacing.xs),
      decoration: BoxDecoration(
        color: (isFree ? AppColors.sand : AppColors.outline).withValues(alpha: 0.22),
        borderRadius: BorderRadius.circular(AppRadii.sm),
      ),
      child: Center(child: Text('$day', style: const TextStyle(fontWeight: FontWeight.w600))),
    );
  }
}
