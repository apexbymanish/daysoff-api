import 'package:get/get.dart';
import '../features/demo/demo_page.dart';
import 'app_routes.dart';

abstract class AppPages {
  static final pages = [
    GetPage(name: AppRoutes.demo, page: () => const DemoPage()),
  ];
}
