/// Whether a holiday grants a weekday off ("free") or lands on a weekend
/// and is "absorbed". Derived in the app — the API does not provide it.
enum HolidayStatus { free, absorbed }

class Holiday {
  const Holiday({required this.date, required this.name, required this.source});

  final DateTime date;
  final String name;
  final String source;

  /// Default weekend until user preferences land (Phase 4).
  static const Set<int> defaultWeekend = {DateTime.saturday, DateTime.sunday};

  bool isOnWeekend([Set<int> weekend = defaultWeekend]) =>
      weekend.contains(date.weekday);

  HolidayStatus status([Set<int> weekend = defaultWeekend]) =>
      isOnWeekend(weekend) ? HolidayStatus.absorbed : HolidayStatus.free;

  @override
  bool operator ==(Object other) =>
      other is Holiday &&
      other.date == date &&
      other.name == name &&
      other.source == source;

  @override
  int get hashCode => Object.hash(date, name, source);
}
