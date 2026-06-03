import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/services/api_service.dart';
import '../../../core/constants/api_constants.dart';

/// Attendance screen showing student's attendance summary.
class AttendanceScreen extends ConsumerStatefulWidget {
  const AttendanceScreen({super.key});

  @override
  ConsumerState<AttendanceScreen> createState() => _AttendanceScreenState();
}

class _AttendanceScreenState extends ConsumerState<AttendanceScreen> {
  List<dynamic> _attendanceSummary = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadAttendance();
  }

  Future<void> _loadAttendance() async {
    try {
      final apiService = ref.read(apiServiceProvider);
      final response = await apiService.get(ApiConstants.myAttendance);
      if (response.statusCode == 200) {
        setState(() {
          _attendanceSummary = response.data;
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  Color _getPercentageColor(double percentage) {
    if (percentage >= 90) return AppColors.gpaExcellent;
    if (percentage >= 75) return AppColors.gpaGood;
    if (percentage >= 60) return AppColors.gpaAverage;
    return AppColors.gpaPoor;
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Attendance'),
      ),
      body: _attendanceSummary.isEmpty
          ? const Center(child: Text('No attendance records found'))
          : ListView.builder(
              padding: const EdgeInsets.all(24),
              itemCount: _attendanceSummary.length,
              itemBuilder: (context, index) {
                final summary = _attendanceSummary[index];
                final percentage = (summary['attendance_percentage'] as num).toDouble();
                final isBelowMin = summary['is_below_minimum'] as bool;

                return Card(
                  margin: const EdgeInsets.only(bottom: 16),
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Course header
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    '${summary['course_code']} - ${summary['course_name']}',
                                    style: Theme.of(context).textTheme.titleLarge,
                                  ),
                                ],
                              ),
                            ),
                            // Percentage badge
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                              decoration: BoxDecoration(
                                color: _getPercentageColor(percentage).withOpacity(0.1),
                                borderRadius: BorderRadius.circular(20),
                                border: Border.all(
                                  color: _getPercentageColor(percentage),
                                ),
                              ),
                              child: Text(
                                '${percentage.toStringAsFixed(1)}%',
                                style: TextStyle(
                                  color: _getPercentageColor(percentage),
                                  fontWeight: FontWeight.bold,
                                  fontSize: 16,
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),

                        // Progress bar
                        ClipRRect(
                          borderRadius: BorderRadius.circular(4),
                          child: LinearProgressIndicator(
                            value: percentage / 100,
                            backgroundColor: Colors.grey[200],
                            color: _getPercentageColor(percentage),
                            minHeight: 8,
                          ),
                        ),
                        const SizedBox(height: 12),

                        // Stats row
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceAround,
                          children: [
                            _buildStatChip(
                              'Present',
                              '${summary['present_count']}',
                              AppColors.success,
                            ),
                            _buildStatChip(
                              'Absent',
                              '${summary['absent_count']}',
                              AppColors.error,
                            ),
                            _buildStatChip(
                              'Excused',
                              '${summary['excused_count']}',
                              AppColors.info,
                            ),
                            _buildStatChip(
                              'Total',
                              '${summary['total_sessions']}',
                              AppColors.textSecondary,
                            ),
                          ],
                        ),

                        // Warning
                        if (isBelowMin) ...[
                          const SizedBox(height: 12),
                          Container(
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(
                              color: AppColors.error.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: const Row(
                              children: [
                                Icon(Icons.warning, color: AppColors.error, size: 20),
                                SizedBox(width: 8),
                                Text(
                                  'Attendance below minimum (75%). Risk of academic warning.',
                                  style: TextStyle(color: AppColors.error, fontSize: 13),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                );
              },
            ),
    );
  }

  Widget _buildStatChip(String label, String value, Color color) {
    return Column(
      children: [
        Text(
          value,
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: color,
          ),
        ),
      ],
    );
  }
}
