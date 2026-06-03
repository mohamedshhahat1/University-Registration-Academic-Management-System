/// Application-wide constants.
class AppConstants {
  // Credit hour limits by CGPA
  static const Map<String, int> creditHourLimits = {
    'high': 21,     // CGPA >= 3.0
    'mid': 18,      // CGPA 2.0-2.99
    'low': 14,      // CGPA 1.0-1.99
    'veryLow': 12,  // CGPA < 1.0
  };

  // Grade scale
  static const Map<String, double> gradePoints = {
    'A+': 4.00, 'A': 4.00, 'A-': 3.70,
    'B+': 3.30, 'B': 3.00, 'B-': 2.70,
    'C+': 2.30, 'C': 2.00, 'C-': 1.70,
    'D+': 1.30, 'D': 1.00, 'F': 0.00,
  };

  // Grade component weights
  static const double midterm1Weight = 0.30;
  static const double midterm2Weight = 0.20;
  static const double courseworkWeight = 0.10;
  static const double finalExamWeight = 0.40;

  // Scholarship thresholds
  static const double scholarshipHighThreshold = 3.7;
  static const double scholarshipMidThreshold = 3.3;
  static const double scholarshipHighDiscount = 0.20;
  static const double scholarshipMidDiscount = 0.10;

  // Academic warning
  static const double academicWarningCgpa = 2.0;
  static const double minAttendancePercentage = 75.0;

  // User roles
  static const String roleStudent = 'student';
  static const String roleAdvisor = 'advisor';
  static const String roleInstructor = 'instructor';
  static const String roleRegistrar = 'registrar';
  static const String roleFinance = 'finance';
  static const String roleAdmin = 'admin';
}
