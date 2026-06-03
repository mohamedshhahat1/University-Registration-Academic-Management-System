/// API endpoint constants and configuration.
class ApiConstants {
  // Relative URL - frontend and backend served from same origin
  static const String baseUrl = '/api/v1';
  
  // Auth endpoints
  static const String login = '/auth/login';
  static const String register = '/auth/register';
  static const String refreshToken = '/auth/refresh';
  static const String me = '/auth/me';
  static const String changePassword = '/auth/change-password';
  
  // Student endpoints
  static const String students = '/students';
  static const String studentDashboard = '/students/me/dashboard';
  
  // Course endpoints
  static const String courses = '/courses';
  static const String semesters = '/semesters';
  static const String currentSemester = '/semesters/current';
  static const String departments = '/departments';
  
  // Registration endpoints
  static const String offerings = '/registration/offerings';
  static const String cart = '/registration/cart';
  static const String cartAdd = '/registration/cart/add';
  static const String cartRemove = '/registration/cart/remove';
  static const String cartValidate = '/registration/cart/validate';
  static const String cartSubmit = '/registration/cart/submit';
  static const String approvalsPending = '/registration/approvals/pending';
  
  // Finance endpoints
  static const String tuitionRates = '/finance/tuition-rates';
  static const String invoicesGenerate = '/finance/invoices/generate';
  static const String myInvoices = '/finance/invoices/my';
  static const String payments = '/finance/payments';
  static const String financeSummary = '/finance/summary';
  
  // Grade endpoints
  static const String gradesEnter = '/grades/enter';
  static const String gradesBulk = '/grades/enter/bulk';
  static const String myGrades = '/grades/my';
  static const String transcript = '/grades/transcript';
  static const String calculateGpa = '/grades/calculate-gpa';
  
  // Attendance endpoints
  static const String attendanceRecord = '/attendance/record';
  static const String myAttendance = '/attendance/my/summary';
}
