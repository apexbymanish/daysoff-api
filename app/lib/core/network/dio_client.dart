import 'package:dio/dio.dart';
import '../env.dart';

/// Configured Dio for the /v1 API. Inject `DioClient().raw` into data sources.
class DioClient {
  DioClient([Dio? dio]) : raw = dio ?? Dio() {
    raw.options
      ..baseUrl = Env.apiBaseUrl
      ..connectTimeout = const Duration(seconds: 15)
      ..receiveTimeout = const Duration(seconds: 20)
      ..headers = {'Accept': 'application/json'};
  }

  final Dio raw;
}
