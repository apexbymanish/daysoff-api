import 'package:get/get.dart';
import '../features/holidays/presentation/bindings/holidays_binding.dart';
import '../features/holidays/presentation/pages/holidays_page.dart';
import 'app_routes.dart';

abstract class AppPages {
  static final pages = [
    GetPage(
      name: AppRoutes.holidays,
      page: () => const HolidaysPage(),
      binding: HolidaysBinding(),
    ),
  ];
}
