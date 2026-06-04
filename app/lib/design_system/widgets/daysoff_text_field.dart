import 'package:flutter/material.dart';
import '../tokens/app_colors.dart';
import '../tokens/app_spacing.dart';

class DaysOffTextField extends StatelessWidget {
  const DaysOffTextField({
    super.key,
    required this.label,
    this.controller,
    this.obscureText = false,
    this.errorText,
    this.keyboardType,
  });

  final String label;
  final TextEditingController? controller;
  final bool obscureText;
  final String? errorText;
  final TextInputType? keyboardType;

  bool get _hasError => errorText != null;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: Theme.of(context).textTheme.labelSmall),
        const SizedBox(height: AppSpacing.xs),
        TextField(
          controller: controller,
          obscureText: obscureText,
          keyboardType: keyboardType,
          decoration: InputDecoration(
            isDense: true,
            enabledBorder: UnderlineInputBorder(
              borderSide: BorderSide(
                  color: _hasError ? AppColors.error : AppColors.outline),
            ),
            focusedBorder: UnderlineInputBorder(
              borderSide: BorderSide(
                  color: _hasError ? AppColors.error : AppColors.primary,
                  width: 2),
            ),
          ),
        ),
        if (_hasError) ...[
          const SizedBox(height: AppSpacing.xs),
          Row(
            children: [
              const Icon(Icons.error_outline, size: 14, color: AppColors.error),
              const SizedBox(width: AppSpacing.xs),
              Expanded(
                child: Text(errorText!,
                    style: const TextStyle(color: AppColors.error, fontSize: 12)),
              ),
            ],
          ),
        ],
      ],
    );
  }
}
