import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTypography {
  AppTypography._();

  static TextStyle get displayNumeral => GoogleFonts.manrope(
      fontSize: 48, fontWeight: FontWeight.w700, height: 1.0, letterSpacing: -0.96);
  static TextStyle get headlineLg =>
      GoogleFonts.manrope(fontSize: 24, fontWeight: FontWeight.w700, height: 1.33);
  static TextStyle get headlineMd =>
      GoogleFonts.manrope(fontSize: 20, fontWeight: FontWeight.w600, height: 1.4);
  static TextStyle get bodyLg =>
      GoogleFonts.manrope(fontSize: 17, fontWeight: FontWeight.w400, height: 1.53);
  static TextStyle get bodySm =>
      GoogleFonts.manrope(fontSize: 14, fontWeight: FontWeight.w400, height: 1.43);
  static TextStyle get labelCaps => GoogleFonts.jetBrainsMono(
      fontSize: 12, fontWeight: FontWeight.w500, height: 1.33, letterSpacing: 0.6);
}
