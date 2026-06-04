import 'package:fpdart/fpdart.dart';
import '../../../../core/error/failure.dart';
import '../entities/holiday.dart';
import '../repositories/holiday_repository.dart';

class GetHolidays {
  const GetHolidays(this._repository);
  final HolidayRepository _repository;

  Future<Either<Failure, List<Holiday>>> call({
    required String country,
    required int year,
  }) =>
      _repository.getHolidays(country: country, year: year);
}
