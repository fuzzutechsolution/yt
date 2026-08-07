// ==========================================================================
// FUZZUTECH PREMIUM FLUTTER TO-DO LIST APPLICATION
// ==========================================================================
// Author: FuzzuTech Educational Material (YouTube Course)
// Version: 1.0.0
// Description: A recruitment-level, ultra-premium Material 3 To-Do List application.
// Architecture: Single-file Clean Architecture (Application, Theme, Constants,
//               Utilities, Models, Storage, Widgets, Dialogs, Home Controller).
// Design Inspiration: Google Tasks, Microsoft To Do, Notion, Windows 11.
// Layout: Dynamically adaptive (Mobile, Tablet, Desktop, Web, Landscape, Portrait).
// State Management: Vanilla Flutter (StatefulController pattern) with zero dependencies.
// Persistence: SharedPreferences with JSON serialization.
// Animations: 60 FPS implicit, explicit, list transitions, and spring-back checkbox.
// ==========================================================================

import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  // Ensure Flutter engine bindings are initialized prior to loading storage
  WidgetsFlutterBinding.ensureInitialized();
  
  // Set preferred orientation to support all but run nicely
  SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
    DeviceOrientation.landscapeLeft,
    DeviceOrientation.landscapeRight,
  ]);
  
  runApp(const PremiumTodoApp());
}

// ==========================================================================
// 1. APPLICATION ENTRYPOINT & MULTI-THEME SUPPORT
// ==========================================================================

class PremiumTodoApp extends StatefulWidget {
  const PremiumTodoApp({super.key});

  @override
  State<PremiumTodoApp> createState() => _PremiumTodoAppState();
}

class _PremiumTodoAppState extends State<PremiumTodoApp> {
  // Simple value notifier for real-time theme mode changes
  late ValueNotifier<ThemeMode> _themeNotifier;

  @override
  void initState() {
    super.initState();
    _themeNotifier = ValueNotifier<ThemeMode>(ThemeMode.system);
    _loadThemePreference();
  }

  Future<void> _loadThemePreference() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final themeStr = prefs.getString(AppConstants.themeKey);
      if (themeStr != null) {
        _themeNotifier.value = ThemeMode.values.firstWhere(
          (e) => e.name == themeStr,
          orElse: () => ThemeMode.system,
        );
      }
    } catch (e) {
      debugPrint('Error loading theme: $e');
    }
  }

  Future<void> _toggleTheme(ThemeMode mode) async {
    _themeNotifier.value = mode;
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(AppConstants.themeKey, mode.name);
    } catch (e) {
      debugPrint('Error saving theme: $e');
    }
  }

  @override
  void dispose() {
    _themeNotifier.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<ThemeMode>(
      valueListenable: _themeNotifier,
      builder: (context, themeMode, _) {
        return MaterialApp(
          title: 'Fuzzu Tasks',
          debugShowCheckedModeBanner: false,
          themeMode: themeMode,
          
          // PREMIUM LIGHT THEME (Indigo/Amethyst base)
          theme: ThemeData(
            useMaterial3: true,
            brightness: Brightness.light,
            colorScheme: ColorScheme.fromSeed(
              seedColor: AppColors.primarySeed,
              brightness: Brightness.light,
            ).copyWith(
              surface: const Color(0xFFF7F9FC),
              surfaceContainer: Colors.white,
              surfaceContainerHigh: const Color(0xFFECEFF5),
            ),
            scaffoldBackgroundColor: const Color(0xFFF7F9FC),
            cardTheme: CardThemeData(
              elevation: 0,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(AppConstants.radiusMedium),
                side: const BorderSide(color: Color(0xFFE2E8F0), width: 1),
              ),
              color: Colors.white,
            ),
            appBarTheme: const AppBarTheme(
              backgroundColor: Colors.transparent,
              elevation: 0,
              centerTitle: false,
            ),
            dialogTheme: DialogThemeData(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(AppConstants.radiusLarge),
              ),
              elevation: 4,
            ),
          ),

          // PREMIUM DARK THEME (Sleek Obsidian/Space Grey base)
          darkTheme: ThemeData(
            useMaterial3: true,
            brightness: Brightness.dark,
            colorScheme: ColorScheme.fromSeed(
              seedColor: AppColors.primarySeed,
              brightness: Brightness.dark,
            ).copyWith(
              surface: const Color(0xFF0C0E14),
              surfaceContainer: const Color(0xFF161920),
              surfaceContainerHigh: const Color(0xFF222632),
            ),
            scaffoldBackgroundColor: const Color(0xFF0C0E14),
            cardTheme: CardThemeData(
              elevation: 0,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(AppConstants.radiusMedium),
                side: const BorderSide(color: Color(0xFF222632), width: 1),
              ),
              color: const Color(0xFF161920),
            ),
            appBarTheme: const AppBarTheme(
              backgroundColor: Colors.transparent,
              elevation: 0,
              centerTitle: false,
            ),
            dialogTheme: DialogThemeData(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(AppConstants.radiusLarge),
              ),
              backgroundColor: const Color(0xFF161920),
              elevation: 8,
            ),
          ),
          
          home: TodoAppHome(
            themeMode: themeMode,
            onThemeChanged: _toggleTheme,
          ),
        );
      },
    );
  }
}

// ==========================================================================
// 2. THEME & APP CONSTANTS
// ==========================================================================

class AppColors {
  static const Color primarySeed = Color(0xFF5E5CE6); // Indigo base
  static const Color success = Color(0xFF34C759); // Apple Green
  static const Color warning = Color(0xFFFF9500); // Orange
  static const Color error = Color(0xFFFF3B30); // Red
  static const Color info = Color(0xFF007AFF); // Blue
}

class AppConstants {
  static const double radiusSmall = 8.0;
  static const double radiusMedium = 16.0;
  static const double radiusLarge = 24.0;
  static const double radiusMax = 32.0;

  static const double paddingSmall = 8.0;
  static const double paddingMedium = 16.0;
  static const double paddingLarge = 24.0;
  
  static const String storageKey = 'fuzzu_tasks_data';
  static const String themeKey = 'fuzzu_theme_preference';
}

// ==========================================================================
// 3. ENUMS
// ==========================================================================

enum TaskPriority {
  low('Low', AppColors.success, Icons.arrow_downward_rounded),
  medium('Medium', AppColors.warning, Icons.density_medium_rounded),
  high('High', AppColors.error, Icons.arrow_upward_rounded);

  final String label;
  final Color color;
  final IconData icon;
  const TaskPriority(this.label, this.color, this.icon);
}

enum TaskCategory {
  personal('Personal', Icons.person_rounded, Color(0xFF007AFF)),
  work('Work', Icons.work_rounded, Color(0xFF8E8E93)),
  study('Study', Icons.school_rounded, Color(0xFFBF5AF2)),
  shopping('Shopping', Icons.shopping_bag_rounded, Color(0xFFFFCC00)),
  others('Others', Icons.bookmark_rounded, Color(0xFF32D7C2));

  final String label;
  final IconData icon;
  final Color color;
  const TaskCategory(this.label, this.icon, this.color);
}

enum TaskSortOption {
  alphabetically('Alphabetically'),
  newest('Newest First'),
  oldest('Oldest First'),
  completedFirst('Completed First'),
  pendingFirst('Pending First'),
  priorityHighFirst('High Priority First');

  final String label;
  const TaskSortOption(this.label);
}

enum TaskFilterOption {
  all('All Tasks'),
  pending('Pending'),
  completed('Completed'),
  highPriority('High Priority');

  final String label;
  const TaskFilterOption(this.label);
}

// ==========================================================================
// 4. TASK DATA MODEL
// ==========================================================================

class Task {
  final String id;
  final String title;
  final String description;
  final String notes;
  final bool isCompleted;
  final TaskPriority priority;
  final TaskCategory category;
  final DateTime createdAt;
  final DateTime updatedAt;
  final DateTime? completedAt;

  const Task({
    required this.id,
    required this.title,
    required this.description,
    required this.notes,
    required this.isCompleted,
    required this.priority,
    required this.category,
    required this.createdAt,
    required this.updatedAt,
    this.completedAt,
  });

  // Create a copy of the Task object with modified fields
  Task copyWith({
    String? title,
    String? description,
    String? notes,
    bool? isCompleted,
    TaskPriority? priority,
    TaskCategory? category,
    DateTime? updatedAt,
    DateTime? completedAt,
  }) {
    return Task(
      id: id,
      title: title ?? this.title,
      description: description ?? this.description,
      notes: notes ?? this.notes,
      isCompleted: isCompleted ?? this.isCompleted,
      priority: priority ?? this.priority,
      category: category ?? this.category,
      createdAt: createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      completedAt: isCompleted == false ? null : (completedAt ?? this.completedAt),
    );
  }

  // JSON Serialization logic
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'notes': notes,
      'isCompleted': isCompleted,
      'priority': priority.name,
      'category': category.name,
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt.toIso8601String(),
      'completedAt': completedAt?.toIso8601String(),
    };
  }

  // JSON Deserialization logic
  factory Task.fromJson(Map<String, dynamic> json) {
    return Task(
      id: json['id'] as String,
      title: json['title'] as String,
      description: json['description'] as String? ?? '',
      notes: json['notes'] as String? ?? '',
      isCompleted: json['isCompleted'] as bool? ?? false,
      priority: TaskPriority.values.firstWhere(
        (e) => e.name == json['priority'],
        orElse: () => TaskPriority.medium,
      ),
      category: TaskCategory.values.firstWhere(
        (e) => e.name == json['category'],
        orElse: () => TaskCategory.others,
      ),
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
      completedAt: json['completedAt'] != null
          ? DateTime.parse(json['completedAt'] as String)
          : null,
    );
  }
}

// ==========================================================================
// 5. LOCAL STORAGE UTILITY
// ==========================================================================

class TaskLocalStorage {
  // Saves the entire list of tasks to SharedPreferences
  static Future<bool> saveTasks(List<Task> tasks) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final String jsonStr = jsonEncode(tasks.map((t) => t.toJson()).toList());
      return await prefs.setString(AppConstants.storageKey, jsonStr);
    } catch (e) {
      debugPrint('Storage Write Error: $e');
      return false;
    }
  }

  // Loads the list of tasks from SharedPreferences
  static Future<List<Task>> loadTasks() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final String? jsonStr = prefs.getString(AppConstants.storageKey);
      if (jsonStr == null || jsonStr.isEmpty) return [];
      
      final List<dynamic> decodedList = jsonDecode(jsonStr) as List<dynamic>;
      return decodedList.map((item) => Task.fromJson(item as Map<String, dynamic>)).toList();
    } catch (e) {
      debugPrint('Storage Read Error: $e');
      return [];
    }
  }

  // Clear all storage content
  static Future<bool> clearAll() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return await prefs.remove(AppConstants.storageKey);
    } catch (e) {
      debugPrint('Storage Clear Error: $e');
      return false;
    }
  }
}

// ==========================================================================
// 6. RESPONSIVE LAYOUT HELPERS & EXTENSIONS
// ==========================================================================

extension ResponsiveContext on BuildContext {
  // Screen metrics
  double get screenWidth => MediaQuery.of(this).size.width;
  double get screenHeight => MediaQuery.of(this).size.height;
  Orientation get orientation => MediaQuery.of(this).orientation;
  bool get isLandscape => orientation == Orientation.landscape;

  // Responsive Breakpoints (Material M3 Standards)
  bool get isSmallMobile => screenWidth < 360;
  bool get isMobile => screenWidth < 600;
  bool get isTablet => screenWidth >= 600 && screenWidth < 1024;
  bool get isDesktop => screenWidth >= 1024;

  // Dynamic layout attributes
  double get responsivePadding => isDesktop 
      ? AppConstants.paddingLarge 
      : isTablet 
          ? AppConstants.paddingMedium 
          : AppConstants.paddingSmall;

  int get statsGridColumnCount {
    if (isDesktop) return 4;
    if (isTablet) return 2;
    return 2;
  }
}

// ==========================================================================
// 7. MAIN CONTROLLER & MAIN STATE WORKHORSE
// ==========================================================================

class TodoAppHome extends StatefulWidget {
  final ThemeMode themeMode;
  final ValueChanged<ThemeMode> onThemeChanged;

  const TodoAppHome({
    super.key,
    required this.themeMode,
    required this.onThemeChanged,
  });

  @override
  State<TodoAppHome> createState() => _TodoAppHomeState();
}

class _TodoAppHomeState extends State<TodoAppHome> with SingleTickerProviderStateMixin {
  // App tasks list state
  List<Task> _tasks = [];
  bool _isLoading = true;

  // Filters, search & sorting state
  String _searchQuery = '';
  TaskFilterOption _activeFilter = TaskFilterOption.all;
  TaskSortOption _activeSort = TaskSortOption.newest;
  TaskCategory? _selectedCategory; // Null represents "All Categories"

  // Navigation Index for mobile layout
  int _currentNavIndex = 0;

  // Undo memory cache
  Task? _lastDeletedTask;
  int? _lastDeletedTaskIndex;

  @override
  void initState() {
    super.initState();
    _loadTasks();
  }

  // Retrieve initial list from device SharedPreferences
  Future<void> _loadTasks() async {
    final loaded = await TaskLocalStorage.loadTasks();
    setState(() {
      _tasks = loaded;
      _isLoading = false;
    });
  }

  // Central persistence state synchronizer
  Future<void> _syncTasksToStorage() async {
    await TaskLocalStorage.saveTasks(_tasks);
  }

  // Core business methods (CRUD)
  void _addTask(Task task) {
    // Prevent duplicate titles
    if (_tasks.any((t) => t.title.trim().toLowerCase() == task.title.trim().toLowerCase())) {
      _showErrorSnackBar('A task with the same title already exists.');
      return;
    }

    setState(() {
      _tasks.insert(0, task);
    });
    _syncTasksToStorage();
    _showSuccessSnackBar('Task created successfully!');
  }

  void _editTask(String id, String updatedTitle, String updatedDesc, String updatedNotes, TaskPriority priority, TaskCategory category) {
    if (_tasks.any((t) => t.id != id && t.title.trim().toLowerCase() == updatedTitle.trim().toLowerCase())) {
      _showErrorSnackBar('A task with the same title already exists.');
      return;
    }

    setState(() {
      final index = _tasks.indexWhere((t) => t.id == id);
      if (index != -1) {
        _tasks[index] = _tasks[index].copyWith(
          title: updatedTitle,
          description: updatedDesc,
          notes: updatedNotes,
          priority: priority,
          category: category,
          updatedAt: DateTime.now(),
        );
      }
    });
    _syncTasksToStorage();
    _showSuccessSnackBar('Task updated successfully!');
  }

  void _toggleTaskStatus(String id) {
    setState(() {
      final index = _tasks.indexWhere((t) => t.id == id);
      if (index != -1) {
        final currentStatus = _tasks[index].isCompleted;
        _tasks[index] = _tasks[index].copyWith(
          isCompleted: !currentStatus,
          completedAt: !currentStatus ? DateTime.now() : null,
          updatedAt: DateTime.now(),
        );
      }
    });
    _syncTasksToStorage();
  }

  void _deleteTask(String id) {
    final index = _tasks.indexWhere((t) => t.id == id);
    if (index != -1) {
      setState(() {
        _lastDeletedTask = _tasks[index];
        _lastDeletedTaskIndex = index;
        _tasks.removeAt(index);
      });
      _syncTasksToStorage();
      _showUndoSnackBar();
    }
  }

  void _undoDelete() {
    if (_lastDeletedTask != null && _lastDeletedTaskIndex != null) {
      setState(() {
        _tasks.insert(_lastDeletedTaskIndex!, _lastDeletedTask!);
        _lastDeletedTask = null;
        _lastDeletedTaskIndex = null;
      });
      _syncTasksToStorage();
      _showSuccessSnackBar('Task restored.');
    }
  }

  void _resetApp() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Reset All Data?'),
        content: const Text('This will delete all tasks and settings permanently. This action is irreversible.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            style: FilledButton.styleFrom(
              backgroundColor: Theme.of(context).colorScheme.error,
              foregroundColor: Theme.of(context).colorScheme.onError,
            ),
            child: const Text('Reset'),
          ),
        ],
      ),
    );

    if (confirm == true) {
      setState(() {
        _tasks.clear();
        _selectedCategory = null;
        _searchQuery = '';
        _activeFilter = TaskFilterOption.all;
        _activeSort = TaskSortOption.newest;
      });
      await TaskLocalStorage.clearAll();
      _showSuccessSnackBar('Application reset successfully.');
    }
  }

  // SnackBar feedback helpers
  void _showSuccessSnackBar(String msg) {
    ScaffoldMessenger.of(context).clearSnackBars();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(msg),
        behavior: SnackBarBehavior.floating,
        backgroundColor: AppColors.success,
        duration: const Duration(seconds: 2),
      ),
    );
  }

  void _showErrorSnackBar(String msg) {
    ScaffoldMessenger.of(context).clearSnackBars();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(msg),
        behavior: SnackBarBehavior.floating,
        backgroundColor: AppColors.error,
        duration: const Duration(seconds: 3),
      ),
    );
  }

  void _showUndoSnackBar() {
    ScaffoldMessenger.of(context).clearSnackBars();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: const Text('Task deleted.'),
        behavior: SnackBarBehavior.floating,
        action: SnackBarAction(
          label: 'UNDO',
          textColor: Colors.white,
          onPressed: _undoDelete,
        ),
        duration: const Duration(seconds: 4),
      ),
    );
  }

  // Computing and filtering lists inside state dynamically
  List<Task> get _processedTasks {
    List<Task> result = List.from(_tasks);

    // 1. Category filter
    if (_selectedCategory != null) {
      result = result.where((t) => t.category == _selectedCategory).toList();
    }

    // 2. Search query filter
    if (_searchQuery.isNotEmpty) {
      final query = _searchQuery.trim().toLowerCase();
      result = result.where((t) {
        return t.title.toLowerCase().contains(query) ||
            t.description.toLowerCase().contains(query) ||
            t.notes.toLowerCase().contains(query);
      }).toList();
    }

    // 3. Status filter
    switch (_activeFilter) {
      case TaskFilterOption.pending:
        result = result.where((t) => !t.isCompleted).toList();
        break;
      case TaskFilterOption.completed:
        result = result.where((t) => t.isCompleted).toList();
        break;
      case TaskFilterOption.highPriority:
        result = result.where((t) => t.priority == TaskPriority.high).toList();
        break;
      case TaskFilterOption.all:
        break;
    }

    // 4. Sorting logic
    switch (_activeSort) {
      case TaskSortOption.alphabetically:
        result.sort((a, b) => a.title.toLowerCase().compareTo(b.title.toLowerCase()));
        break;
      case TaskSortOption.newest:
        result.sort((a, b) => b.createdAt.compareTo(a.createdAt));
        break;
      case TaskSortOption.oldest:
        result.sort((a, b) => a.createdAt.compareTo(b.createdAt));
        break;
      case TaskSortOption.completedFirst:
        result.sort((a, b) {
          if (a.isCompleted == b.isCompleted) return b.createdAt.compareTo(a.createdAt);
          return a.isCompleted ? -1 : 1;
        });
        break;
      case TaskSortOption.pendingFirst:
        result.sort((a, b) {
          if (a.isCompleted == b.isCompleted) return b.createdAt.compareTo(a.createdAt);
          return a.isCompleted ? 1 : -1;
        });
        break;
      case TaskSortOption.priorityHighFirst:
        result.sort((a, b) {
          if (a.priority == b.priority) return b.createdAt.compareTo(a.createdAt);
          return b.priority.index.compareTo(a.priority.index);
        });
        break;
    }

    return result;
  }

  // Count items for statistics cards
  int get _totalCount => _tasks.length;
  int get _completedCount => _tasks.where((t) => t.isCompleted).toList().length;
  int get _pendingCount => _totalCount - _completedCount;
  double get _completionPercentage => _totalCount == 0 ? 0.0 : _completedCount / _totalCount;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final processedList = _processedTasks;

    // Mobile layout vs Large layout selection
    if (context.isDesktop || (context.isTablet && context.isLandscape)) {
      return _buildLargeScreenLayout(theme, processedList);
    }
    return _buildMobileLayout(theme, processedList);
  }

  // ==========================================================================
  // LAYOUT A: ULTRA-WIDE RESPONSIVE SCREEN GRID LAYOUT (Desktop & Tablets)
  // ==========================================================================
  
  Widget _buildLargeScreenLayout(ThemeData theme, List<Task> processedList) {
    return Scaffold(
      body: SafeArea(
        child: Row(
          children: [
            // LEFT PANEL: NAVIGATION & REALTIME DASHBOARD SIDEBAR (Fixed 320 width)
            Container(
              width: 340,
              decoration: BoxDecoration(
                border: Border(right: BorderSide(color: theme.dividerColor.withValues(alpha: 0.08))),
                color: theme.colorScheme.surfaceContainer,
              ),
              child: Column(
                children: [
                  _buildSidebarHeader(theme),
                  const Divider(height: 1),
                  Expanded(
                    child: SingleChildScrollView(
                      padding: const EdgeInsets.all(AppConstants.paddingMedium),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          _buildMiniProfileTile(theme),
                          const SizedBox(height: 20),
                          _buildDesktopStatisticsSection(theme),
                          const SizedBox(height: 20),
                          _buildDesktopCategorySection(theme),
                        ],
                      ),
                    ),
                  ),
                  _buildSidebarFooter(theme),
                ],
              ),
            ),
            
            // RIGHT PANEL: SEARCHBAR, FILTERING BAR & TASK LIST (Expanded View)
            Expanded(
              child: Container(
                color: theme.scaffoldBackgroundColor,
                child: Padding(
                  padding: EdgeInsets.all(context.responsivePadding),
                  child: Column(
                    children: [
                      _buildDesktopToolbarSection(theme),
                      const SizedBox(height: 16),
                      _buildDesktopFilterChipRow(theme),
                      const SizedBox(height: 20),
                      
                      // Active list container
                      Expanded(
                        child: _isLoading
                            ? const Center(child: CircularProgressIndicator())
                            : _buildMainContentArea(processedList),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _openAddTaskDialog,
        icon: const Icon(Icons.add_rounded),
        label: const Text('Add Task'),
        elevation: 3,
      ),
    );
  }

  // ==========================================================================
  // LAYOUT B: SLEEK ADAPTIVE MOBILE LAYOUT (Phones & Portrait Tablets)
  // ==========================================================================

  Widget _buildMobileLayout(ThemeData theme, List<Task> processedList) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          _getMobileTitle(),
          style: theme.textTheme.headlineMedium?.copyWith(
            fontWeight: FontWeight.w800,
            letterSpacing: -0.5,
          ),
        ),
        actions: _getMobileAppBarActions(theme),
      ),
      body: _isLoading 
          ? const Center(child: CircularProgressIndicator())
          : AnimatedSwitcher(
              duration: const Duration(milliseconds: 300),
              child: _buildSelectedMobileTab(processedList),
            ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentNavIndex,
        onDestinationSelected: (idx) {
          setState(() {
            _currentNavIndex = idx;
          });
        },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.task_alt_rounded),
            selectedIcon: Icon(Icons.task_alt_rounded),
            label: 'Tasks',
          ),
          NavigationDestination(
            icon: Icon(Icons.analytics_outlined),
            selectedIcon: Icon(Icons.analytics_rounded),
            label: 'Analytics',
          ),
          NavigationDestination(
            icon: Icon(Icons.info_outline_rounded),
            selectedIcon: Icon(Icons.info_rounded),
            label: 'About',
          ),
        ],
      ),
      floatingActionButton: _currentNavIndex == 0
          ? FloatingActionButton(
              onPressed: _openAddTaskDialog,
              elevation: 4,
              child: const Icon(Icons.add_rounded, size: 28),
            )
          : null,
    );
  }

  // ==========================================================================
  // COMPONENTS: COMPONENT WIDGET SUB-FUNCTIONS
  // ==========================================================================

  String _getMobileTitle() {
    switch (_currentNavIndex) {
      case 1:
        return 'Analytics';
      case 2:
        return 'Settings';
      case 0:
      default:
        return 'Tasks';
    }
  }

  List<Widget> _getMobileAppBarActions(ThemeData theme) {
    if (_currentNavIndex == 0) {
      return [
        IconButton(
          icon: const Icon(Icons.search_rounded),
          onPressed: _openMobileSearchSheet,
        ),
        PopupMenuButton<TaskSortOption>(
          icon: const Icon(Icons.sort_rounded),
          tooltip: 'Sort Tasks',
          onSelected: (sortOpt) {
            setState(() {
              _activeSort = sortOpt;
            });
          },
          itemBuilder: (context) => TaskSortOption.values.map((opt) {
            return PopupMenuItem<TaskSortOption>(
              value: opt,
              child: Row(
                children: [
                  Icon(
                    _activeSort == opt ? Icons.radio_button_checked_rounded : Icons.radio_button_off_rounded,
                    color: _activeSort == opt ? theme.colorScheme.primary : theme.disabledColor,
                    size: 18,
                  ),
                  const SizedBox(width: 12),
                  Text(opt.label),
                ],
              ),
            );
          }).toList(),
        ),
        _buildThemeToggle(theme),
      ];
    }
    return [_buildThemeToggle(theme)];
  }

  Widget _buildThemeToggle(ThemeData theme) {
    final isDark = theme.brightness == Brightness.dark;
    return IconButton(
      icon: AnimatedSwitcher(
        duration: const Duration(milliseconds: 300),
        transitionBuilder: (child, anim) => ScaleTransition(scale: anim, child: child),
        child: Icon(
          isDark ? Icons.light_mode_rounded : Icons.dark_mode_rounded,
          key: ValueKey(isDark),
        ),
      ),
      tooltip: 'Toggle Theme',
      onPressed: () {
        widget.onThemeChanged(isDark ? ThemeMode.light : ThemeMode.dark);
      },
    );
  }

  Widget _buildSelectedMobileTab(List<Task> processedList) {
    switch (_currentNavIndex) {
      case 1:
        return SingleChildScrollView(
          padding: const EdgeInsets.all(AppConstants.paddingMedium),
          child: Column(
            key: const ValueKey('analytics_tab'),
            children: [
              _buildResponsiveStatsGrid(),
              const SizedBox(height: 20),
              _buildProgressMetricCard(),
              const SizedBox(height: 20),
              _buildTaskDistributionChart(),
            ],
          ),
        );
      case 2:
        return _buildAboutScreen();
      case 0:
      default:
        return Column(
          key: const ValueKey('tasks_tab'),
          children: [
            // Mini stats card to keep mobile tasks engaging
            if (_totalCount > 0) _buildMobileMiniStatsHeader(),
            _buildMobileCategoryHorizontalList(),
            _buildMobileActiveFiltersInfoRow(),
            Expanded(child: _buildMainContentArea(processedList)),
          ],
        );
    }
  }

  Widget _buildMainContentArea(List<Task> processedList) {
    if (processedList.isEmpty) {
      return _buildEmptyStateView();
    }
    return ListView.builder(
      padding: EdgeInsets.zero,
      itemCount: processedList.length,
      physics: const BouncingScrollPhysics(),
      itemBuilder: (context, index) {
        final task = processedList[index];
        return AnimatedTaskCard(
          key: ValueKey(task.id),
          task: task,
          onToggle: () => _toggleTaskStatus(task.id),
          onDelete: () => _deleteTask(task.id),
          onEdit: () => _openEditTaskDialog(task),
        );
      },
    );
  }

  // Sidebar header component
  Widget _buildSidebarHeader(ThemeData theme) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [theme.colorScheme.primary, theme.colorScheme.secondary],
              ),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(Icons.check_box_rounded, color: Colors.white, size: 24),
          ),
          const SizedBox(width: 12),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Fuzzu Tasks',
                style: theme.textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.w900,
                  letterSpacing: -0.5,
                ),
              ),
              Text(
                'Professional Edition',
                style: theme.textTheme.labelSmall?.copyWith(
                  color: theme.colorScheme.primary.withValues(alpha: 0.8),
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMiniProfileTile(ThemeData theme) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHigh,
        borderRadius: BorderRadius.circular(AppConstants.radiusMedium),
      ),
      child: Row(
        children: [
          CircleAvatar(
            backgroundColor: theme.colorScheme.primary.withValues(alpha: 0.2),
            child: Text(
              'FT',
              style: TextStyle(color: theme.colorScheme.primary, fontWeight: FontWeight.bold),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Fuzzu Developer',
                  style: theme.textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.bold),
                ),
                Text(
                  'Premium Account',
                  style: theme.textTheme.bodySmall?.copyWith(color: theme.disabledColor),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDesktopStatisticsSection(ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(left: 4, bottom: 8),
          child: Text(
            'STATISTICS',
            style: theme.textTheme.labelMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: theme.disabledColor,
            ),
          ),
        ),
        _buildStatTile(theme, 'Total Tasks', _totalCount.toString(), Icons.assignment_rounded, theme.colorScheme.primary),
        const SizedBox(height: 8),
        _buildStatTile(theme, 'Completed', _completedCount.toString(), Icons.task_alt_rounded, AppColors.success),
        const SizedBox(height: 8),
        _buildStatTile(theme, 'Pending', _pendingCount.toString(), Icons.pending_actions_rounded, AppColors.warning),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: theme.colorScheme.surfaceContainerHigh,
            borderRadius: BorderRadius.circular(AppConstants.radiusSmall),
          ),
          child: AnimatedProgressBar(
            percentage: _completionPercentage,
            gradientColors: [theme.colorScheme.primary, AppColors.success],
          ),
        ),
      ],
    );
  }

  Widget _buildStatTile(ThemeData theme, String label, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHigh.withValues(alpha: 0.5),
        borderRadius: BorderRadius.circular(AppConstants.radiusSmall),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              Icon(icon, color: color, size: 20),
              const SizedBox(width: 12),
              Text(label, style: theme.textTheme.bodyMedium),
            ],
          ),
          Text(value, style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _buildDesktopCategorySection(ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(left: 4, bottom: 8),
          child: Text(
            'CATEGORIES',
            style: theme.textTheme.labelMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: theme.disabledColor,
            ),
          ),
        ),
        InkWell(
          onTap: () => setState(() => _selectedCategory = null),
          borderRadius: BorderRadius.circular(AppConstants.radiusSmall),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
            decoration: BoxDecoration(
              color: _selectedCategory == null ? theme.colorScheme.primary.withValues(alpha: 0.15) : Colors.transparent,
              borderRadius: BorderRadius.circular(AppConstants.radiusSmall),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.grid_view_rounded,
                      color: _selectedCategory == null ? theme.colorScheme.primary : theme.disabledColor,
                      size: 20,
                    ),
                    const SizedBox(width: 12),
                    Text(
                      'All Tasks',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        fontWeight: _selectedCategory == null ? FontWeight.bold : FontWeight.normal,
                      ),
                    ),
                  ],
                ),
                Text(
                  _tasks.length.toString(),
                  style: theme.textTheme.bodySmall?.copyWith(fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 4),
        ...TaskCategory.values.map((cat) {
          final isSelected = _selectedCategory == cat;
          final count = _tasks.where((t) => t.category == cat).length;
          return Padding(
            padding: const EdgeInsets.only(bottom: 4),
            child: InkWell(
              onTap: () => setState(() => _selectedCategory = cat),
              borderRadius: BorderRadius.circular(AppConstants.radiusSmall),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                decoration: BoxDecoration(
                  color: isSelected ? theme.colorScheme.primary.withValues(alpha: 0.15) : Colors.transparent,
                  borderRadius: BorderRadius.circular(AppConstants.radiusSmall),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      children: [
                        Icon(
                          cat.icon,
                          color: isSelected ? theme.colorScheme.primary : cat.color,
                          size: 20,
                        ),
                        const SizedBox(width: 12),
                        Text(
                          cat.label,
                          style: theme.textTheme.bodyMedium?.copyWith(
                            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                          ),
                        ),
                      ],
                    ),
                    Text(
                      count.toString(),
                      style: theme.textTheme.bodySmall?.copyWith(
                        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
        }),
      ],
    );
  }

  Widget _buildSidebarFooter(ThemeData theme) {
    return Padding(
      padding: const EdgeInsets.all(AppConstants.paddingMedium),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildThemeToggle(theme),
              Text(
                'Light / Dark',
                style: theme.textTheme.bodySmall?.copyWith(color: theme.disabledColor),
              ),
            ],
          ),
          const SizedBox(height: 8),
          OutlinedButton.icon(
            onPressed: _resetApp,
            icon: const Icon(Icons.restore_rounded, size: 16),
            label: const Text('Reset All Data'),
            style: OutlinedButton.styleFrom(
              minimumSize: const Size.fromHeight(40),
              foregroundColor: theme.colorScheme.error,
              side: BorderSide(color: theme.colorScheme.error.withValues(alpha: 0.5)),
            ),
          ),
          const SizedBox(height: 8),
          InkWell(
            onTap: _openAboutDialog,
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 4),
              child: Text(
                'About App',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.primary,
                  decoration: TextDecoration.underline,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDesktopToolbarSection(ThemeData theme) {
    return Row(
      children: [
        Expanded(
          child: Container(
            height: 52,
            padding: const EdgeInsets.symmetric(horizontal: 16),
            decoration: BoxDecoration(
              color: theme.colorScheme.surfaceContainer,
              borderRadius: BorderRadius.circular(AppConstants.radiusMedium),
              border: Border.all(color: theme.dividerColor.withValues(alpha: 0.08)),
            ),
            child: Row(
              children: [
                Icon(Icons.search_rounded, color: theme.disabledColor),
                const SizedBox(width: 12),
                Expanded(
                  child: TextField(
                    onChanged: (val) {
                      setState(() {
                        _searchQuery = val;
                      });
                    },
                    decoration: const InputDecoration(
                      hintText: 'Search tasks by title, description or notes...',
                      border: InputBorder.none,
                      isDense: true,
                    ),
                  ),
                ),
                if (_searchQuery.isNotEmpty)
                  IconButton(
                    icon: const Icon(Icons.clear_rounded),
                    onPressed: () {
                      setState(() {
                        _searchQuery = '';
                      });
                    },
                  ),
              ],
            ),
          ),
        ),
        const SizedBox(width: 16),
        Container(
          height: 52,
          padding: const EdgeInsets.symmetric(horizontal: 12),
          decoration: BoxDecoration(
            color: theme.colorScheme.surfaceContainer,
            borderRadius: BorderRadius.circular(AppConstants.radiusMedium),
            border: Border.all(color: theme.dividerColor.withValues(alpha: 0.08)),
          ),
          child: DropdownButtonHideUnderline(
            child: DropdownButton<TaskSortOption>(
              value: _activeSort,
              icon: const Icon(Icons.sort_rounded),
              elevation: 4,
              borderRadius: BorderRadius.circular(AppConstants.radiusMedium),
              onChanged: (TaskSortOption? newValue) {
                if (newValue != null) {
                  setState(() {
                    _activeSort = newValue;
                  });
                }
              },
              items: TaskSortOption.values.map<DropdownMenuItem<TaskSortOption>>((TaskSortOption value) {
                return DropdownMenuItem<TaskSortOption>(
                  value: value,
                  child: Text(
                    value.label,
                    style: theme.textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w600),
                  ),
                );
              }).toList(),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildDesktopFilterChipRow(ThemeData theme) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: TaskFilterOption.values.map((opt) {
          final isSelected = _activeFilter == opt;
          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: FilterChip(
              selected: isSelected,
              label: Text(opt.label),
              onSelected: (selected) {
                setState(() {
                  _activeFilter = opt;
                });
              },
              backgroundColor: theme.colorScheme.surfaceContainer,
              selectedColor: theme.colorScheme.primary.withValues(alpha: 0.2),
              checkmarkColor: theme.colorScheme.primary,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(AppConstants.radiusMax),
                side: BorderSide(
                  color: isSelected ? theme.colorScheme.primary : theme.dividerColor.withValues(alpha: 0.1),
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  // ==========================================================================
  // MOBILE SUB-COMPONENTS
  // ==========================================================================

  Widget _buildMobileMiniStatsHeader() {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: AppConstants.paddingMedium, vertical: 8),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: theme.colorScheme.surfaceContainerHigh,
          borderRadius: BorderRadius.circular(AppConstants.radiusMedium),
        ),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Text(
                        'Total Progress',
                        style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold),
                      ),
                      const Spacer(),
                      Text(
                        '$_completedCount / $_totalCount Completed',
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.primary,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  AnimatedProgressBar(
                    percentage: _completionPercentage,
                    gradientColors: [theme.colorScheme.primary, AppColors.success],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMobileCategoryHorizontalList() {
    final theme = Theme.of(context);
    return Container(
      height: 50,
      margin: const EdgeInsets.symmetric(vertical: 8),
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: AppConstants.paddingMedium),
        itemCount: TaskCategory.values.length + 1,
        itemBuilder: (context, index) {
          final isAll = index == 0;
          final cat = isAll ? null : TaskCategory.values[index - 1];
          final isSelected = _selectedCategory == cat;
          
          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: ChoiceChip(
              label: Text(isAll ? 'All Categories' : cat!.label),
              selected: isSelected,
              onSelected: (_) {
                setState(() {
                  _selectedCategory = cat;
                });
              },
              avatar: isAll 
                  ? const Icon(Icons.grid_view_rounded, size: 16)
                  : Icon(cat!.icon, size: 16, color: isSelected ? Colors.white : cat.color),
              selectedColor: theme.colorScheme.primary,
              labelStyle: TextStyle(
                color: isSelected ? Colors.white : theme.textTheme.bodyMedium?.color,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildMobileActiveFiltersInfoRow() {
    final theme = Theme.of(context);
    final hasSearch = _searchQuery.isNotEmpty;
    final hasFilter = _activeFilter != TaskFilterOption.all;
    
    if (!hasSearch && !hasFilter) return const SizedBox.shrink();
    
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: AppConstants.paddingMedium, vertical: 4),
      child: Wrap(
        spacing: 8,
        crossAxisAlignment: WrapCrossAlignment.center,
        children: [
          Text(
            'Filters active:',
            style: theme.textTheme.bodySmall?.copyWith(color: theme.disabledColor),
          ),
          if (hasFilter)
            Chip(
              label: Text(_activeFilter.label, style: const TextStyle(fontSize: 10)),
              onDeleted: () {
                setState(() {
                  _activeFilter = TaskFilterOption.all;
                });
              },
              materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
              padding: EdgeInsets.zero,
            ),
          if (hasSearch)
            Chip(
              label: Text('Search: "$_searchQuery"', style: const TextStyle(fontSize: 10)),
              onDeleted: () {
                setState(() {
                  _searchQuery = '';
                });
              },
              materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
              padding: EdgeInsets.zero,
            ),
        ],
      ),
    );
  }

  // Mobile BottomSheet Search Interface
  void _openMobileSearchSheet() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Theme.of(context).colorScheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(AppConstants.radiusLarge)),
      ),
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setSheetState) {
            return Padding(
              padding: EdgeInsets.only(
                bottom: MediaQuery.of(context).viewInsets.bottom + 16,
                top: 16,
                left: 16,
                right: 16,
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 40,
                    height: 4,
                    decoration: BoxDecoration(
                      color: Colors.grey.shade400,
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Search Tasks',
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
                      ),
                      // Dropdown filter inside mobile search sheet
                      DropdownButton<TaskFilterOption>(
                        value: _activeFilter,
                        underline: const SizedBox.shrink(),
                        icon: const Icon(Icons.filter_list_rounded),
                        onChanged: (opt) {
                          if (opt != null) {
                            setState(() {
                              _activeFilter = opt;
                            });
                            setSheetState(() {});
                          }
                        },
                        items: TaskFilterOption.values.map((opt) {
                          return DropdownMenuItem(
                            value: opt,
                            child: Text(opt.label),
                          );
                        }).toList(),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    autofocus: true,
                    decoration: InputDecoration(
                      hintText: 'Type task details...',
                      prefixIcon: const Icon(Icons.search_rounded),
                      suffixIcon: _searchQuery.isNotEmpty
                          ? IconButton(
                              icon: const Icon(Icons.clear_rounded),
                              onPressed: () {
                                setState(() => _searchQuery = '');
                                setSheetState(() {});
                              },
                            )
                          : null,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(AppConstants.radiusMedium),
                      ),
                    ),
                    onChanged: (val) {
                      setState(() {
                        _searchQuery = val;
                      });
                      setSheetState(() {});
                    },
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }

  // ==========================================================================
  // METRICS & CHARTS COMPONENT WIDGETS
  // ==========================================================================

  Widget _buildResponsiveStatsGrid() {
    return LayoutBuilder(
      builder: (context, constraints) {
        return GridView.count(
          crossAxisCount: context.statsGridColumnCount,
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          childAspectRatio: 1.4,
          children: [
            _buildMobileDashboardCard('Total Tasks', _totalCount.toString(), Icons.assignment_rounded, AppColors.primarySeed),
            _buildMobileDashboardCard('Completed', _completedCount.toString(), Icons.task_alt_rounded, AppColors.success),
            _buildMobileDashboardCard('Pending', _pendingCount.toString(), Icons.pending_actions_rounded, AppColors.warning),
            _buildMobileDashboardCard('Completion %', '${(_completionPercentage * 100).toInt()}%', Icons.query_stats_rounded, AppColors.info),
          ],
        );
      },
    );
  }

  Widget _buildMobileDashboardCard(String title, String value, IconData icon, Color accentColor) {
    final theme = Theme.of(context);
    return Card(
      color: theme.colorScheme.surfaceContainer,
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Icon(icon, color: accentColor, size: 24),
                Container(
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(shape: BoxShape.circle, color: accentColor),
                ),
              ],
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  value,
                  style: theme.textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.w900,
                    letterSpacing: -1,
                  ),
                ),
                Text(
                  title,
                  style: theme.textTheme.bodySmall?.copyWith(color: theme.disabledColor),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProgressMetricCard() {
    final theme = Theme.of(context);
    return Card(
      color: theme.colorScheme.surfaceContainer,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Your Productivity Index',
              style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 6),
            Text(
              'Keep checking off items to maintain your high score.',
              style: theme.textTheme.bodySmall?.copyWith(color: theme.disabledColor),
            ),
            const SizedBox(height: 16),
            AnimatedProgressBar(
              percentage: _completionPercentage,
              gradientColors: [theme.colorScheme.primary, AppColors.success],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTaskDistributionChart() {
    final theme = Theme.of(context);
    
    // Compute category numbers
    final Map<TaskCategory, int> catCounts = {};
    for (var cat in TaskCategory.values) {
      catCounts[cat] = _tasks.where((t) => t.category == cat).length;
    }
    
    final maxCount = catCounts.values.isEmpty 
        ? 1 
        : catCounts.values.fold<int>(0, (max, val) => val > max ? val : max);
    
    return Card(
      color: theme.colorScheme.surfaceContainer,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Category Distribution',
              style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            ...TaskCategory.values.map((cat) {
              final count = catCounts[cat] ?? 0;
              final relativeRatio = maxCount == 0 ? 0.0 : count / maxCount;
              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 6.0),
                child: Row(
                  children: [
                    Icon(cat.icon, color: cat.color, size: 18),
                    const SizedBox(width: 8),
                    SizedBox(
                      width: 80,
                      child: Text(
                        cat.label,
                        style: theme.textTheme.bodyMedium,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: LayoutBuilder(
                        builder: (context, constraints) {
                          return Stack(
                            children: [
                              Container(
                                height: 8,
                                decoration: BoxDecoration(
                                  color: theme.dividerColor.withValues(alpha: 0.08),
                                  borderRadius: BorderRadius.circular(4),
                                ),
                              ),
                              AnimatedContainer(
                                duration: const Duration(milliseconds: 500),
                                width: constraints.maxWidth * relativeRatio,
                                height: 8,
                                decoration: BoxDecoration(
                                  color: cat.color,
                                  borderRadius: BorderRadius.circular(4),
                                ),
                              ),
                            ],
                          );
                        },
                      ),
                    ),
                    const SizedBox(width: 12),
                    Text(
                      count.toString(),
                      style: theme.textTheme.bodySmall?.copyWith(fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
              );
            }),
          ],
        ),
      ),
    );
  }

  // ==========================================================================
  // ABOUT SECTION UI
  // ==========================================================================

  Widget _buildAboutScreen() {
    final theme = Theme.of(context);
    return SingleChildScrollView(
      key: const ValueKey('settings_tab'),
      padding: const EdgeInsets.all(AppConstants.paddingMedium),
      child: Column(
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                children: [
                  Container(
                    width: 70,
                    height: 70,
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [theme.colorScheme.primary, theme.colorScheme.secondary],
                      ),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.check_box_rounded, color: Colors.white, size: 36),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Fuzzu Tasks',
                    style: theme.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold),
                  ),
                  Text(
                    'Version 1.0.0 (Production Release)',
                    style: theme.textTheme.bodySmall?.copyWith(color: theme.disabledColor),
                  ),
                  const SizedBox(height: 20),
                  const Divider(),
                  const SizedBox(height: 16),
                  _buildAboutRow(context, 'Author & Instructor', 'FuzzuTech'),
                  _buildAboutRow(context, 'Platform SDK', 'Flutter 3.41 & Dart 3.11'),
                  _buildAboutRow(context, 'Storage Sync', 'JSON / SharedPreferences'),
                  _buildAboutRow(context, 'UX Engine', 'Material 3 Adaptive'),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Card(
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.restore_rounded, color: AppColors.error),
                  title: const Text('Reset Application Database'),
                  subtitle: const Text('Completely deletes all tasks on storage'),
                  onTap: _resetApp,
                ),
                const Divider(height: 1),
                ListTile(
                  leading: const Icon(Icons.info_outline_rounded),
                  title: const Text('Show Educational Project Info'),
                  onTap: _openAboutDialog,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAboutRow(BuildContext context, String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Theme.of(context).disabledColor)),
          Text(value, style: Theme.of(context).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  // ==========================================================================
  // DIALOG FLOWS & INTERACTIVE PROMPTS
  // ==========================================================================

  void _openAddTaskDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) {
        return TaskDialog(
          onSaved: (title, description, notes, priority, category) {
            final newTask = Task(
              id: DateTime.now().millisecondsSinceEpoch.toString(),
              title: title,
              description: description,
              notes: notes,
              isCompleted: false,
              priority: priority,
              category: category,
              createdAt: DateTime.now(),
              updatedAt: DateTime.now(),
            );
            _addTask(newTask);
          },
        );
      },
    );
  }

  void _openEditTaskDialog(Task task) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) {
        return TaskDialog(
          task: task,
          onSaved: (title, description, notes, priority, category) {
            _editTask(task.id, title, description, notes, priority, category);
          },
        );
      },
    );
  }

  void _openAboutDialog() {
    showDialog(
      context: context,
      builder: (context) => const EducationalAboutDialog(),
    );
  }

  // ==========================================================================
  // EMPTY STATE RENDERER
  // ==========================================================================

  Widget _buildEmptyStateView() {
    return LayoutBuilder(
      builder: (context, constraints) {
        return Center(
          child: SingleChildScrollView(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Custom Paint Vector Graphic
                const SizedBox(
                  width: 140,
                  height: 140,
                  child: EmptyStateIllustration(),
                ),
                const SizedBox(height: 24),
                Text(
                  _searchQuery.isNotEmpty 
                      ? 'No search matches'
                      : _selectedCategory != null 
                          ? 'Empty category' 
                          : 'You\'re all caught up!',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 8),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 40.0),
                  child: Text(
                    _searchQuery.isNotEmpty
                        ? 'Try searching with different keywords.'
                        : 'No pending tasks left. Enjoy your free time or add a new task to organize your schedule.',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: Theme.of(context).disabledColor,
                        ),
                  ),
                ),
                const SizedBox(height: 24),
                FilledButton.icon(
                  onPressed: _openAddTaskDialog,
                  icon: const Icon(Icons.add_rounded),
                  label: const Text('Add New Task'),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

// ==========================================================================
// 8. PROGRESS INDICATORS & CHECKBOX ANIMATIONS
// ==========================================================================

class AnimatedProgressBar extends StatelessWidget {
  final double percentage;
  final List<Color> gradientColors;

  const AnimatedProgressBar({
    super.key,
    required this.percentage,
    required this.gradientColors,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        ClipRRect(
          borderRadius: BorderRadius.circular(10),
          child: Container(
            height: 10,
            width: double.infinity,
            color: Theme.of(context).dividerColor.withValues(alpha: 0.08),
            child: Stack(
              children: [
                LayoutBuilder(
                  builder: (context, constraints) {
                    final targetWidth = constraints.maxWidth * percentage;
                    return AnimatedContainer(
                      duration: const Duration(milliseconds: 650),
                      curve: Curves.fastOutSlowIn,
                      width: targetWidth.isNaN ? 0.0 : targetWidth,
                      height: double.infinity,
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: gradientColors,
                          begin: Alignment.centerLeft,
                          end: Alignment.centerRight,
                        ),
                        borderRadius: BorderRadius.circular(10),
                      ),
                    );
                  },
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

// Spring-action Animated Checkbox
class AnimatedTaskCheckbox extends StatefulWidget {
  final bool value;
  final ValueChanged<bool> onChanged;
  final Color activeColor;

  const AnimatedTaskCheckbox({
    super.key,
    required this.value,
    required this.onChanged,
    required this.activeColor,
  });

  @override
  State<AnimatedTaskCheckbox> createState() => _AnimatedTaskCheckboxState();
}

class _AnimatedTaskCheckboxState extends State<AnimatedTaskCheckbox>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 250),
    );
    // Dynamic scale spring-back elastic curve
    _scaleAnimation = Tween<double>(begin: 0.8, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.elasticOut),
    );
    if (widget.value) {
      _controller.forward();
    }
  }

  @override
  void didUpdateWidget(covariant AnimatedTaskCheckbox oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.value != oldWidget.value) {
      if (widget.value) {
        _controller.forward(from: 0.0);
      } else {
        _controller.reverse();
      }
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return GestureDetector(
      onTap: () => widget.onChanged(!widget.value),
      child: ScaleTransition(
        scale: _scaleAnimation,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          width: 26,
          height: 26,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: widget.value ? widget.activeColor : Colors.transparent,
            border: Border.all(
              color: widget.value ? widget.activeColor : theme.disabledColor.withValues(alpha: 0.5),
              width: 2.2,
            ),
          ),
          child: widget.value
              ? const Icon(
                  Icons.check,
                  size: 16,
                  color: Colors.white,
                )
              : null,
        ),
      ),
    );
  }
}

// ==========================================================================
// 9. ANIMATED TASK CARD COMPONENT
// ==========================================================================

class AnimatedTaskCard extends StatefulWidget {
  final Task task;
  final VoidCallback onToggle;
  final VoidCallback onDelete;
  final VoidCallback onEdit;

  const AnimatedTaskCard({
    super.key,
    required this.task,
    required this.onToggle,
    required this.onDelete,
    required this.onEdit,
  });

  @override
  State<AnimatedTaskCard> createState() => _AnimatedTaskCardState();
}

class _AnimatedTaskCardState extends State<AnimatedTaskCard> with SingleTickerProviderStateMixin {
  bool _isExpanded = false;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    // M3 Dismissible structure
    return Padding(
      padding: const EdgeInsets.symmetric(
        horizontal: AppConstants.paddingMedium,
        vertical: 6.0,
      ),
      child: Dismissible(
        key: ValueKey('dismiss_${widget.task.id}'),
        direction: DismissDirection.endToStart,
        onDismissed: (direction) => widget.onDelete(),
        confirmDismiss: (dir) async {
          return await showDialog<bool>(
            context: context,
            builder: (context) => AlertDialog(
              title: const Text('Delete Task'),
              content: Text('Are you sure you want to delete "${widget.task.title}"?'),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context, false),
                  child: const Text('Cancel'),
                ),
                FilledButton(
                  onPressed: () => Navigator.pop(context, true),
                  style: FilledButton.styleFrom(
                    backgroundColor: theme.colorScheme.error,
                    foregroundColor: theme.colorScheme.onError,
                  ),
                  child: const Text('Delete'),
                ),
              ],
            ),
          );
        },
        background: Container(
          alignment: Alignment.centerRight,
          padding: const EdgeInsets.symmetric(horizontal: 24),
          decoration: BoxDecoration(
            color: theme.colorScheme.error,
            borderRadius: BorderRadius.circular(AppConstants.radiusMedium),
          ),
          child: const Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              Text(
                'Delete',
                style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
              ),
              SizedBox(width: 8),
              Icon(Icons.delete_forever_rounded, color: Colors.white),
            ],
          ),
        ),
        child: AnimatedSize(
          duration: const Duration(milliseconds: 250),
          curve: Curves.easeInOut,
          child: Card(
            margin: EdgeInsets.zero,
            child: InkWell(
              borderRadius: BorderRadius.circular(AppConstants.radiusMedium),
              onTap: () {
                setState(() {
                  _isExpanded = !_isExpanded;
                });
              },
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 14.0, vertical: 12.0),
                child: Column(
                  children: [
                    Row(
                      children: [
                        AnimatedTaskCheckbox(
                          value: widget.task.isCompleted,
                          activeColor: AppColors.success,
                          onChanged: (_) => widget.onToggle(),
                        ),
                        const SizedBox(width: 14),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                widget.task.title,
                                style: theme.textTheme.titleMedium?.copyWith(
                                  fontWeight: FontWeight.w700,
                                  decoration: widget.task.isCompleted 
                                      ? TextDecoration.lineThrough 
                                      : TextDecoration.none,
                                  color: widget.task.isCompleted
                                      ? theme.disabledColor
                                      : theme.textTheme.titleMedium?.color,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Row(
                                children: [
                                  // Category indicator pill
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                    decoration: BoxDecoration(
                                      color: widget.task.category.color.withValues(alpha: 0.12),
                                      borderRadius: BorderRadius.circular(6),
                                    ),
                                    child: Row(
                                      children: [
                                        Icon(
                                          widget.task.category.icon,
                                          size: 11,
                                          color: widget.task.category.color,
                                        ),
                                        const SizedBox(width: 4),
                                        Text(
                                          widget.task.category.label,
                                          style: TextStyle(
                                            fontSize: 10,
                                            fontWeight: FontWeight.w800,
                                            color: widget.task.category.color,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  
                                  // Priority indicator pill
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                    decoration: BoxDecoration(
                                      color: widget.task.priority.color.withValues(alpha: 0.12),
                                      borderRadius: BorderRadius.circular(6),
                                    ),
                                    child: Row(
                                      children: [
                                        Icon(
                                          widget.task.priority.icon,
                                          size: 11,
                                          color: widget.task.priority.color,
                                        ),
                                        const SizedBox(width: 4),
                                        Text(
                                          widget.task.priority.label,
                                          style: TextStyle(
                                            fontSize: 10,
                                            fontWeight: FontWeight.w800,
                                            color: widget.task.priority.color,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                        
                        // Context actions menu
                        PopupMenuButton<String>(
                          icon: Icon(Icons.more_vert_rounded, color: theme.disabledColor),
                          onSelected: (val) {
                            if (val == 'edit') {
                              widget.onEdit();
                            } else if (val == 'delete') {
                              widget.onDelete();
                            }
                          },
                          itemBuilder: (context) => [
                            const PopupMenuItem(
                              value: 'edit',
                              child: Row(
                                children: [
                                  Icon(Icons.edit_outlined, size: 18),
                                  SizedBox(width: 10),
                                  Text('Edit Task'),
                                ],
                              ),
                            ),
                            PopupMenuItem(
                              value: 'delete',
                              child: Row(
                                children: [
                                  Icon(Icons.delete_outline_rounded, color: theme.colorScheme.error, size: 18),
                                  const SizedBox(width: 10),
                                  Text(
                                    'Delete',
                                    style: TextStyle(color: theme.colorScheme.error),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                    
                    // Expanding description/notes section
                    if (_isExpanded) ...[
                      const SizedBox(height: 12),
                      const Divider(height: 1),
                      const SizedBox(height: 10),
                      Align(
                        alignment: Alignment.centerLeft,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            if (widget.task.description.isNotEmpty) ...[
                              Text(
                                'Description',
                                style: theme.textTheme.labelMedium?.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: theme.disabledColor,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                widget.task.description,
                                style: theme.textTheme.bodyMedium,
                              ),
                              const SizedBox(height: 10),
                            ],
                            if (widget.task.notes.isNotEmpty) ...[
                              Text(
                                'Internal Notes',
                                style: theme.textTheme.labelMedium?.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: theme.disabledColor,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                widget.task.notes,
                                style: theme.textTheme.bodySmall,
                              ),
                              const SizedBox(height: 10),
                            ],
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  'Created: ${_formatDate(widget.task.createdAt)}',
                                  style: theme.textTheme.labelSmall?.copyWith(color: theme.disabledColor),
                                ),
                                if (widget.task.isCompleted && widget.task.completedAt != null)
                                  Text(
                                    'Completed: ${_formatDate(widget.task.completedAt!)}',
                                    style: theme.textTheme.labelSmall?.copyWith(color: AppColors.success),
                                  ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  String _formatDate(DateTime dt) {
    return '${dt.day}/${dt.month}/${dt.year} - ${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
  }
}

// ==========================================================================
// 10. TASK DIALOG IMPLEMENTATION (ADD & EDIT FLOWS)
// ==========================================================================

class TaskDialog extends StatefulWidget {
  final Task? task; // Null represents "Add Mode"
  final Function(
    String title,
    String description,
    String notes,
    TaskPriority priority,
    TaskCategory category,
  ) onSaved;

  const TaskDialog({
    super.key,
    this.task,
    required this.onSaved,
  });

  @override
  State<TaskDialog> createState() => _TaskDialogState();
}

class _TaskDialogState extends State<TaskDialog> {
  final _formKey = GlobalKey<FormState>();
  
  late TextEditingController _titleController;
  late TextEditingController _descController;
  late TextEditingController _notesController;
  
  late TaskPriority _selectedPriority;
  late TaskCategory _selectedCategory;

  @override
  void initState() {
    super.initState();
    final t = widget.task;
    _titleController = TextEditingController(text: t?.title ?? '');
    _descController = TextEditingController(text: t?.description ?? '');
    _notesController = TextEditingController(text: t?.notes ?? '');
    
    _selectedPriority = t?.priority ?? TaskPriority.medium;
    _selectedCategory = t?.category ?? TaskCategory.personal;
  }

  @override
  void dispose() {
    _titleController.dispose();
    _descController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  void _submitData() {
    if (_formKey.currentState!.validate()) {
      widget.onSaved(
        _titleController.text.trim(),
        _descController.text.trim(),
        _notesController.text.trim(),
        _selectedPriority,
        _selectedCategory,
      );
      Navigator.pop(context);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isEdit = widget.task != null;
    
    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppConstants.radiusLarge)),
      insetPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 24),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 500),
        child: Padding(
          padding: EdgeInsets.only(
            bottom: MediaQuery.of(context).viewInsets.bottom,
          ),
          child: SingleChildScrollView(
            child: Padding(
              padding: const EdgeInsets.all(AppConstants.paddingLarge),
              child: Form(
                key: _formKey,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          isEdit ? 'Edit Task' : 'Create Task',
                          style: theme.textTheme.headlineSmall?.copyWith(
                            fontWeight: FontWeight.w900,
                            letterSpacing: -0.5,
                          ),
                        ),
                        IconButton(
                          icon: const Icon(Icons.close_rounded),
                          onPressed: () => Navigator.pop(context),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    
                    // Task Title Input
                    TextFormField(
                      controller: _titleController,
                      textCapitalization: TextCapitalization.sentences,
                      decoration: InputDecoration(
                        labelText: 'Task Title *',
                        prefixIcon: const Icon(Icons.title_rounded),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(AppConstants.radiusMedium),
                        ),
                      ),
                      validator: (val) {
                        if (val == null || val.trim().isEmpty) {
                          return 'Please enter a task title.';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    
                    // Task Description Input
                    TextFormField(
                      controller: _descController,
                      textCapitalization: TextCapitalization.sentences,
                      maxLines: 2,
                      decoration: InputDecoration(
                        labelText: 'Brief Description',
                        prefixIcon: const Icon(Icons.description_outlined),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(AppConstants.radiusMedium),
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Internal Notes Input
                    TextFormField(
                      controller: _notesController,
                      textCapitalization: TextCapitalization.sentences,
                      maxLines: 2,
                      decoration: InputDecoration(
                        labelText: 'Additional Notes / Reminders',
                        prefixIcon: const Icon(Icons.note_alt_outlined),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(AppConstants.radiusMedium),
                        ),
                      ),
                    ),
                    const SizedBox(height: 20),
                    
                    // Priority chips selection
                    Text(
                      'Task Priority',
                      style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: TaskPriority.values.map((p) {
                        final isSelected = _selectedPriority == p;
                        return Expanded(
                          child: Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 4),
                            child: ChoiceChip(
                              label: Text(p.label),
                              selected: isSelected,
                              onSelected: (_) {
                                setState(() {
                                  _selectedPriority = p;
                                });
                              },
                              selectedColor: p.color.withValues(alpha: 0.2),
                              labelStyle: TextStyle(
                                color: isSelected ? p.color : theme.textTheme.bodyMedium?.color,
                                fontWeight: isSelected ? FontWeight.w800 : FontWeight.normal,
                              ),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(AppConstants.radiusSmall),
                                side: BorderSide(color: isSelected ? p.color : Colors.grey.shade300),
                              ),
                            ),
                          ),
                        );
                      }).toList(),
                    ),
                    const SizedBox(height: 20),
                    
                    // Category Selection Grid layout
                    Text(
                      'Select Category',
                      style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: TaskCategory.values.map((c) {
                        final isSelected = _selectedCategory == c;
                        return ChoiceChip(
                          avatar: Icon(c.icon, size: 16, color: isSelected ? Colors.white : c.color),
                          label: Text(c.label),
                          selected: isSelected,
                          onSelected: (_) {
                            setState(() {
                              _selectedCategory = c;
                            });
                          },
                          selectedColor: c.color,
                          labelStyle: TextStyle(
                            color: isSelected ? Colors.white : theme.textTheme.bodyMedium?.color,
                          ),
                        );
                      }).toList(),
                    ),
                    const SizedBox(height: 24),
                    
                    // Action controls row
                    Row(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        TextButton(
                          onPressed: () => Navigator.pop(context),
                          child: const Text('Cancel'),
                        ),
                        const SizedBox(width: 12),
                        FilledButton(
                          onPressed: _submitData,
                          child: Text(isEdit ? 'Save Changes' : 'Add Task'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

// ==========================================================================
// 11. EDUCATIONAL ABOUT INFO DIALOG
// ==========================================================================

class EducationalAboutDialog extends StatelessWidget {
  const EducationalAboutDialog({super.key});

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Row(
        children: [
          Icon(Icons.school_rounded, color: AppColors.primarySeed),
          SizedBox(width: 12),
          Text('Educational Project'),
        ],
      ),
      content: const SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'This application was developed as a recruitment-level project showcase for the FuzzuTech Flutter course.',
              style: TextStyle(fontWeight: FontWeight.w600),
            ),
            SizedBox(height: 12),
            Text(
              'Key Architecture Highlights:',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 4),
            Text('• Fully responsive LayoutBuilder UI adapting instantly across Web, Tablet, and Mobile.'),
            Text('• State synchronization using SharedPreferences & custom serialization logic.'),
            Text('• Spring-back elastic curves and explicit animation controllers for clean checkbox response.'),
            Text('• Explicit Material 3 standards using custom ColorSchemes & surface containers.'),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Dismiss'),
        ),
      ],
    );
  }
}

// ==========================================================================
// 12. CUSTOM ILLUSTRATION PAINTER (EMPTY STATE VECTOR)
// ==========================================================================

class EmptyStateIllustration extends StatelessWidget {
  const EmptyStateIllustration({super.key});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    return CustomPaint(
      painter: _EmptyIllustrationPainter(
        circleColor: isDark ? const Color(0xFF1E2433) : const Color(0xFFE8EBF4),
        tickColor: AppColors.primarySeed,
        starColor: AppColors.warning,
      ),
    );
  }
}

class _EmptyIllustrationPainter extends CustomPainter {
  final Color circleColor;
  final Color tickColor;
  final Color starColor;

  _EmptyIllustrationPainter({
    required this.circleColor,
    required this.tickColor,
    required this.starColor,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final paint = Paint()
      ..style = PaintingStyle.fill
      ..isAntiAlias = true;

    // Draw background circle base
    paint.color = circleColor;
    canvas.drawCircle(center, size.width * 0.4, paint);

    // Draw elegant checklist ticks/details
    final linePaint = Paint()
      ..color = tickColor
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round
      ..strokeWidth = 6.0;

    final path = Path()
      ..moveTo(size.width * 0.35, size.height * 0.5)
      ..lineTo(size.width * 0.47, size.height * 0.62)
      ..lineTo(size.width * 0.68, size.height * 0.38);
    canvas.drawPath(path, linePaint);

    // Draw decorative little stars/points around the base
    paint.color = starColor;
    canvas.drawCircle(Offset(size.width * 0.22, size.height * 0.3), 5, paint);
    canvas.drawCircle(Offset(size.width * 0.8, size.height * 0.65), 7, paint);
    canvas.drawCircle(Offset(size.width * 0.76, size.height * 0.24), 4, paint);
  }

  @override
  bool shouldRepaint(covariant _EmptyIllustrationPainter oldDelegate) {
    return oldDelegate.circleColor != circleColor ||
        oldDelegate.tickColor != tickColor ||
        oldDelegate.starColor != starColor;
  }
}
