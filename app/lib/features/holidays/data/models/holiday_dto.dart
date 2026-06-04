import '../../domain/entities/holiday.dart';

/// Wire model for one item of `/v1/holidays`.holidays.
class HolidayDto {
  const HolidayDto({required this.date, required this.name, required this.source});

  final String date; // ISO yyyy-MM-dd
  final String name;
  final String source;

  factory HolidayDto.fromJson(Map<String, dynamic> json) => HolidayDto(
        date: json['date'] as String,
        name: json['name'] as String,
        source: json['source'] as String? ?? '',
      );

  Holiday toEntity() =>
      Holiday(date: DateTime.parse(date), name: name, source: source);
}
