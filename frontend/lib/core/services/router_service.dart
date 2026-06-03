import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../../features/auth/presentation/login_screen.dart';
import '../../features/students/presentation/student_dashboard_screen.dart';
import '../../features/registration/presentation/registration_screen.dart';
import '../../features/grades/presentation/grades_screen.dart';
import '../../features/finance/presentation/finance_screen.dart';
import '../../features/attendance/presentation/attendance_screen.dart';
import '../../features/advisors/presentation/advisor_dashboard_screen.dart';
import '../../shared/widgets/main_layout.dart';

/// Auth state notifier to trigger router refresh on login/logout.
final authStateProvider = StateProvider<bool>((ref) => false);

/// Router provider for the application.
final routerProvider = Provider<GoRouter>((ref) {
  // Watch auth state to rebuild router on login/logout
  ref.watch(authStateProvider);

  return GoRouter(
    initialLocation: '/login',
    redirect: (context, state) async {
      final path = state.uri.path;
      final goingToLogin = path == '/login';

      // Check if token exists
      const storage = FlutterSecureStorage();
      final token = await storage.read(key: 'access_token');
      final hasToken = token != null && token.isNotEmpty;

      // Not logged in and trying to access protected route → redirect to login
      if (!hasToken && !goingToLogin) {
        return '/login';
      }

      // Logged in and on login page → redirect to dashboard
      if (hasToken && goingToLogin) {
        return '/dashboard';
      }

      return null; // No redirect needed
    },
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
