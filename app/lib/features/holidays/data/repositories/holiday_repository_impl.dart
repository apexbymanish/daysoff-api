import 'package:dio/dio.dart';
import 'package:fpdart/fpdart.dart';
import '../../../../core/error/failure.dart';
import '../../domain/entities/holiday.dart';
import '../../domain/repositories/holiday_repository.dart';
import '../datasources/holiday_remote_data_source.dart';

class HolidayRepositoryImpl implements HolidayRepository {
  const HolidayRepositoryImpl(this._remote);
  final HolidayRemoteDataSource _remote;

  @override
  Future<Either<Failure, List<Holiday>>> getHolidays({
    required String country,
    required int year,
  }) async {
    try {
      final dtos = await _remote.fetchHolidays(country: country, year: year);
      final holidays = dtos.map((d) => d.toEntity()).toList()
        ..sort((a, b) => a.date.compareTo(b.date));
      return Right(holidays);
    } on DioException catch (e) {
      const networkTypes = {
        DioExceptionType.connectionError,
        DioExceptionType.connectionTimeout,
        DioExceptionType.receiveTimeout,
        DioExceptionType.sendTimeout,
      };
      return Left(networkTypes.contains(e.type)
          ? const NetworkFailure()
          : const ServerFailure());
    } catch (_) {
      return const Left(ServerFailure());
    }
  }
}
