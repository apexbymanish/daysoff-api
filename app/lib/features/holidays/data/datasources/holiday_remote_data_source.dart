import 'package:dio/dio.dart';
import '../models/holiday_dto.dart';

class HolidayRemoteDataSource {
  const HolidayRemoteDataSource(this._dio);
  final Dio _dio;

  Future<List<HolidayDto>> fetchHolidays({
    required String country,
    required int year,
  }) async {
    final res = await _dio.get(
      '/v1/holidays',
      queryParameters: {'country': country, 'year': year},
    );
    final data = res.data as Map<String, dynamic>;
    final items = (data['holidays'] as List).cast<Map<String, dynamic>>();
    return items.map(HolidayDto.fromJson).toList();
  }
}
