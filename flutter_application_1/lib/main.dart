import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  runApp(const MathSolverApp());
}

class MathSolverApp extends StatelessWidget {
  const MathSolverApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Advanced Math Problem Solver',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        fontFamily: 'Roboto',
        scaffoldBackgroundColor: Colors.white,
        inputDecorationTheme: InputDecorationTheme(
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(6),
            borderSide: BorderSide(color: Colors.grey.shade300),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(6),
            borderSide: const BorderSide(color: Colors.blue, width: 2),
          ),
        ),
      ),
      home: const MathSolverHome(),
    );
  }
}

class MathSolverHome extends StatefulWidget {
  const MathSolverHome({Key? key}) : super(key: key);

  @override
  _MathSolverHomeState createState() => _MathSolverHomeState();
}

class _MathSolverHomeState extends State<MathSolverHome> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final TextEditingController _expressionController = TextEditingController();
  String _selectedProblemType = 'linear';
  String _selectedSubType = '';
  List<Map<String, dynamic>> _solutionHistory = [];
  bool _isLoading = false;
  Map<String, dynamic>? _currentSolution;
  
  final Map<String, String> _examples = {
    'linear': '2*x + 3 = 7',
    'quadratic': 'x**2 + 5*x + 6 = 0',
    'system': 'x + y = 10; 2*x - y = 5',
    'inequality': 'x**2 - 4 < 0',
    'polynomial': 'x**3 - 6*x**2 + 11*x - 6 = 0',
    'differentiation': 'x**2 + 3*x + 2',
    'integration': '2*x + 3',
    'trigonometry': 'sin(x) = 0.5',
    'limit': 'limit(x, 0, (sin(x)/x))',
    'statistics': 'data = [10, 20, 30, 40, 50]',
  };

  final Map<String, Map<String, String>> _geometryExamples = {
    'circle_area': {'example': 'radius = 5'},
    'circle_circumference': {'example': 'radius = 5'},
    'triangle_area': {'example': 'base = 5; height = 8'},
    'rectangle_area': {'example': 'length = 5; width = 10'},
    'sphere_volume': {'example': 'radius = 3'},
  };

  final Map<String, Map<String, String>> _statisticsExamples = {
    'mean': {'example': 'data = [10, 20, 30, 40, 50]'},
    'median': {'example': 'data = [10, 20, 30, 40, 50]'},
    'mode': {'example': 'data = [10, 20, 20, 30, 40, 50]'},
    'standard_deviation': {'example': 'data = [10, 20, 30, 40, 50]'},
    'variance': {'example': 'data = [10, 20, 30, 40, 50]'},
    'range': {'example': 'data = [10, 20, 30, 40, 50]'},
  };

  String _currentExample = '2*x + 3 = 7';
  bool _showSubOptions = false;
  List<DropdownMenuItem<String>> _subTypeOptions = [];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _tabController.addListener(_handleTabChange);
    _loadHistory();
  }

  @override
  void dispose() {
    _tabController.removeListener(_handleTabChange);
    _tabController.dispose();
    _expressionController.dispose();
    super.dispose();
  }

  void _handleTabChange() {
    if (_tabController.index == 1) {
      _loadHistory();
    }
  }

  Future<void> _loadHistory() async {
    final prefs = await SharedPreferences.getInstance();
    final historyJson = prefs.getString('mathSolverHistory');
    
    if (historyJson != null) {
      setState(() {
        _solutionHistory = List<Map<String, dynamic>>.from(
          jsonDecode(historyJson).map((item) => Map<String, dynamic>.from(item))
        );
      });
    }
  }

  Future<void> _saveHistory() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('mathSolverHistory', jsonEncode(_solutionHistory));
  }

  void _updateExampleAndOptions() {
    setState(() {
      _showSubOptions = false;
      _subTypeOptions = [];

      if (_selectedProblemType == 'geometry') {
        _showSubOptions = true;
        _selectedSubType = 'circle_area';
        _subTypeOptions = _geometryExamples.entries
            .map((e) => DropdownMenuItem<String>(
                  value: e.key,
                  child: Text(e.key.split('_').map((word) => 
                      word[0].toUpperCase() + word.substring(1)).join(' ')),
                ))
            .toList();
        _currentExample = _geometryExamples[_selectedSubType]!['example']!;
      } else if (_selectedProblemType == 'statistics') {
        _showSubOptions = true;
        _selectedSubType = 'mean';
        _subTypeOptions = _statisticsExamples.entries
            .map((e) => DropdownMenuItem<String>(
                  value: e.key,
                  child: Text(e.key.split('_').map((word) => 
                      word[0].toUpperCase() + word.substring(1)).join(' ')),
                ))
            .toList();
        _currentExample = _statisticsExamples[_selectedSubType]!['example']!;
      } else {
        _currentExample = _examples[_selectedProblemType]!;
      }
    });
  }

  void _updateExample() {
    setState(() {
      if (_selectedProblemType == 'geometry') {
        _currentExample = _geometryExamples[_selectedSubType]!['example']!;
      } else if (_selectedProblemType == 'statistics') {
        _currentExample = _statisticsExamples[_selectedSubType]!['example']!;
      } else {
        _currentExample = _examples[_selectedProblemType]!;
      }
    });
  }

  Future<void> _solveProblem() async {
    if (_expressionController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a valid expression')),
      );
      return;
    }

    setState(() {
      _isLoading = true;
      _currentSolution = null;
    });


try {
  final response = await http.post(
    Uri.parse('https://maths-backend-1.onrender.com/solve'),  // Use 10.0.2.2 for Android emulator, or your local IP for a real device
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'type': _selectedProblemType,
      'expression': _expressionController.text.trim(),
      'subType': _selectedSubType,  // Only required for geometry/statistics
    }),
  );

  if (response.statusCode == 200) {
    final responseData = jsonDecode(response.body);
    
    setState(() {
      _isLoading = false;
      _currentSolution = responseData;

      // Store history
      final historyItem = {
        'type': _selectedProblemType,
        'subType': _selectedSubType,
        'expression': _expressionController.text.trim(),
        'solution': responseData['solution'],
        'steps': responseData['steps'],
        'timestamp': DateTime.now().toIso8601String(),
      };

      _solutionHistory.insert(0, historyItem);
      if (_solutionHistory.length > 10) {
        _solutionHistory.removeLast();
      }

      _saveHistory();
    });
  } else {
    throw Exception('Failed to solve problem: ${response.statusCode}');
  }
} catch (e) {
  setState(() {
    _isLoading = false;
  });

  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(content: Text('Error: ${e.toString()}')),
  );
}

  }

  void _loadHistoryItem(int index) {
    final item = _solutionHistory[index];
    
    setState(() {
      _selectedProblemType = item['type'];
      _updateExampleAndOptions();
      
      if (item['subType'] != null && item['subType'].isNotEmpty) {
        _selectedSubType = item['subType'];
      }
      
      _expressionController.text = item['expression'];
      _currentSolution = {
        'steps': item['steps'],
        'solution': item['solution'],
      };
      
      _tabController.animateTo(0);
    });
  }

  Future<void> _clearHistory() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Clear History'),
        content: const Text('Are you sure you want to clear your solution history?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Clear'),
          ),
        ],
      ),
    );
    
    if (confirmed == true) {
      setState(() {
        _solutionHistory = [];
      });
      
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('mathSolverHistory');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFF74ebd5), Color(0xFF9face6)],
          ),
        ),
        child: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              child: Padding(
                padding: const EdgeInsets.all(20.0),
                child: Card(
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  elevation: 8,
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: SizedBox(
                      width: 800,
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          const Text(
                            'Advanced Math Problem Solver',
                            style: TextStyle(
                              fontSize: 28,
                              fontWeight: FontWeight.bold,
                              color: Colors.blue,
                            ),
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(height: 24),
                          TabBar(
                            controller: _tabController,
                            labelColor: Colors.white,
                            unselectedLabelColor: Colors.blue,
                            indicator: BoxDecoration(
                              borderRadius: BorderRadius.circular(5),
                              color: Colors.blue,
                            ),
                            tabs: const [
                              Tab(text: 'Problem Solver'),
                              Tab(text: 'Solution History'),
                              Tab(text: 'About'),
                            ],
                          ),
                          const SizedBox(height: 20),
                          SizedBox(
                            height: 600, // Fixed height for tab content
                            child: TabBarView(
                              controller: _tabController,
                              children: [
                                // Problem Solver Tab
                                SingleChildScrollView(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      const Text(
                                        'Select Problem Type:',
                                        style: TextStyle(
                                          fontWeight: FontWeight.bold,
                                          fontSize: 16,
                                        ),
                                      ),
                                      const SizedBox(height: 8),
                                      DropdownButtonFormField<String>(
                                        decoration: const InputDecoration(
                                          border: OutlineInputBorder(),
                                        ),
                                        value: _selectedProblemType,
                                        items: const [
                                          DropdownMenuItem(value: 'linear', child: Text('Linear Equation')),
                                          DropdownMenuItem(value: 'quadratic', child: Text('Quadratic Equation')),
                                          DropdownMenuItem(value: 'system', child: Text('System of Equations')),
                                          DropdownMenuItem(value: 'inequality', child: Text('Inequality')),
                                          DropdownMenuItem(value: 'polynomial', child: Text('Polynomial Equation')),
                                          DropdownMenuItem(value: 'geometry', child: Text('Geometry')),
                                          DropdownMenuItem(value: 'differentiation', child: Text('Differentiation')),
                                          DropdownMenuItem(value: 'integration', child: Text('Integration')),
                                          DropdownMenuItem(value: 'trigonometry', child: Text('Trigonometric Equations')),
                                          DropdownMenuItem(value: 'limit', child: Text('Limits')),
                                          DropdownMenuItem(value: 'statistics', child: Text('Statistics')),
                                        ],
                                        onChanged: (value) {
                                          setState(() {
                                            _selectedProblemType = value!;
                                            _updateExampleAndOptions();
                                          });
                                        },
                                      ),
                                      if (_showSubOptions) ...[
                                        const SizedBox(height: 16),
                                        const Text(
                                          'Specific Type:',
                                          style: TextStyle(
                                            fontWeight: FontWeight.bold,
                                            fontSize: 16,
                                          ),
                                        ),
                                        const SizedBox(height: 8),
                                        DropdownButtonFormField<String>(
                                          decoration: const InputDecoration(
                                            border: OutlineInputBorder(),
                                          ),
                                          value: _selectedSubType,
                                          items: _subTypeOptions,
                                          onChanged: (value) {
                                            setState(() {
                                              _selectedSubType = value!;
                                              _updateExample();
                                            });
                                          },
                                        ),
                                      ],
                                      const SizedBox(height: 16),
                                      Container(
                                        padding: const EdgeInsets.all(16),
                                        decoration: BoxDecoration(
                                          color: Colors.blue.shade50,
                                          borderRadius: BorderRadius.circular(6),
                                          border: Border.all(color: Colors.blue.shade200),
                                        ),
                                        child: Column(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            const Text(
                                              'Example:',
                                              style: TextStyle(
                                                fontWeight: FontWeight.bold,
                                                color: Colors.blue,
                                                fontSize: 16,
                                              ),
                                            ),
                                            const SizedBox(height: 8),
                                            Text(_currentExample),
                                          ],
                                        ),
                                      ),
                                      const SizedBox(height: 16),
                                      const Text(
                                        'Enter Expression:',
                                        style: TextStyle(
                                          fontWeight: FontWeight.bold,
                                          fontSize: 16,
                                        ),
                                      ),
                                      const SizedBox(height: 8),
                                      TextField(
                                        controller: _expressionController,
                                        decoration: const InputDecoration(
                                          hintText: 'Enter your mathematical expression here...',
                                          border: OutlineInputBorder(),
                                        ),
                                        minLines: 4,
                                        maxLines: 4,
                                      ),
                                      const SizedBox(height: 16),
                                      SizedBox(
                                        width: double.infinity,
                                        height: 50,
                                        child: ElevatedButton(
                                          onPressed: _solveProblem,
                                          style: ElevatedButton.styleFrom(
                                            foregroundColor: Colors.white,
                                            backgroundColor: Colors.blue,
                                            textStyle: const TextStyle(
                                              fontWeight: FontWeight.bold,
                                              fontSize: 16,
                                            ),
                                          ),
                                          child: const Text('Solve'),
                                        ),
                                      ),
                                      const SizedBox(height: 20),
                                      if (_isLoading)
                                        const Center(child: CircularProgressIndicator()),
                                      if (_currentSolution != null) ...[
                                        Container(
                                          padding: const EdgeInsets.all(16),
                                          decoration: BoxDecoration(
                                            color: Colors.grey.shade100,
                                            borderRadius: BorderRadius.circular(6),
                                            border: Border.all(color: Colors.grey.shade300),
                                          ),
                                          child: Column(
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            children: [
                                              const Text(
                                                'Solution Steps:',
                                                style: TextStyle(
                                                  fontWeight: FontWeight.bold,
                                                  fontSize: 18,
                                                ),
                                              ),
                                              const SizedBox(height: 12),
                                              ..._currentSolution!['steps'].asMap().entries.map((entry) {
                                                final index = entry.key;
                                                final step = entry.value;
                                                return Container(
                                                  margin: const EdgeInsets.only(bottom: 8),
                                                  padding: const EdgeInsets.all(12),
                                                  decoration: BoxDecoration(
                                                    color: Colors.blue.shade50,
                                                    borderRadius: BorderRadius.circular(6),
                                                    border: Border.all(color: Colors.blue.shade200),
                                                  ),
                                                  child: RichText(
                                                    text: TextSpan(
                                                      style: const TextStyle(color: Colors.blue, fontSize: 16),
                                                      children: [
                                                        TextSpan(
                                                          text: 'Step ${index + 1}: ',
                                                          style: const TextStyle(fontWeight: FontWeight.bold),
                                                        ),
                                                        TextSpan(
                                                          text: step,
                                                          style: const TextStyle(color: Colors.black87),
                                                        ),
                                                      ],
                                                    ),
                                                  ),
                                                );
                                              }).toList(),
                                              const SizedBox(height: 16),
                                              Container(
                                                width: double.infinity,
                                                padding: const EdgeInsets.all(16),
                                                decoration: BoxDecoration(
                                                  color: Colors.green.shade50,
                                                  borderRadius: BorderRadius.circular(6),
                                                  border: Border.all(color: Colors.green.shade200),
                                                ),
                                                child: Text(
                                                  'Solution: ${_currentSolution!['solution']}',
                                                  style: TextStyle(
                                                    fontSize: 18,
                                                    fontWeight: FontWeight.bold,
                                                    color: Colors.green.shade800,
                                                  ),
                                                  textAlign: TextAlign.center,
                                                ),
                                              ),
                                            ],
                                          ),
                                        ),
                                      ],
                                    ],
                                  ),
                                ),
                                
                                // History Tab
                                Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    const Text(
                                      'Solution History',
                                      style: TextStyle(
                                        fontSize: 24,
                                        fontWeight: FontWeight.bold,
                                        color: Colors.blue,
                                      ),
                                    ),
                                    const SizedBox(height: 8),
                                    const Text(
                                      'Click on a previous problem to view its solution again.',
                                      style: TextStyle(fontSize: 16),
                                    ),
                                    const SizedBox(height: 16),
                                    Expanded(
                                      child: _solutionHistory.isEmpty
                                          ? const Center(
                                              child: Text(
                                                'No history yet. Solve some problems to see them here.',
                                                style: TextStyle(
                                                  fontSize: 16,
                                                  color: Colors.grey,
                                                ),
                                              ),
                                            )
                                          : ListView.builder(
                                              itemCount: _solutionHistory.length,
                                              itemBuilder: (context, index) {
                                                final item = _solutionHistory[index];
                                                final date = DateTime.parse(item['timestamp']);
                                                
                                                return Card(
                                                  margin: const EdgeInsets.only(bottom: 8),
                                                  child: InkWell(
                                                    onTap: () => _loadHistoryItem(index),
                                                    child: Padding(
                                                      padding: const EdgeInsets.all(16),
                                                      child: Column(
                                                        crossAxisAlignment: CrossAxisAlignment.start,
                                                        children: [
                                                          Text(
                                                            '${item['type'].toString().capitalize()}${item['subType'] != null && item['subType'].isNotEmpty ? ': ${item['subType'].toString().capitalize()}' : ''}',
                                                            style: const TextStyle(
                                                              fontWeight: FontWeight.bold,
                                                              fontSize: 16,
                                                            ),
                                                          ),
                                                          const SizedBox(height: 4),
                                                          Text(
                                                            item['expression'],
                                                            style: const TextStyle(fontSize: 14),
                                                          ),
                                                          const SizedBox(height: 4),
                                                          Text(
                                                            '${date.day}/${date.month}/${date.year} ${date.hour}:${date.minute.toString().padLeft(2, '0')}',
                                                            style: TextStyle(
                                                              fontSize: 12,
                                                              color: Colors.grey.shade600,
                                                            ),
                                                          ),
                                                        ],
                                                      ),
                                                    ),
                                                  ),
                                                );
                                              },
                                            ),
                                    ),
                                    const SizedBox(height: 16),
                                    SizedBox(
                                      width: double.infinity,
                                      child: ElevatedButton(
                                        onPressed: _clearHistory,
                                        style: ElevatedButton.styleFrom(
                                          foregroundColor: Colors.white,
                                          backgroundColor: Colors.red,
                                        ),
                                        child: const Text('Clear History'),
                                      ),
                                    ),
                                  ],
                                ),
                                
                                // About Tab
                                SingleChildScrollView(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      const Text(
                                        'About This Math Solver',
                                        style: TextStyle(
                                          fontSize: 24,
                                          fontWeight: FontWeight.bold,
                                          color: Colors.blue,
                                        ),
                                      ),
                                      const SizedBox(height: 16),
                                      const Text(
                                        'This advanced mathematics problem solver is designed to help students and professionals solve a wide variety of mathematical problems. The solver provides step-by-step solutions to enhance understanding of the solution process.',
                                        style: TextStyle(fontSize: 16),
                                      ),
                                      const SizedBox(height: 24),
                                      const Text(
                                        'Features:',
                                        style: TextStyle(
                                          fontSize: 20,
                                          fontWeight: FontWeight.bold,
                                          color: Colors.blue,
                                        ),
                                      ),
                                      const SizedBox(height: 8),
                                      _buildBulletPoint('Solves various types of mathematical problems'),
                                      _buildBulletPoint('Shows detailed solution steps'),
                                      _buildBulletPoint('Provides visual representations where applicable'),
                                      _buildBulletPoint('Saves solution history for future reference'),
                                      const SizedBox(height: 24),
                                      const Text(
                                        'Supported Problem Types:',
                                        style: TextStyle(
                                          fontSize: 20,
                                          fontWeight: FontWeight.bold,
                                          color: Colors.blue,
                                        ),
                                      ),
                                      const SizedBox(height: 8),
                                      _buildBulletPoint('Algebraic equations (linear, quadratic, polynomial, systems)'),
                                      _buildBulletPoint('Calculus (differentiation, integration, limits)'),
                                      _buildBulletPoint('Geometry (area, volume, perimeter calculations)'),
                                      _buildBulletPoint('Trigonometry'),
                                      _buildBulletPoint('Statistics (mean, median, standard deviation, etc.)'),
                                      const SizedBox(height: 24),
                                      const Text(
                                        'This tool uses advanced mathematical libraries to perform calculations and provide accurate solutions.',
                                        style: TextStyle(fontSize: 16),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildBulletPoint(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('• ', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          Expanded(
            child: Text(text, style: const TextStyle(fontSize: 16)),
          ),
        ],
      ),
    );
  }
}

// Extension to capitalize strings
extension StringExtension on String {
  String capitalize() {
    return split('_').map((word) => 
      word.isNotEmpty ? word[0].toUpperCase() + word.substring(1) : ''
    ).join(' ');
  }
}