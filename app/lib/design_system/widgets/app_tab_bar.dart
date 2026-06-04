import 'package:flutter/material.dart';
import '../tokens/app_colors.dart';

class AppTabBar extends StatelessWidget {
  const AppTabBar({super.key, required this.currentIndex, required this.onTap});
  final int currentIndex;
  final ValueChanged<int> onTap;

  @override
  Widget build(BuildContext context) {
    return NavigationBar(
      selectedIndex: currentIndex,
      onDestinationSelected: onTap,
      backgroundColor: Theme.of(context).colorScheme.surface,
      indicatorColor: AppColors.sage.withValues(alpha: 0.25),
      destinations: const [
        NavigationDestination(
            icon: Icon(Icons.calendar_today_outlined),
            selectedIcon: Icon(Icons.calendar_today),
            label: 'Holidays'),
        NavigationDestination(
            icon: Icon(Icons.event_available_outlined),
            selectedIcon: Icon(Icons.event_available),
            label: 'Plan'),
        NavigationDestination(
            icon: Icon(Icons.settings_outlined),
            selectedIcon: Icon(Icons.settings),
            label: 'Settings'),
      ],
    );
  }
}
