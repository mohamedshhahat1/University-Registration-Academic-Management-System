import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/services/api_service.dart';
import '../../../core/constants/api_constants.dart';

/// Finance screen displaying invoices and payment history.
class FinanceScreen extends ConsumerStatefulWidget {
  const FinanceScreen({super.key});

  @override
  ConsumerState<FinanceScreen> createState() => _FinanceScreenState();
}

class _FinanceScreenState extends ConsumerState<FinanceScreen> {
  List<dynamic> _invoices = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadInvoices();
  }

  Future<void> _loadInvoices() async {
    try {
      final apiService = ref.read(apiServiceProvider);
      final response = await apiService.get(ApiConstants.myInvoices);
      if (response.statusCode == 200) {
        setState(() {
          _invoices = response.data;
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'paid': return AppColors.success;
      case 'partial': return AppColors.warning;
      case 'pending': return AppColors.error;
      case 'cancelled': return AppColors.textSecondary;
      default: return AppColors.info;
    }
  }

  IconData _getStatusIcon(String status) {
    switch (status) {
      case 'paid': return Icons.check_circle;
      case 'partial': return Icons.timelapse;
      case 'pending': return Icons.pending;
      case 'cancelled': return Icons.cancel;
      default: return Icons.receipt;
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Finance & Payments'),
      ),
      body: _invoices.isEmpty
          ? const Center(child: Text('No invoices found'))
          : ListView.builder(
              padding: const EdgeInsets.all(24),
              itemCount: _invoices.length,
              itemBuilder: (context, index) {
                final invoice = _invoices[index];
                final status = invoice['status'] ?? 'draft';

                return Card(
                  margin: const EdgeInsets.only(bottom: 16),
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Header
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Row(
                              children: [
                                Icon(
                                  _getStatusIcon(status),
                                  color: _getStatusColor(status),
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  'Invoice #${invoice['id'].toString().substring(0, 8)}',
                                  style: Theme.of(context).textTheme.titleLarge,
                                ),
                              ],
                            ),
                            Chip(
                              label: Text(
                                status.toUpperCase(),
                                style: TextStyle(
                                  color: _getStatusColor(status),
                                  fontWeight: FontWeight.bold,
                                  fontSize: 12,
                                ),
                              ),
                              backgroundColor: _getStatusColor(status).withOpacity(0.1),
                            ),
                          ],
                        ),
                        const Divider(height: 24),

                        // Breakdown
                        _buildRow('Credit Hours Cost', '${invoice['credit_hours_cost']} EGP'),
                        _buildRow('Fixed Fees', '${invoice['fixed_fees']} EGP'),
                        if ((invoice['scholarship_discount'] as num) > 0)
                          _buildRow(
                            'Scholarship Discount',
                            '-${invoice['scholarship_discount']} EGP',
                            color: AppColors.success,
                          ),
                        const Divider(height: 16),
                        _buildRow(
                          'Total Amount',
                          '${invoice['total_amount']} EGP',
                          isBold: true,
                        ),
                        _buildRow('Paid', '${invoice['paid_amount']} EGP'),
                        _buildRow(
                          'Remaining',
                          '${invoice['remaining_amount']} EGP',
                          color: (invoice['remaining_amount'] as num) > 0
                              ? AppColors.error
                              : AppColors.success,
                          isBold: true,
                        ),

                        // Pay button for unpaid invoices
                        if (status == 'pending' || status == 'partial') ...[
                          const SizedBox(height: 16),
                          SizedBox(
                            width: double.infinity,
                            child: ElevatedButton.icon(
                              onPressed: () {},
                              icon: const Icon(Icons.payment),
                              label: const Text('Make Payment'),
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

  Widget _buildRow(String label, String value, {Color? color, bool isBold = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: Theme.of(context).textTheme.bodyMedium),
          Text(
            value,
            style: TextStyle(
              color: color ?? AppColors.textPrimary,
              fontWeight: isBold ? FontWeight.bold : FontWeight.normal,
              fontSize: isBold ? 16 : 14,
            ),
          ),
        ],
      ),
    );
  }
}
