import 'package:get/get.dart';
import '../../domain/entities/holiday.dart';
import '../../domain/usecases/get_holidays.dart';

enum HolidaysViewStatus { loading, loaded, empty, error }

const _monthNames = [
  '', 'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];

class HolidaysController extends GetxController {
  HolidaysController(this._getHolidays);
  final GetHolidays _getHolidays;

  // Hardcoded for Phase 2; the country picker + prefs arrive in Phase 4.
  static const String country = 'KR';
  static const int year = 2026;

  final status = HolidaysViewStatus.loading.obs;
  final holidays = <Holiday>[].obs;
  final errorMessage = ''.obs;
  final isCalendarView = false.obs;

  @override
  void onInit() {
    super.onInit();
    load();
  }

  Future<void> load() async {
    status.value = HolidaysViewStatus.loading;
    final result = await _getHolidays(country: country, year: year);
    result.match(
      (failure) {
        errorMessage.value = failure.message;
        status.value = HolidaysViewStatus.error;
      },
      (list) {
        holidays.assignAll(list);
        status.value =
            list.isEmpty ? HolidaysViewStatus.empty : HolidaysViewStatus.loaded;
      },
    );
  }

  void toggleView() => isCalendarView.toggle();

  /// Holidays grouped by spelled-out month name, preserving chronological order.
  Map<String, List<Holiday>> get holidaysByMonth {
    final map = <String, List<Holiday>>{};
    for (final h in holidays) {
      map.putIfAbsent(_monthNames[h.date.month], () => []).add(h);
    }
    return map;
  }
}
