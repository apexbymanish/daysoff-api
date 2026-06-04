import 'package:dio/dio.dart';
import 'package:get/get.dart';
import '../../../../core/network/dio_client.dart';
import '../../data/datasources/holiday_remote_data_source.dart';
import '../../data/repositories/holiday_repository_impl.dart';
import '../../domain/repositories/holiday_repository.dart';
import '../../domain/usecases/get_holidays.dart';
import '../controllers/holidays_controller.dart';

/// Composition root for the Holidays feature: wires
/// Dio -> RemoteDataSource -> RepositoryImpl -> GetHolidays -> Controller.
class HolidaysBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<Dio>(() => DioClient().raw, fenix: true);
    Get.lazyPut<HolidayRemoteDataSource>(
        () => HolidayRemoteDataSource(Get.find<Dio>()));
    Get.lazyPut<HolidayRepository>(
        () => HolidayRepositoryImpl(Get.find<HolidayRemoteDataSource>()));
    Get.lazyPut<GetHolidays>(() => GetHolidays(Get.find<HolidayRepository>()));
    Get.lazyPut<HolidaysController>(
        () => HolidaysController(Get.find<GetHolidays>()));
  }
}
