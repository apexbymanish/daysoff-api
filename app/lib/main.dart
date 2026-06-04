import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'app/app_pages.dart';
import 'app/app_routes.dart';
import 'design_system/app_theme.dart';

void main() => runApp(const DaysOffApp());

class DaysOffApp extends StatelessWidget {
  const DaysOffApp({super.key});

  @override
  Widget build(BuildContext context) {
    return GetMaterialApp(
      title: 'daysoff',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      darkTheme: AppTheme.dark,
      themeMode: ThemeMode.system,
      initialRoute: AppRoutes.demo,
      getPages: AppPages.pages,
    );
  }
}
