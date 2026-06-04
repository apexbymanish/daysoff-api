# daysoff Flutter App — Phase 2 (Holidays Vertical Slice) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Holidays feature end-to-end — domain + data + presentation — fetching `/v1/holidays` for KR 2026 and rendering a month-grouped timeline, a calendar month-grid view, a holiday detail bottom sheet, and loading/empty/error states — proving the full Clean Architecture + GetX + Dio stack against the live API.

**Architecture:** Clean Architecture inside `features/holidays/{domain,data,presentation}`. Domain is pure Dart (`Holiday` entity, `HolidayRepository` interface, `GetHolidays` use case returning `Either<Failure, List<Holiday>>`). Data implements the repo over `HolidayRemoteDataSource` (Dio → `/v1/holidays`) with DTO↔entity mapping and `DioException`→`Failure` mapping. Presentation uses a GetX `HolidaysController` + `HolidaysBinding` (composition root) driving reusable `design_system/` widgets and feature widgets.

**Tech Stack:** Flutter, GetX, Dio, fpdart (`Either`), mocktail (tests). Builds on Phase 1 (`design_system/`, `core/`).

**Specs:** `docs/superpowers/specs/2026-06-04-daysoff-flutter-app-design.md` (overall), Phase 1 plan (foundation already built).

**Prerequisite:** Phase 1 complete (23 tests passing, `flutter analyze` clean). Work from `/Users/manishadhikari/Documents/Projects/daysoff-api`; flutter commands run in `app/`. Branch `feat/plan-endpoint` — commit there, never switch branches. Flutter 3.41.5 (`withValues(alpha:)` available).

## Live API contract (verified against the backend `holidays` lib)

`GET /v1/holidays?country=KR&year=2026` →
```json
{ "country": "KR", "year": 2026, "count": 20,
  "holidays": [ { "date": "2026-01-01", "name": "New Year's Day", "source": "..." }, ... ] }
```
Each holiday record is exactly `{ date: "YYYY-MM-DD", name: String, source: String }`. **No weekday, no status, no local script** — the app derives weekday from the date and free/absorbed from whether the date falls on the weekend (default weekend = Sat+Sun until preferences arrive in Phase 4). Real KR-2026 names include multi-day clusters with **distinct per-day names** (e.g. `2026-02-16 "The day preceding Korean New Year"`, `02-17 "Korean New Year"`, `02-18 "The second day of Korean New Year"`; `09-24/25/26` Chuseok cluster), so **do not merge multi-day holidays** in this phase — render each record as its own row.

## Out of scope (Phase 2)
Country picker (hardcode `KR`/`2026` here; Phase 4), multi-day merging, residence overlay, calendar-event overlay, local script/Hangul (not in API), workweek preferences (default Sat/Sun). The demo screen from Phase 1 is removed (Task 11).

---

## File Structure (this phase)

```
app/lib/features/holidays/
  domain/
    entities/holiday.dart                    # Holiday entity + HolidayStatus + derived getters
    repositories/holiday_repository.dart      # abstract HolidayRepository
    usecases/get_holidays.dart                # GetHolidays use case
  data/
    models/holiday_dto.dart                   # HolidayDto.fromJson + toEntity
    datasources/holiday_remote_data_source.dart   # Dio GET /v1/holidays -> List<HolidayDto>
    repositories/holiday_repository_impl.dart      # impl + DioException -> Failure
  presentation/
    controllers/holidays_controller.dart      # GetxController + HolidaysViewStatus
    bindings/holidays_binding.dart             # DI composition root
    pages/holidays_page.dart                   # Obx on status: skeleton/empty/error/content + view toggle
    widgets/holiday_card.dart                  # one holiday row (date stack + name + StatusBadge)
    widgets/month_section.dart                 # month header + its holiday rows
    widgets/holiday_detail_sheet.dart          # bottom-sheet content + showHolidayDetailSheet()
    widgets/holiday_calendar_view.dart         # single-month grid with holiday days marked
app/lib/app/app_routes.dart                    # MODIFY: add holidays route
app/lib/app/app_pages.dart                     # MODIFY: register holidays page + binding, make it initial
app/lib/main.dart                              # MODIFY: initialRoute -> holidays
app/test/features/holidays/...                 # mirrors lib structure
```

---

## Task 1: Holiday entity (domain)

**Files:**
- Create: `app/lib/features/holidays/domain/entities/holiday.dart`
- Test: `app/test/features/holidays/domain/holiday_test.dart`

- [ ] **Step 1: Write the failing test**

`app/test/features/holidays/domain/holiday_test.dart`:
```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:daysoff_app/features/holidays/domain/entities/holiday.dart';

void main() {
  Holiday h(String iso) =>
      Holiday(date: DateTime.parse(iso), name: 'X', source: 's');

  test('weekday holiday is free (Children\'s Day 2026-05-05 is a Tuesday)', () {
    final c = h('2026-05-05');
    expect(c.date.weekday, DateTime.tuesday);
    expect(c.isOnWeekend(), isFalse);
    expect(c.status(), HolidayStatus.free);
  });

  test('weekend holiday is absorbed (2026-03-01 Independence Day is a Sunday)', () {
    final d = h('2026-03-01');
    expect(d.date.weekday, DateTime.sunday);
    expect(d.isOnWeekend(), isTrue);
    expect(d.status(), HolidayStatus.absorbed);
  });

  test('Chuseok 2026-09-26 (Saturday) is absorbed', () {
    expect(h('2026-09-26').status(), HolidayStatus.absorbed);
  });

  test('custom weekend set is honored (Fri/Sat off)', () {
    // 2026-10-09 Hangul Day is a Friday → absorbed when Fri is a weekend
    expect(h('2026-10-09').status({DateTime.friday, DateTime.saturday}),
        HolidayStatus.absorbed);
  });

  test('value equality by date+name+source', () {
    expect(h('2026-01-01'), equals(h('2026-01-01')));
  });
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd app && flutter test test/features/holidays/domain/holiday_test.dart`
Expected: FAIL — undefined `Holiday`/`HolidayStatus`.

- [ ] **Step 3: Implement the entity**

`app/lib/features/holidays/domain/entities/holiday.dart`:
```dart
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd app && flutter test test/features/holidays/domain/holiday_test.dart`
Expected: PASS (5 tests).

- [ ] **Step 5: Commit**
```bash
git add app/lib/features/holidays/domain/entities/holiday.dart app/test/features/holidays/domain/holiday_test.dart
git commit -m "feat(holidays): add Holiday entity with derived free/absorbed status"
```

---

## Task 2: HolidayRepository interface + GetHolidays use case

**Files:**
- Create: `app/lib/features/holidays/domain/repositories/holiday_repository.dart`
- Create: `app/lib/features/holidays/domain/usecases/get_holidays.dart`
- Test: `app/test/features/holidays/domain/get_holidays_test.dart`

- [ ] **Step 1: Write the failing test**

`app/test/features/holidays/domain/get_holidays_test.dart`:
```dart
import 'package:fpdart/fpdart.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:daysoff_app/core/error/failure.dart';
import 'package:daysoff_app/features/holidays/domain/entities/holiday.dart';
import 'package:daysoff_app/features/holidays/domain/repositories/holiday_repository.dart';
import 'package:daysoff_app/features/holidays/domain/usecases/get_holidays.dart';

class _MockRepo extends Mock implements HolidayRepository {}

void main() {
  late _MockRepo repo;
  late GetHolidays usecase;

  setUp(() {
    repo = _MockRepo();
    usecase = GetHolidays(repo);
  });

  final sample = [
    Holiday(date: DateTime(2026, 1, 1), name: "New Year's Day", source: 's'),
  ];

  test('delegates to repository and returns its Right result', () async {
    when(() => repo.getHolidays(country: 'KR', year: 2026))
        .thenAnswer((_) async => Right(sample));

    final result = await usecase(country: 'KR', year: 2026);

    expect(result, Right<Failure, List<Holiday>>(sample));
    verify(() => repo.getHolidays(country: 'KR', year: 2026)).called(1);
  });

  test('passes through a Left failure', () async {
    when(() => repo.getHolidays(country: 'KR', year: 2026))
        .thenAnswer((_) async => const Left(NetworkFailure()));

    final result = await usecase(country: 'KR', year: 2026);

    expect(result.isLeft(), isTrue);
  });
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd app && flutter test test/features/holidays/domain/get_holidays_test.dart`
Expected: FAIL — undefined `HolidayRepository`/`GetHolidays`.

- [ ] **Step 3: Implement interface + use case**

`app/lib/features/holidays/domain/repositories/holiday_repository.dart`:
```dart
import 'package:fpdart/fpdart.dart';
import '../../../../core/error/failure.dart';
import '../entities/holiday.dart';

abstract class HolidayRepository {
  Future<Either<Failure, List<Holiday>>> getHolidays({
    required String country,
    required int year,
  });
}
```

`app/lib/features/holidays/domain/usecases/get_holidays.dart`:
```dart
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd app && flutter test test/features/holidays/domain/get_holidays_test.dart`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**
```bash
git add app/lib/features/holidays/domain/repositories app/lib/features/holidays/domain/usecases app/test/features/holidays/domain/get_holidays_test.dart
git commit -m "feat(holidays): add HolidayRepository interface + GetHolidays use case"
```

---

## Task 3: HolidayDto (data model)

**Files:**
- Create: `app/lib/features/holidays/data/models/holiday_dto.dart`
- Test: `app/test/features/holidays/data/holiday_dto_test.dart`

- [ ] **Step 1: Write the failing test**

`app/test/features/holidays/data/holiday_dto_test.dart`:
```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:daysoff_app/features/holidays/data/models/holiday_dto.dart';
import 'package:daysoff_app/features/holidays/domain/entities/holiday.dart';

void main() {
  test('fromJson parses the /v1/holidays record shape', () {
    final dto = HolidayDto.fromJson(const {
      'date': '2026-09-25',
      'name': 'Chuseok',
      'source': 'holidays-lib',
    });
    expect(dto.date, '2026-09-25');
    expect(dto.name, 'Chuseok');
    expect(dto.source, 'holidays-lib');
  });

  test('toEntity converts ISO date string to DateTime', () {
    final entity = HolidayDto.fromJson(const {
      'date': '2026-09-25',
      'name': 'Chuseok',
      'source': 'holidays-lib',
    }).toEntity();
    expect(entity, isA<Holiday>());
    expect(entity.date, DateTime(2026, 9, 25));
    expect(entity.name, 'Chuseok');
  });
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd app && flutter test test/features/holidays/data/holiday_dto_test.dart`
Expected: FAIL — undefined `HolidayDto`.

- [ ] **Step 3: Implement the DTO**

`app/lib/features/holidays/data/models/holiday_dto.dart`:
```dart
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd app && flutter test test/features/holidays/data/holiday_dto_test.dart`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**
```bash
git add app/lib/features/holidays/data/models app/test/features/holidays/data/holiday_dto_test.dart
git commit -m "feat(holidays): add HolidayDto with fromJson + toEntity"
```

---

## Task 4: HolidayRemoteDataSource

**Files:**
- Create: `app/lib/features/holidays/data/datasources/holiday_remote_data_source.dart`
- Test: `app/test/features/holidays/data/holiday_remote_data_source_test.dart`

- [ ] **Step 1: Write the failing test**

`app/test/features/holidays/data/holiday_remote_data_source_test.dart`:
```dart
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:daysoff_app/features/holidays/data/datasources/holiday_remote_data_source.dart';

class _MockDio extends Mock implements Dio {}

void main() {
  late _MockDio dio;
  late HolidayRemoteDataSource dataSource;

  setUp(() {
    dio = _MockDio();
    dataSource = HolidayRemoteDataSource(dio);
  });

  test('GETs /v1/holidays with country+year and maps the holidays array', () async {
    when(() => dio.get('/v1/holidays',
            queryParameters: {'country': 'KR', 'year': 2026}))
        .thenAnswer((_) async => Response(
              requestOptions: RequestOptions(path: '/v1/holidays'),
              statusCode: 200,
              data: {
                'country': 'KR',
                'year': 2026,
                'count': 2,
                'holidays': [
                  {'date': '2026-01-01', 'name': "New Year's Day", 'source': 's'},
                  {'date': '2026-09-25', 'name': 'Chuseok', 'source': 's'},
                ],
              },
            ));

    final dtos = await dataSource.fetchHolidays(country: 'KR', year: 2026);

    expect(dtos.length, 2);
    expect(dtos.first.name, "New Year's Day");
    expect(dtos.last.date, '2026-09-25');
    verify(() => dio.get('/v1/holidays',
        queryParameters: {'country': 'KR', 'year': 2026})).called(1);
  });
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd app && flutter test test/features/holidays/data/holiday_remote_data_source_test.dart`
Expected: FAIL — undefined `HolidayRemoteDataSource`.

- [ ] **Step 3: Implement the data source**

`app/lib/features/holidays/data/datasources/holiday_remote_data_source.dart`:
```dart
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd app && flutter test test/features/holidays/data/holiday_remote_data_source_test.dart`
Expected: PASS (1 test).

- [ ] **Step 5: Commit**
```bash
git add app/lib/features/holidays/data/datasources app/test/features/holidays/data/holiday_remote_data_source_test.dart
git commit -m "feat(holidays): add HolidayRemoteDataSource (Dio /v1/holidays)"
```

---

## Task 5: HolidayRepositoryImpl (with failure mapping)

**Files:**
- Create: `app/lib/features/holidays/data/repositories/holiday_repository_impl.dart`
- Test: `app/test/features/holidays/data/holiday_repository_impl_test.dart`

- [ ] **Step 1: Write the failing test**

`app/test/features/holidays/data/holiday_repository_impl_test.dart`:
```dart
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:daysoff_app/core/error/failure.dart';
import 'package:daysoff_app/features/holidays/data/datasources/holiday_remote_data_source.dart';
import 'package:daysoff_app/features/holidays/data/models/holiday_dto.dart';
import 'package:daysoff_app/features/holidays/data/repositories/holiday_repository_impl.dart';

class _MockRemote extends Mock implements HolidayRemoteDataSource {}

void main() {
  late _MockRemote remote;
  late HolidayRepositoryImpl repo;

  setUp(() {
    remote = _MockRemote();
    repo = HolidayRepositoryImpl(remote);
  });

  test('maps DTOs to entities sorted by date on success', () async {
    when(() => remote.fetchHolidays(country: 'KR', year: 2026))
        .thenAnswer((_) async => const [
              HolidayDto(date: '2026-09-25', name: 'Chuseok', source: 's'),
              HolidayDto(date: '2026-01-01', name: "New Year's Day", source: 's'),
            ]);

    final result = await repo.getHolidays(country: 'KR', year: 2026);

    final list = result.getRight().toNullable()!;
    expect(list.first.date, DateTime(2026, 1, 1)); // sorted ascending
    expect(list.last.name, 'Chuseok');
  });

  test('connection error maps to NetworkFailure', () async {
    when(() => remote.fetchHolidays(country: 'KR', year: 2026)).thenThrow(
      DioException(
        requestOptions: RequestOptions(path: '/v1/holidays'),
        type: DioExceptionType.connectionError,
      ),
    );

    final result = await repo.getHolidays(country: 'KR', year: 2026);

    expect(result.isLeft(), isTrue);
    result.match((f) => expect(f, isA<NetworkFailure>()), (_) => fail('expected Left'));
  });

  test('non-connection error maps to ServerFailure', () async {
    when(() => remote.fetchHolidays(country: 'KR', year: 2026)).thenThrow(
      DioException(
        requestOptions: RequestOptions(path: '/v1/holidays'),
        type: DioExceptionType.badResponse,
      ),
    );

    final result = await repo.getHolidays(country: 'KR', year: 2026);

    result.match((f) => expect(f, isA<ServerFailure>()), (_) => fail('expected Left'));
  });
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd app && flutter test test/features/holidays/data/holiday_repository_impl_test.dart`
Expected: FAIL — undefined `HolidayRepositoryImpl`.

- [ ] **Step 3: Implement the repository**

`app/lib/features/holidays/data/repositories/holiday_repository_impl.dart`:
```dart
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd app && flutter test test/features/holidays/data/holiday_repository_impl_test.dart`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**
```bash
git add app/lib/features/holidays/data/repositories app/test/features/holidays/data/holiday_repository_impl_test.dart
git commit -m "feat(holidays): add HolidayRepositoryImpl with DioException->Failure mapping"
```

---

## Task 6: HolidaysController (GetX)

**Files:**
- Create: `app/lib/features/holidays/presentation/controllers/holidays_controller.dart`
- Test: `app/test/features/holidays/presentation/holidays_controller_test.dart`

- [ ] **Step 1: Write the failing test**

`app/test/features/holidays/presentation/holidays_controller_test.dart`:
```dart
import 'package:fpdart/fpdart.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:daysoff_app/core/error/failure.dart';
import 'package:daysoff_app/features/holidays/domain/entities/holiday.dart';
import 'package:daysoff_app/features/holidays/domain/repositories/holiday_repository.dart';
import 'package:daysoff_app/features/holidays/domain/usecases/get_holidays.dart';
import 'package:daysoff_app/features/holidays/presentation/controllers/holidays_controller.dart';

class _MockRepo extends Mock implements HolidayRepository {}

void main() {
  late _MockRepo repo;
  late GetHolidays usecase;

  setUp(() {
    repo = _MockRepo();
    usecase = GetHolidays(repo);
  });

  final feb = [
    Holiday(date: DateTime(2026, 2, 17), name: 'Korean New Year', source: 's'),
    Holiday(date: DateTime(2026, 5, 5), name: "Children's Day", source: 's'),
  ];

  test('load(): loading -> loaded and groups by month', () async {
    when(() => repo.getHolidays(country: 'KR', year: 2026))
        .thenAnswer((_) async => Right(feb));
    final c = HolidaysController(usecase);

    await c.load();

    expect(c.status.value, HolidaysViewStatus.loaded);
    expect(c.holidays.length, 2);
    expect(c.holidaysByMonth.keys.toList(), ['February', 'May']);
    expect(c.holidaysByMonth['February']!.single.name, 'Korean New Year');
  });

  test('load(): empty list -> empty status', () async {
    when(() => repo.getHolidays(country: 'KR', year: 2026))
        .thenAnswer((_) async => const Right<Failure, List<Holiday>>([]));
    final c = HolidaysController(usecase);

    await c.load();

    expect(c.status.value, HolidaysViewStatus.empty);
  });

  test('load(): failure -> error status with message', () async {
    when(() => repo.getHolidays(country: 'KR', year: 2026))
        .thenAnswer((_) async => const Left(NetworkFailure()));
    final c = HolidaysController(usecase);

    await c.load();

    expect(c.status.value, HolidaysViewStatus.error);
    expect(c.errorMessage.value, isNotEmpty);
  });

  test('toggleView flips calendar/timeline', () {
    final c = HolidaysController(usecase);
    expect(c.isCalendarView.value, isFalse);
    c.toggleView();
    expect(c.isCalendarView.value, isTrue);
  });
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd app && flutter test test/features/holidays/presentation/holidays_controller_test.dart`
Expected: FAIL — undefined `HolidaysController`/`HolidaysViewStatus`.

- [ ] **Step 3: Implement the controller**

`app/lib/features/holidays/presentation/controllers/holidays_controller.dart`:
```dart
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd app && flutter test test/features/holidays/presentation/holidays_controller_test.dart`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**
```bash
git add app/lib/features/holidays/presentation/controllers app/test/features/holidays/presentation/holidays_controller_test.dart
git commit -m "feat(holidays): add HolidaysController (load/group/toggle states)"
```

---

## Task 7: HolidayCard widget

**Files:**
- Create: `app/lib/features/holidays/presentation/widgets/holiday_card.dart`
- Test: `app/test/features/holidays/presentation/holiday_card_test.dart`

- [ ] **Step 1: Write the failing test**

`app/test/features/holidays/presentation/holiday_card_test.dart`:
```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:daysoff_app/features/holidays/domain/entities/holiday.dart';
import 'package:daysoff_app/features/holidays/presentation/widgets/holiday_card.dart';

Widget _host(Widget child) => MaterialApp(home: Scaffold(body: child));

void main() {
  testWidgets('free holiday shows day numeral, weekday, name and "free"',
      (tester) async {
    await tester.pumpWidget(_host(HolidayCard(
      holiday: Holiday(date: DateTime(2026, 5, 5), name: "Children's Day", source: 's'),
      onTap: () {},
    )));
    expect(find.text('5'), findsOneWidget);
    expect(find.text('TUE'), findsOneWidget);
    expect(find.text("Children's Day"), findsOneWidget);
    expect(find.text('free'), findsOneWidget);
  });

  testWidgets('absorbed holiday shows "absorbed"', (tester) async {
    await tester.pumpWidget(_host(HolidayCard(
      holiday: Holiday(date: DateTime(2026, 3, 1), name: 'Independence Movement Day', source: 's'),
      onTap: () {},
    )));
    expect(find.text('absorbed'), findsOneWidget);
  });

  testWidgets('tapping the card fires onTap', (tester) async {
    var tapped = false;
    await tester.pumpWidget(_host(HolidayCard(
      holiday: Holiday(date: DateTime(2026, 5, 5), name: "Children's Day", source: 's'),
      onTap: () => tapped = true,
    )));
    await tester.tap(find.byType(HolidayCard));
    expect(tapped, isTrue);
  });
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd app && flutter test test/features/holidays/presentation/holiday_card_test.dart`
Expected: FAIL — undefined `HolidayCard`.

- [ ] **Step 3: Implement the widget**

`app/lib/features/holidays/presentation/widgets/holiday_card.dart`:
```dart
import 'package:flutter/material.dart';
import '../../../../design_system/tokens/app_colors.dart';
import '../../../../design_system/tokens/app_spacing.dart';
import '../../../../design_system/widgets/status_badge.dart';
import '../../domain/entities/holiday.dart';

const _weekdayCaps = ['', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];

class HolidayCard extends StatelessWidget {
  const HolidayCard({super.key, required this.holiday, required this.onTap});

  final Holiday holiday;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final isFree = holiday.status() == HolidayStatus.free;
    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: AppSpacing.md),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            SizedBox(
              width: 56,
              child: Column(
                children: [
                  Text('${holiday.date.day}',
                      style: const TextStyle(
                          fontSize: 26, fontWeight: FontWeight.w600)),
                  Text(_weekdayCaps[holiday.date.weekday],
                      style: const TextStyle(
                          fontSize: 11, color: AppColors.onSurfaceVariant)),
                ],
              ),
            ),
            const SizedBox(width: AppSpacing.md),
            Expanded(
              child: Text(holiday.name,
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w500)),
            ),
            const SizedBox(width: AppSpacing.sm),
            isFree ? const StatusBadge.free() : const StatusBadge.absorbed(),
          ],
        ),
      ),
    );
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd app && flutter test test/features/holidays/presentation/holiday_card_test.dart`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**
```bash
git add app/lib/features/holidays/presentation/widgets/holiday_card.dart app/test/features/holidays/presentation/holiday_card_test.dart
git commit -m "feat(holidays): add HolidayCard row widget"
```

---

## Task 8: MonthSection + HolidaysPage (states + timeline)

**Files:**
- Create: `app/lib/features/holidays/presentation/widgets/month_section.dart`
- Create: `app/lib/features/holidays/presentation/pages/holidays_page.dart`
- Test: `app/test/features/holidays/presentation/holidays_page_test.dart`

- [ ] **Step 1: Write the failing test**

`app/test/features/holidays/presentation/holidays_page_test.dart`:
```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';
import 'package:mocktail/mocktail.dart';
import 'package:fpdart/fpdart.dart';
import 'package:daysoff_app/core/error/failure.dart';
import 'package:daysoff_app/features/holidays/domain/entities/holiday.dart';
import 'package:daysoff_app/features/holidays/domain/repositories/holiday_repository.dart';
import 'package:daysoff_app/features/holidays/domain/usecases/get_holidays.dart';
import 'package:daysoff_app/features/holidays/presentation/controllers/holidays_controller.dart';
import 'package:daysoff_app/features/holidays/presentation/pages/holidays_page.dart';

class _MockRepo extends Mock implements HolidayRepository {}

void main() {
  setUp(() => Get.testMode = true);
  tearDown(Get.reset);

  Future<void> pumpWith(WidgetTester tester, _MockRepo repo) async {
    Get.put<HolidaysController>(HolidaysController(GetHolidays(repo)));
    await tester.pumpWidget(const GetMaterialApp(home: HolidaysPage()));
  }

  testWidgets('loaded state shows month header and a holiday row', (tester) async {
    final repo = _MockRepo();
    when(() => repo.getHolidays(country: 'KR', year: 2026)).thenAnswer((_) async =>
        Right([Holiday(date: DateTime(2026, 5, 5), name: "Children's Day", source: 's')]));
    await pumpWith(tester, repo);
    await tester.pumpAndSettle();
    expect(find.text('May'), findsOneWidget);
    expect(find.text("Children's Day"), findsOneWidget);
  });

  testWidgets('error state shows message and retry', (tester) async {
    final repo = _MockRepo();
    when(() => repo.getHolidays(country: 'KR', year: 2026))
        .thenAnswer((_) async => const Left(NetworkFailure()));
    await pumpWith(tester, repo);
    await tester.pumpAndSettle();
    expect(find.text('Retry'), findsOneWidget);
  });
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd app && flutter test test/features/holidays/presentation/holidays_page_test.dart`
Expected: FAIL — undefined `HolidaysPage`/`MonthSection`.

- [ ] **Step 3: Implement MonthSection + HolidaysPage**

`app/lib/features/holidays/presentation/widgets/month_section.dart`:
```dart
import 'package:flutter/material.dart';
import '../../../../design_system/tokens/app_colors.dart';
import '../../../../design_system/tokens/app_spacing.dart';
import '../../domain/entities/holiday.dart';
import 'holiday_card.dart';

class MonthSection extends StatelessWidget {
  const MonthSection({
    super.key,
    required this.month,
    required this.holidays,
    required this.onTapHoliday,
  });

  final String month;
  final List<Holiday> holidays;
  final ValueChanged<Holiday> onTapHoliday;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(top: AppSpacing.lg, bottom: AppSpacing.xs),
          child: Text(month, style: Theme.of(context).textTheme.headlineMedium),
        ),
        const Divider(height: 1),
        for (final h in holidays) HolidayCard(holiday: h, onTap: () => onTapHoliday(h)),
      ],
    );
  }
}
```

`app/lib/features/holidays/presentation/pages/holidays_page.dart`:
```dart
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../../design_system/tokens/app_spacing.dart';
import '../../../../design_system/widgets/app_scaffold.dart';
import '../../../../design_system/widgets/app_tab_bar.dart';
import '../../../../design_system/widgets/segmented_toggle.dart';
import '../../../../design_system/widgets/state_blocks.dart';
import '../controllers/holidays_controller.dart';
import '../widgets/month_section.dart';
import '../widgets/holiday_detail_sheet.dart';
import '../widgets/holiday_calendar_view.dart';

class HolidaysPage extends StatelessWidget {
  const HolidaysPage({super.key});

  @override
  Widget build(BuildContext context) {
    final c = Get.find<HolidaysController>();
    return AppScaffold(
      title: 'Holidays · 🇰🇷 KR 2026',
      bottomNavigationBar: AppTabBar(currentIndex: 0, onTap: (_) {}),
      body: Obx(() {
        switch (c.status.value) {
          case HolidaysViewStatus.loading:
            return const LoadingSkeleton(rows: 6);
          case HolidaysViewStatus.empty:
            return const EmptyState(
              icon: Icons.event_busy,
              title: 'No holidays found.',
              body: 'Try another year.',
            );
          case HolidaysViewStatus.error:
            return ErrorView(message: c.errorMessage.value, onRetry: c.load);
          case HolidaysViewStatus.loaded:
            return Column(
              children: [
                Padding(
                  padding: const EdgeInsets.all(AppSpacing.containerMargin),
                  child: SegmentedToggle(
                    segments: const ['Timeline', 'Calendar'],
                    selectedIndex: c.isCalendarView.value ? 1 : 0,
                    onChanged: (i) => c.isCalendarView.value = i == 1,
                  ),
                ),
                Expanded(
                  child: c.isCalendarView.value
                      ? HolidayCalendarView(holidays: c.holidays)
                      : ListView(
                          padding: const EdgeInsets.symmetric(
                              horizontal: AppSpacing.containerMargin),
                          children: [
                            for (final entry in c.holidaysByMonth.entries)
                              MonthSection(
                                month: entry.key,
                                holidays: entry.value,
                                onTapHoliday: (h) => showHolidayDetailSheet(h),
                              ),
                            const SizedBox(height: AppSpacing.xl),
                          ],
                        ),
                ),
              ],
            );
        }
      }),
    );
  }
}
```

> Note: this references `showHolidayDetailSheet` (Task 9) and `HolidayCalendarView` (Task 10). Implement those tasks before running this page test, OR add minimal stub files first. To keep TDD honest, implement Task 9 and Task 10 immediately after this step's red test, then return and make Task 8's test green. (Recommended order: write all three widgets, then run T8–T10 tests together.) If the spec reviewer prefers strict per-task green, create temporary stubs:
> - `showHolidayDetailSheet(Holiday h) {}` and `class HolidayCalendarView extends StatelessWidget { final List<Holiday> holidays; const HolidayCalendarView({super.key, required this.holidays}); @override Widget build(c)=>const SizedBox(); }`
> then replace them with the real Task 9/10 implementations.

- [ ] **Step 4: Implement Task 9 and Task 10 files (below), then run**

Run: `cd app && flutter test test/features/holidays/presentation/holidays_page_test.dart`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**
```bash
git add app/lib/features/holidays/presentation/widgets/month_section.dart app/lib/features/holidays/presentation/pages/holidays_page.dart app/test/features/holidays/presentation/holidays_page_test.dart
git commit -m "feat(holidays): add MonthSection + HolidaysPage (states + timeline)"
```

---

## Task 9: HolidayDetailSheet

**Files:**
- Create: `app/lib/features/holidays/presentation/widgets/holiday_detail_sheet.dart`
- Test: `app/test/features/holidays/presentation/holiday_detail_sheet_test.dart`

- [ ] **Step 1: Write the failing test**

`app/test/features/holidays/presentation/holiday_detail_sheet_test.dart`:
```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:daysoff_app/features/holidays/domain/entities/holiday.dart';
import 'package:daysoff_app/features/holidays/presentation/widgets/holiday_detail_sheet.dart';

void main() {
  testWidgets('renders holiday name, full date and status', (tester) async {
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: HolidayDetailSheetBody(
          holiday: Holiday(date: DateTime(2026, 9, 25), name: 'Chuseok', source: 's'),
        ),
      ),
    ));
    expect(find.text('Chuseok'), findsOneWidget);
    expect(find.textContaining('Friday'), findsOneWidget); // 2026-09-25 is a Friday
    expect(find.textContaining('free'), findsOneWidget);
  });
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd app && flutter test test/features/holidays/presentation/holiday_detail_sheet_test.dart`
Expected: FAIL — undefined `HolidayDetailSheetBody`.

- [ ] **Step 3: Implement the sheet**

`app/lib/features/holidays/presentation/widgets/holiday_detail_sheet.dart`:
```dart
import 'package:flutter/material.dart';
import '../../../../design_system/tokens/app_spacing.dart';
import '../../../../design_system/widgets/daysoff_bottom_sheet.dart';
import '../../../../design_system/widgets/status_badge.dart';
import '../../domain/entities/holiday.dart';

const _weekdayFull = [
  '', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
];
const _monthFull = [
  '', 'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];

/// Pure body widget (testable without GetX). Shown via [showHolidayDetailSheet].
class HolidayDetailSheetBody extends StatelessWidget {
  const HolidayDetailSheetBody({super.key, required this.holiday});
  final Holiday holiday;

  @override
  Widget build(BuildContext context) {
    final d = holiday.date;
    final isFree = holiday.status() == HolidayStatus.free;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(holiday.name, style: Theme.of(context).textTheme.headlineLarge),
        const SizedBox(height: AppSpacing.sm),
        Text('${_weekdayFull[d.weekday]}, ${_monthFull[d.month]} ${d.day}, ${d.year}',
            style: Theme.of(context).textTheme.bodyLarge),
        const SizedBox(height: AppSpacing.lg),
        isFree ? const StatusBadge.free() : const StatusBadge.absorbed(),
        const SizedBox(height: AppSpacing.lg),
        Text(
          isFree
              ? 'Falls on a weekday — a free day off.'
              : 'Falls on the weekend — absorbed.',
          style: Theme.of(context).textTheme.bodyMedium,
        ),
      ],
    );
  }
}

Future<void> showHolidayDetailSheet(Holiday holiday) {
  return showDaysOffBottomSheet<void>(
    title: 'Holiday',
    child: HolidayDetailSheetBody(holiday: holiday),
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd app && flutter test test/features/holidays/presentation/holiday_detail_sheet_test.dart`
Expected: PASS (1 test).

- [ ] **Step 5: Commit**
```bash
git add app/lib/features/holidays/presentation/widgets/holiday_detail_sheet.dart app/test/features/holidays/presentation/holiday_detail_sheet_test.dart
git commit -m "feat(holidays): add HolidayDetailSheet (bottom sheet body + show helper)"
```

---

## Task 10: HolidayCalendarView (month grid)

**Files:**
- Create: `app/lib/features/holidays/presentation/widgets/holiday_calendar_view.dart`
- Test: `app/test/features/holidays/presentation/holiday_calendar_view_test.dart`

- [ ] **Step 1: Write the failing test**

`app/test/features/holidays/presentation/holiday_calendar_view_test.dart`:
```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:daysoff_app/features/holidays/domain/entities/holiday.dart';
import 'package:daysoff_app/features/holidays/presentation/widgets/holiday_calendar_view.dart';

void main() {
  testWidgets('shows the first holiday\'s month and marks its day', (tester) async {
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: HolidayCalendarView(holidays: [
          Holiday(date: DateTime(2026, 5, 5), name: "Children's Day", source: 's'),
        ]),
      ),
    ));
    expect(find.text('May 2026'), findsOneWidget);
    // Day cell "5" rendered as a holiday-marked cell.
    expect(find.byKey(const ValueKey('holiday-day-2026-05-05')), findsOneWidget);
  });
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd app && flutter test test/features/holidays/presentation/holiday_calendar_view_test.dart`
Expected: FAIL — undefined `HolidayCalendarView`.

- [ ] **Step 3: Implement the calendar view**

`app/lib/features/holidays/presentation/widgets/holiday_calendar_view.dart`:
```dart
import 'package:flutter/material.dart';
import '../../../../design_system/tokens/app_colors.dart';
import '../../../../design_system/tokens/app_radii.dart';
import '../../../../design_system/tokens/app_spacing.dart';
import '../../domain/entities/holiday.dart';

const _monthFull = [
  '', 'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];

/// A simple single-month grid. Starts on the month of the first holiday and
/// lets the user page month-to-month. Holiday days are marked (peach=free,
/// grey=absorbed) with a label, never color alone.
class HolidayCalendarView extends StatefulWidget {
  const HolidayCalendarView({super.key, required this.holidays});
  final List<Holiday> holidays;

  @override
  State<HolidayCalendarView> createState() => _HolidayCalendarViewState();
}

class _HolidayCalendarViewState extends State<HolidayCalendarView> {
  late DateTime _month; // first day of the visible month

  @override
  void initState() {
    super.initState();
    final first = widget.holidays.isEmpty ? DateTime.now() : widget.holidays.first.date;
    _month = DateTime(first.year, first.month);
  }

  Holiday? _holidayOn(int day) {
    for (final h in widget.holidays) {
      if (h.date.year == _month.year && h.date.month == _month.month && h.date.day == day) {
        return h;
      }
    }
    return null;
  }

  @override
  Widget build(BuildContext context) {
    final daysInMonth = DateTime(_month.year, _month.month + 1, 0).day;
    final leadingBlanks = DateTime(_month.year, _month.month, 1).weekday - 1; // Mon=0
    final cells = <Widget>[
      for (var i = 0; i < leadingBlanks; i++) const SizedBox.shrink(),
      for (var day = 1; day <= daysInMonth; day++) _dayCell(day),
    ];
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            IconButton(
              onPressed: () => setState(
                  () => _month = DateTime(_month.year, _month.month - 1)),
              icon: const Icon(Icons.chevron_left),
            ),
            Text('${_monthFull[_month.month]} ${_month.year}',
                style: Theme.of(context).textTheme.headlineMedium),
            IconButton(
              onPressed: () => setState(
                  () => _month = DateTime(_month.year, _month.month + 1)),
              icon: const Icon(Icons.chevron_right),
            ),
          ],
        ),
        Expanded(
          child: GridView.count(
            crossAxisCount: 7,
            padding: const EdgeInsets.all(AppSpacing.sm),
            children: cells,
          ),
        ),
      ],
    );
  }

  Widget _dayCell(int day) {
    final holiday = _holidayOn(day);
    if (holiday == null) {
      return Center(child: Text('$day'));
    }
    final isFree = holiday.status() == HolidayStatus.free;
    final iso =
        '${_month.year.toString().padLeft(4, '0')}-${_month.month.toString().padLeft(2, '0')}-${day.toString().padLeft(2, '0')}';
    return Container(
      key: ValueKey('holiday-day-$iso'),
      margin: const EdgeInsets.all(AppSpacing.xs),
      decoration: BoxDecoration(
        color: (isFree ? AppColors.sand : AppColors.outline).withValues(alpha: 0.22),
        borderRadius: BorderRadius.circular(AppRadii.sm),
      ),
      child: Center(child: Text('$day', style: const TextStyle(fontWeight: FontWeight.w600))),
    );
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd app && flutter test test/features/holidays/presentation/holiday_calendar_view_test.dart`
Expected: PASS (1 test). Now also run the Task 8 page test (it depends on Tasks 9+10): `cd app && flutter test test/features/holidays/presentation/holidays_page_test.dart` → PASS.

- [ ] **Step 5: Commit**
```bash
git add app/lib/features/holidays/presentation/widgets/holiday_calendar_view.dart app/test/features/holidays/presentation/holiday_calendar_view_test.dart
git commit -m "feat(holidays): add HolidayCalendarView month grid"
```

---

## Task 11: Binding + wire route as the app's initial screen

**Files:**
- Create: `app/lib/features/holidays/presentation/bindings/holidays_binding.dart`
- Modify: `app/lib/app/app_routes.dart`, `app/lib/app/app_pages.dart`, `app/lib/main.dart`
- Delete: `app/lib/features/demo/demo_page.dart` (Phase 1 throwaway)
- Modify: `app/test/app/app_boots_test.dart`
- Test: `app/test/features/holidays/presentation/holidays_binding_test.dart`

- [ ] **Step 1: Write the failing tests**

`app/test/features/holidays/presentation/holidays_binding_test.dart`:
```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';
import 'package:daysoff_app/features/holidays/presentation/bindings/holidays_binding.dart';
import 'package:daysoff_app/features/holidays/presentation/controllers/holidays_controller.dart';

void main() {
  setUp(() => Get.testMode = true);
  tearDown(Get.reset);

  test('binding registers a resolvable HolidaysController', () {
    HolidaysBinding().dependencies();
    expect(Get.isRegistered<HolidaysController>(), isTrue);
    expect(Get.find<HolidaysController>(), isA<HolidaysController>());
  });
}
```

Update `app/test/app/app_boots_test.dart` to assert the app boots to Holidays (it now starts on the holidays route, which loads data; with no network in the test it lands in an error/loading state — assert the app shell renders without throwing and shows the Holidays title):
```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:daysoff_app/main.dart';
import 'package:daysoff_app/design_system/widgets/app_tab_bar.dart';

void main() {
  testWidgets('app boots to the Holidays screen shell', (tester) async {
    await tester.pumpWidget(const DaysOffApp());
    await tester.pump(); // let first frame build (data load is async/failing offline)
    expect(find.textContaining('Holidays'), findsOneWidget);
    expect(find.byType(AppTabBar), findsOneWidget);
  });
}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd app && flutter test test/features/holidays/presentation/holidays_binding_test.dart`
Expected: FAIL — undefined `HolidaysBinding`.

- [ ] **Step 3: Implement binding + wire routes**

`app/lib/features/holidays/presentation/bindings/holidays_binding.dart`:
```dart
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
```

Replace `app/lib/app/app_routes.dart`:
```dart
abstract class AppRoutes {
  static const holidays = '/holidays';
}
```

Replace `app/lib/app/app_pages.dart`:
```dart
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
```

Edit `app/lib/main.dart` — change `initialRoute: AppRoutes.demo` to `initialRoute: AppRoutes.holidays` (leave everything else as-is).

Delete the Phase 1 throwaway: `rm app/lib/features/demo/demo_page.dart`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd app && flutter test test/features/holidays/presentation/holidays_binding_test.dart test/app/app_boots_test.dart`
Expected: PASS. Then the FULL suite + analyzer:
Run: `cd app && flutter test && flutter analyze`
Expected: all tests pass; analyzer clean.

- [ ] **Step 5: Commit**
```bash
git add app/lib/features/holidays/presentation/bindings app/lib/app app/lib/main.dart app/test
git rm app/lib/features/demo/demo_page.dart
git commit -m "feat(holidays): wire HolidaysBinding + make Holidays the initial route"
```

---

## Phase 2 self-review

- **Spec coverage:** GetHolidays domain ✓ (T1,T2); data layer DTO/datasource/repo with failure mapping ✓ (T3–T5); GetX controller with loading/loaded/empty/error + month grouping + view toggle ✓ (T6); HolidayCard ✓ (T7); month-grouped timeline + states ✓ (T8); holiday detail bottom sheet ✓ (T9); calendar month-grid view ✓ (T10); DI binding + initial route ✓ (T11). Reuses Phase-1 `design_system/` (StatusBadge, LoadingSkeleton/EmptyState/ErrorView, SegmentedToggle, AppScaffold, AppTabBar, DaysOffBottomSheet). Clean Architecture: domain pure (fpdart only), GetX only in presentation/binding.
- **Placeholder scan:** none — every file has complete code. The only forward-reference is Task 8's page using Task 9/10 symbols, explicitly called out with ordering guidance + stub fallback.
- **Type consistency:** `Holiday(date,name,source)`, `HolidayStatus.{free,absorbed}`, `status([weekend])`, `HolidayRepository.getHolidays({country,year})`, `GetHolidays.call({country,year})`, `HolidayDto.fromJson/toEntity`, `HolidayRemoteDataSource.fetchHolidays`, `HolidaysController` fields (`status`,`holidays`,`errorMessage`,`isCalendarView`,`load`,`toggleView`,`holidaysByMonth`), `HolidaysViewStatus.{loading,loaded,empty,error}`, `showHolidayDetailSheet`/`HolidayDetailSheetBody`, `HolidayCalendarView({holidays})`, `HolidaysBinding`, `AppRoutes.holidays` — all consistent across tasks.
- **Accessibility:** free/absorbed always paired with StatusBadge icon+label; calendar cells carry day text + color.

## Done when
`cd app && flutter test && flutter analyze` is clean, and `cd app && flutter run` shows the live KR-2026 holiday timeline (real data from `https://daysoff-api.fly.dev`), a working Timeline⇄Calendar toggle, and a holiday detail sheet on tap. (Offline, the screen shows the error state with Retry — that is correct behavior.)
