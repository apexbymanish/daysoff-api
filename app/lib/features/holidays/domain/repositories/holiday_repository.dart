import 'package:fpdart/fpdart.dart';
import '../../../../core/error/failure.dart';
import '../entities/holiday.dart';

abstract class HolidayRepository {
  Future<Either<Failure, List<Holiday>>> getHolidays({
    required String country,
    required int year,
  });
}
