import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/services/api_service.dart';
import '../../../core/constants/api_constants.dart';

/// Course registration screen with cart management.
class RegistrationScreen extends ConsumerStatefulWidget {
  const RegistrationScreen({super.key});

  @override
  ConsumerState<RegistrationScreen> createState() => _RegistrationScreenState();
}

class _RegistrationScreenState extends ConsumerState<RegistrationScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  List<dynamic> _offerings = [];
  Map<String, dynamic>? _cart;
  Map<String, dynamic>? _validation;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    await Future.wait([
      _loadOfferings(),
      _loadCart(),
    ]);
    setState(() => _isLoading = false);
  }

  Future<void> _loadOfferings() async {
    try {
      final apiService = ref.read(apiServiceProvider);
      final response = await apiService.get(ApiConstants.offerings);
      if (response.statusCode == 200) {
        setState(() => _offerings = response.data);
      }
    } catch (_) {}
  }

  Future<void> _loadCart() async {
    try {
      final apiService = ref.read(apiServiceProvider);
      final response = await apiService.get(ApiConstants.cart);
      if (response.statusCode == 200) {
        setState(() => _cart = response.data);
      }
    } catch (_) {}
  }

  Future<void> _addToCart(String unitId) async {
    try {
      final apiService = ref.read(apiServiceProvider);
      await apiService.post(
        ApiConstants.cartAdd,
        data: {'teaching_unit_id': unitId},
      );
      await _loadCart();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Course added to cart'),
            backgroundColor: AppColors.success,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Failed to add course'),
            backgroundColor: AppColors.error,
          ),
        );
      }
    }
  }

  Future<void> _validateCart() async {
    try {
      final apiService = ref.read(apiServiceProvider);
      final response = await apiService.post(ApiConstants.cartValidate);
      if (response.statusCode == 200) {
        setState(() => _validation = response.data);
      }
    } catch (_) {}
  }

  Future<void> _submitCart() async {
    try {
      final apiService = ref.read(apiServiceProvider);
      final response = await apiService.post(ApiConstants.cartSubmit);
      if (response.statusCode == 200) {
        await _loadCart();
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Registration submitted for approval!'),
              backgroundColor: AppColors.success,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Submission failed. Check validation errors.'),
            backgroundColor: AppColors.error,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Course Registration'),
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          tabs: const [
            Tab(text: 'Available Courses', icon: Icon(Icons.search)),
            Tab(text: 'My Cart', icon: Icon(Icons.shopping_cart)),
            Tab(text: 'Validation', icon: Icon(Icons.check_circle)),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          // Tab 1: Available Courses
          _buildOfferingsTab(),
          // Tab 2: Cart
          _buildCartTab(),
          // Tab 3: Validation
          _buildValidationTab(),
        ],
      ),
    );
  }

  Widget _buildOfferingsTab() {
    if (_offerings.isEmpty) {
      return const Center(child: Text('No courses available for registration'));
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _offerings.length,
      itemBuilder: (context, index) {
        final offering = _offerings[index];
        final availableSeats = offering['available_seats'] as int;
        final isFull = availableSeats <= 0;

        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: isFull ? AppColors.error : AppColors.primary,
              child: Text(
                '${offering['credit_hours']}',
                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
              ),
            ),
            title: Text(
              '${offering['course_code']} - ${offering['course_name']}',
              style: const TextStyle(fontWeight: FontWeight.w600),
            ),
            subtitle: Text(
              '$availableSeats seats available • ${offering['credit_hours']} credit hours',
            ),
            trailing: isFull
                ? const Chip(
                    label: Text('FULL', style: TextStyle(color: Colors.white)),
                    backgroundColor: AppColors.error,
                  )
                : ElevatedButton.icon(
                    onPressed: () => _addToCart(offering['teaching_unit_id'] ?? offering['id']),
                    icon: const Icon(Icons.add, size: 18),
                    label: const Text('Add'),
                  ),
          ),
        );
      },
    );
  }

  Widget _buildCartTab() {
    final items = (_cart?['items'] as List?) ?? [];
    final totalHours = _cart?['total_hours'] ?? 0;
    final status = _cart?['status'] ?? 'draft';

    return Column(
      children: [
        // Cart summary bar
        Container(
          padding: const EdgeInsets.all(16),
          color: AppColors.primary.withOpacity(0.05),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Total: $totalHours credit hours',
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
              Text(
                'Status: ${status.toString().toUpperCase()}',
                style: TextStyle(
                  color: status == 'draft' ? AppColors.info : AppColors.success,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
        
        // Cart items
        Expanded(
          child: items.isEmpty
              ? const Center(child: Text('Your cart is empty. Add courses from the Available tab.'))
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: items.length,
                  itemBuilder: (context, index) {
                    final item = items[index];
                    return Card(
                      child: ListTile(
                        title: Text('${item['course_code']} - ${item['course_name']}'),
                        subtitle: Text('${item['credit_hours']} hrs • ${item['unit_type']} group ${item['group_number']}'),
                        trailing: IconButton(
                          icon: const Icon(Icons.remove_circle, color: AppColors.error),
                          onPressed: () {},
                        ),
                      ),
                    );
                  },
                ),
        ),

        // Action buttons
        if (status == 'draft' && items.isNotEmpty)
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _validateCart,
                    icon: const Icon(Icons.check_circle_outline),
                    label: const Text('Validate'),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _submitCart,
                    icon: const Icon(Icons.send),
                    label: const Text('Submit for Approval'),
                  ),
                ),
              ],
            ),
          ),
      ],
    );
  }

  Widget _buildValidationTab() {
    if (_validation == null) {
      return const Center(
        child: Text('Click "Validate" in the Cart tab to check your registration.'),
      );
    }

    final isValid = _validation!['is_valid'] as bool;
    final errors = (_validation!['errors'] as List?) ?? [];
    final totalHours = _validation!['total_hours'];
    final maxHours = _validation!['max_allowed_hours'];

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Status banner
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: isValid ? AppColors.success.withOpacity(0.1) : AppColors.error.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              children: [
                Icon(
                  isValid ? Icons.check_circle : Icons.error,
                  color: isValid ? AppColors.success : AppColors.error,
                  size: 32,
                ),
                const SizedBox(width: 12),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      isValid ? 'Registration Valid ✓' : 'Validation Failed',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: isValid ? AppColors.success : AppColors.error,
                      ),
                    ),
                    Text('$totalHours / $maxHours credit hours'),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // Errors list
          if (errors.isNotEmpty) ...[
            Text(
              'Issues Found (${errors.length}):',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 12),
            ...errors.map((error) => Card(
              color: AppColors.error.withOpacity(0.05),
              margin: const EdgeInsets.only(bottom: 8),
              child: ListTile(
                leading: _getErrorIcon(error['error_type']),
                title: Text(error['message']),
                subtitle: error['course_code'] != null
                    ? Text('Course: ${error['course_code']}')
                    : null,
              ),
            )),
          ],
        ],
      ),
    );
  }

  Widget _getErrorIcon(String errorType) {
    switch (errorType) {
      case 'prerequisite':
        return const Icon(Icons.link_off, color: AppColors.error);
      case 'conflict':
        return const Icon(Icons.schedule, color: AppColors.warning);
      case 'capacity':
        return const Icon(Icons.people, color: AppColors.error);
      case 'credit_limit':
        return const Icon(Icons.block, color: AppColors.error);
      default:
        return const Icon(Icons.error, color: AppColors.error);
    }
  }
}
