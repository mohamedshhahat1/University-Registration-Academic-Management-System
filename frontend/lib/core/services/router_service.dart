import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../features/auth/presentation/login_screen.dart';
import '../../features/students/presentation/student_dashboard_screen.dart';
import '../../features/registration/presentation/registration_screen.dart';
import '../../features/grades/presentation/grades_screen.dart';
import '../../features/finance/presentation/finance_screen.dart';
import '../../features/attendance/presentation/attendance_screen.dart';
import '../../features/advisors/presentation/advisor_dashboard_screen.dart';
import '../../shared/widgets/main_layout.dart';

/// Router provider for the application.
final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/login',
    routes: [
      // Authentication
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      
      // Main application shell with sidebar navigation
      ShellRoute(
        builder: (context, state, child) => MainLayout(child: child),
        routes: [
          // Student Dashboard
          GoRoute(
            path: '/dashboard',
            builder: (context, state) => const StudentDashboardScreen(),
          ),
          
          // Registration
          GoRoute(
            path: '/registration',
            builder: (context, state) => const RegistrationScreen(),
          ),
          
          // Grades
          GoRoute(
            path: '/grades',
            builder: (context, state) => const GradesScreen(),
          ),
          
          // Finance
          GoRoute(
            path: '/finance',
            builder: (context, state) => const FinanceScreen(),
          ),
          
          // Attendance
          GoRoute(
            path: '/attendance',
            builder: (context, state) => const AttendanceScreen(),
          ),
          
          // Advisor Dashboard
          GoRoute(
            path: '/advisor',
            builder: (context, state) => const AdvisorDashboardScreen(),
          ),
        ],
      ),
    ],
  );
});
