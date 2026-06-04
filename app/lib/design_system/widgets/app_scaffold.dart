import 'package:flutter/material.dart';

/// Standard screen scaffold: optional title app bar, body, optional tab bar.
class AppScaffold extends StatelessWidget {
  const AppScaffold({
    super.key,
    required this.body,
    this.title,
    this.bottomNavigationBar,
    this.actions,
  });

  final Widget body;
  final String? title;
  final Widget? bottomNavigationBar;
  final List<Widget>? actions;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: title == null
          ? null
          : AppBar(title: Text(title!), actions: actions),
      body: SafeArea(child: body),
      bottomNavigationBar: bottomNavigationBar,
    );
  }
}
