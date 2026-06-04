import 'package:flutter/material.dart';
import '../../design_system/widgets/app_scaffold.dart';
import '../../design_system/widgets/app_tab_bar.dart';
import '../../design_system/widgets/daysoff_button.dart';
import '../../design_system/widgets/segmented_toggle.dart';
import '../../design_system/widgets/daysoff_dialog.dart';
import '../../design_system/tokens/app_spacing.dart';

/// Throwaway screen proving theme + components + nav. Removed in Phase 2.
class DemoPage extends StatefulWidget {
  const DemoPage({super.key});
  @override
  State<DemoPage> createState() => _DemoPageState();
}

class _DemoPageState extends State<DemoPage> {
  int _seg = 0;
  int _tab = 0;

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      title: 'daysoff',
      bottomNavigationBar:
          AppTabBar(currentIndex: _tab, onTap: (i) => setState(() => _tab = i)),
      body: Padding(
        padding: const EdgeInsets.all(AppSpacing.containerMargin),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SegmentedToggle(
              segments: const ['Timeline', 'Calendar'],
              selectedIndex: _seg,
              onChanged: (i) => setState(() => _seg = i),
            ),
            const SizedBox(height: AppSpacing.xl),
            DaysOffButton(
              label: 'Confirm dialog demo',
              onPressed: () => showConfirmDialog(
                title: 'Sign out?',
                message: 'You can sign back in anytime.',
                confirmLabel: 'Sign out',
                onConfirm: () {},
              ),
            ),
          ],
        ),
      ),
    );
  }
}
