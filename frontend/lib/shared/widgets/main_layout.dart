import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/theme/app_theme.dart';

/// Main application layout with responsive sidebar navigation.
class MainLayout extends ConsumerWidget {
  final Widget child;

  const MainLayout({super.key, required this.child});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentPath = GoRouterState.of(context).uri.path;

    return Scaffold(
      body: Row(
        children: [
          // Sidebar Navigation
          NavigationRail(
            extended: MediaQuery.of(context).size.width > 1200,
            backgroundColor: AppColors.primary,
            unselectedIconTheme: const IconThemeData(color: Colors.white70),
            selectedIconTheme: const IconThemeData(color: Colors.white),
            unselectedLabelTextStyle: const TextStyle(color: Colors.white70),
            selectedLabelTextStyle: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
            indicatorColor: Colors.white24,
            selectedIndex: _getSelectedIndex(currentPath),
            onDestinationSelected: (index) => _onNavSelected(context, index),
            leading: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                children: [
                  const Icon(Icons.school, color: Colors.white, size: 32),
                  const SizedBox(height: 8),
                  if (MediaQuery.of(context).size.width > 1200)
                    const Text(
                      'URS',
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 18,
                      ),
                    ),
                ],
              ),
            ),
            trailing: Expanded(
              child: Align(
                alignment: Alignment.bottomCenter,
                child: Padding(
                  padding: const EdgeInsets.only(bottom: 16.0),
                  child: IconButton(
                    icon: const Icon(Icons.logout, color: Colors.white70),
                    onPressed: () => _logout(context, ref),
                    tooltip: 'Logout',
                  ),
                ),
              ),
            ),
            destinations: const [
              NavigationRailDestination(
                icon: Icon(Icons.dashboard_outlined),
                selectedIcon: Icon(Icons.dashboard),
                label: Text('Dashboard'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.app_registration_outlined),
                selectedIcon: Icon(Icons.app_registration),
                label: Text('Registration'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.grade_outlined),
                selectedIcon: Icon(Icons.grade),
                label: Text('Grades'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.payment_outlined),
                selectedIcon: Icon(Icons.payment),
                label: Text('Finance'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.checklist_outlined),
                selectedIcon: Icon(Icons.checklist),
                label: Text('Attendance'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.supervisor_account_outlined),
                selectedIcon: Icon(Icons.supervisor_account),
                label: Text('Advisor'),
              ),
            ],
          ),
          
          // Main Content Area
          Expanded(
            child: child,
          ),
        ],
      ),
    );
  }

  int _getSelectedIndex(String path) {
    switch (path) {
      case '/dashboard': return 0;
      case '/registration': return 1;
      case '/grades': return 2;
      case '/finance': return 3;
      case '/attendance': return 4;
      case '/advisor': return 5;
      default: return 0;
    }
  }

  void _onNavSelected(BuildContext context, int index) {
    final routes = [
      '/dashboard',
      '/registration',
      '/grades',
      '/finance',
      '/attendance',
      '/advisor',
    ];
    context.go(routes[index]);
  }

  void _logout(BuildContext context, WidgetRef ref) {
    // Clear tokens and navigate to login
    context.go('/login');
  }
}
