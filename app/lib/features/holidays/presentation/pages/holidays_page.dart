import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../../design_system/tokens/app_spacing.dart';
import '../../../../design_system/widgets/app_scaffold.dart';
import '../../../../design_system/widgets/app_tab_bar.dart';
import '../../../../design_system/widgets/segmented_toggle.dart';
import '../../../../design_system/widgets/state_blocks.dart';
import '../controllers/holidays_controller.dart';
import '../widgets/month_section.dart';
import '../widgets/holiday_detail_sheet.dart';
import '../widgets/holiday_calendar_view.dart';

class HolidaysPage extends StatelessWidget {
  const HolidaysPage({super.key});

  @override
  Widget build(BuildContext context) {
    final c = Get.find<HolidaysController>();
    return AppScaffold(
      title: 'Holidays · 🇰🇷 KR 2026',
      bottomNavigationBar: AppTabBar(currentIndex: 0, onTap: (_) {}),
      body: Obx(() {
        switch (c.status.value) {
          case HolidaysViewStatus.loading:
            return const LoadingSkeleton(rows: 6);
          case HolidaysViewStatus.empty:
            return const EmptyState(
              icon: Icons.event_busy,
              title: 'No holidays found.',
              body: 'Try another year.',
            );
          case HolidaysViewStatus.error:
            return ErrorView(message: c.errorMessage.value, onRetry: c.load);
          case HolidaysViewStatus.loaded:
            return Column(
              children: [
                Padding(
                  padding: const EdgeInsets.all(AppSpacing.containerMargin),
                  child: SegmentedToggle(
                    segments: const ['Timeline', 'Calendar'],
                    selectedIndex: c.isCalendarView.value ? 1 : 0,
                    onChanged: (i) => c.isCalendarView.value = i == 1,
                  ),
                ),
                Expanded(
                  child: c.isCalendarView.value
                      ? HolidayCalendarView(holidays: c.holidays)
                      : ListView(
                          padding: const EdgeInsets.symmetric(
                              horizontal: AppSpacing.containerMargin),
                          children: [
                            for (final entry in c.holidaysByMonth.entries)
                              MonthSection(
                                month: entry.key,
                                holidays: entry.value,
                                onTapHoliday: (h) => showHolidayDetailSheet(h),
                              ),
                            const SizedBox(height: AppSpacing.xl),
                          ],
                        ),
                ),
              ],
            );
        }
      }),
    );
  }
}
