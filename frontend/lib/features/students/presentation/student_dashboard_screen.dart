import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/services/api_service.dart';
import '../../../core/constants/api_constants.dart';
import '../../../shared/widgets/stat_card.dart';

/// Student dashboard displaying academic overview.
class StudentDashboardScreen extends ConsumerStatefulWidget {
  const StudentDashboardScreen({super.key});

  @override
  ConsumerState<StudentDashboardScreen> createState() => _StudentDashboardScreenState();
}

class _StudentDashboardScreenState extends ConsumerState<StudentDashboardScreen> {
  Map<String, dynamic>? _dashboardData;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadDashboard();
  }

  Future<void> _loadDashboard() async {
    try {
      final apiService = ref.read(apiServiceProvider);
      final response = await apiService.get(ApiConstants.studentDashboard);
      if (response.statusCode == 200) {
        setState(() {
          _dashboardData = response.data;
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  Color _getGpaColor(double cgpa) {
    if (cgpa >= 3.7) return AppColors.gpaExcellent;
    if (cgpa >= 3.0) return AppColors.gpaGood;
    if (cgpa >= 2.0) return AppColors.gpaAverage;
    return AppColors.gpaPoor;
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_dashboardData == null) {
      return const Center(child: Text('Failed to load dashboard'));
    }

    final data = _dashboardData!;
    final cgpa = (data['cgpa'] as num).toDouble();

    return Scaffold(
      appBar: AppBar(
        title: Text('Welcome, ${data['full_name']}'),
        actions: [
          Chip(
            label: Text(
              data['academic_status'].toString().replaceAll('_', ' ').toUpperCase(),
              style: const TextStyle(color: Colors.white, fontSize: 12),
            ),
            backgroundColor: data['academic_status'] == 'good_standing'
                ? AppColors.success
                : AppColors.warning,
          ),
          const SizedBox(width: 16),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadDashboard,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Student Info Header
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Row(
                    children: [
                      CircleAvatar(
                        radius: 30,
                        backgroundColor: AppColors.primary,
                        child: Text(
                          data['full_name'][0],
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            data['student_code'],
                            style: Theme.of(context).textTheme.titleLarge,
                          ),
                          Text(
                            '${data['department']} - ${data['program']}',
                            style: Theme.of(context).textTheme.bodyMedium,
                          ),
                          Text(
                            'Level ${data['level']}',
                            style: Theme.of(context).textTheme.bodyMedium,
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),

              // Stats Grid
              Text(
                'Academic Overview',
                style: Theme.of(context).textTheme.headlineMedium,
              ),
              const SizedBox(height: 16),
              GridView.count(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                crossAxisCount: 4,
                crossAxisSpacing: 16,
                mainAxisSpacing: 16,
                childAspectRatio: 1.5,
                children: [
                  StatCard(
                    title: 'CGPA',
                    value: cgpa.toStringAsFixed(2),
                    icon: Icons.trending_up,
                    color: _getGpaColor(cgpa),
                  ),
                  StatCard(
                    title: 'Total Hours',
                    value: '${data['total_hours']}',
                    icon: Icons.access_time,
                    color: AppColors.info,
                  ),
                  StatCard(
                    title: 'Current Semester',
                    value: '${data['current_semester_hours']} hrs',
                    icon: Icons.calendar_today,
                    color: AppColors.secondary,
                  ),
                  StatCard(
                    title: 'Tuition Balance',
                    value: '${data['tuition_balance']} EGP',
                    icon: Icons.account_balance_wallet,
                    color: (data['tuition_balance'] as num) > 0
                        ? AppColors.warning
                        : AppColors.success,
                  ),
                ],
              ),
              const SizedBox(height: 24),

              // Warnings section
              if ((data['warnings_count'] as num) > 0) ...[
                Card(
                  color: AppColors.warning.withOpacity(0.1),
                  child: ListTile(
                    leading: const Icon(Icons.warning_amber, color: AppColors.warning),
                    title: Text(
                      'Academic Warning (${data['warnings_count']})',
                      style: const TextStyle(
                        color: AppColors.warning,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    subtitle: const Text(
                      'Your CGPA is below the minimum threshold. Please consult your advisor.',
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
