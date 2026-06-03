import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/services/api_service.dart';
import '../../../core/constants/api_constants.dart';

/// Grades screen displaying student results and GPA.
class GradesScreen extends ConsumerStatefulWidget {
  const GradesScreen({super.key});

  @override
  ConsumerState<GradesScreen> createState() => _GradesScreenState();
}

class _GradesScreenState extends ConsumerState<GradesScreen> {
  List<dynamic> _grades = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadGrades();
  }

  Future<void> _loadGrades() async {
    try {
      final apiService = ref.read(apiServiceProvider);
      final response = await apiService.get(ApiConstants.myGrades);
      if (response.statusCode == 200) {
        setState(() {
          _grades = response.data;
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  Color _getGradeColor(String? letterGrade) {
    if (letterGrade == null) return AppColors.textSecondary;
    if (letterGrade.startsWith('A')) return AppColors.gpaExcellent;
    if (letterGrade.startsWith('B')) return AppColors.gpaGood;
    if (letterGrade.startsWith('C')) return AppColors.gpaAverage;
    return AppColors.gpaPoor;
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Grades'),
        actions: [
          TextButton.icon(
            onPressed: () {},
            icon: const Icon(Icons.description, color: Colors.white),
            label: const Text('Transcript', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
      body: _grades.isEmpty
          ? const Center(child: Text('No grades available yet'))
          : SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Grades table
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Semester Results',
                            style: Theme.of(context).textTheme.titleLarge,
                          ),
                          const SizedBox(height: 16),
                          DataTable(
                            columnSpacing: 24,
                            columns: const [
                              DataColumn(label: Text('Code')),
                              DataColumn(label: Text('Course')),
                              DataColumn(label: Text('Hours'), numeric: true),
                              DataColumn(label: Text('Midterm 1'), numeric: true),
                              DataColumn(label: Text('Midterm 2'), numeric: true),
                              DataColumn(label: Text('Coursework'), numeric: true),
                              DataColumn(label: Text('Final'), numeric: true),
                              DataColumn(label: Text('Total'), numeric: true),
                              DataColumn(label: Text('Grade')),
                              DataColumn(label: Text('Points'), numeric: true),
                            ],
                            rows: _grades.map((grade) {
                              return DataRow(cells: [
                                DataCell(Text(grade['course_code'] ?? '-')),
                                DataCell(
                                  SizedBox(
                                    width: 150,
                                    child: Text(
                                      grade['course_name'] ?? '-',
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                ),
                                DataCell(Text('${grade['credit_hours'] ?? '-'}')),
                                DataCell(Text('${grade['midterm1'] ?? '-'}')),
                                DataCell(Text('${grade['midterm2'] ?? '-'}')),
                                DataCell(Text('${grade['coursework'] ?? '-'}')),
                                DataCell(Text('${grade['final_exam'] ?? '-'}')),
                                DataCell(Text(
                                  '${grade['total_score'] ?? '-'}',
                                  style: const TextStyle(fontWeight: FontWeight.bold),
                                )),
                                DataCell(
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                    decoration: BoxDecoration(
                                      color: _getGradeColor(grade['letter_grade']).withOpacity(0.1),
                                      borderRadius: BorderRadius.circular(4),
                                    ),
                                    child: Text(
                                      grade['letter_grade'] ?? '-',
                                      style: TextStyle(
                                        color: _getGradeColor(grade['letter_grade']),
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ),
                                ),
                                DataCell(Text('${grade['grade_points'] ?? '-'}')),
                              ]);
                            }).toList(),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}
