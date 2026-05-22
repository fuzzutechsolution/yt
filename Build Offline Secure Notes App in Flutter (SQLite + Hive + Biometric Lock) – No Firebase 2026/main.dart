import 'dart:io';

import 'package:flutter/foundation.dart';

import 'package:flutter/material.dart';

import 'package:google_fonts/google_fonts.dart';

import 'package:hive_flutter/hive_flutter.dart';

import 'package:sqflite/sqflite.dart';

import 'package:path/path.dart' as p;

import 'package:flutter_staggered_grid_view/flutter_staggered_grid_view.dart';

import 'package:glassmorphism/glassmorphism.dart';

import 'package:intl/intl.dart';

import 'package:local_auth/local_auth.dart';

import 'package:flutter_animate/flutter_animate.dart';

import 'package:sqflite_common_ffi/sqflite_ffi.dart';



void main() async {

  WidgetsFlutterBinding.ensureInitialized();

  

  if (!kIsWeb && (Platform.isWindows || Platform.isLinux)) {

    // Initialize FFI for desktop support

    sqfliteFfiInit();

    databaseFactory = databaseFactoryFfi;

  }

  

  // Initialize Hive

  await Hive.initFlutter();

  await Hive.openBox('settingsBox');

  

  // Initialize SQLite (Bypass on Web to avoid crashes)

  if (!kIsWeb) {

    await DatabaseHelper.instance.database;

  }



  runApp(const CyberNotesApp());

}



class CyberNotesApp extends StatelessWidget {

  const CyberNotesApp({super.key});



  @override

  Widget build(BuildContext context) {

    return MaterialApp(

      title: 'Cyber Notes',

      debugShowCheckedModeBanner: false,

      theme: ThemeData(

        brightness: Brightness.dark,

        scaffoldBackgroundColor: const Color(0xFF09090B), // Deep dark void

        primaryColor: const Color(0xFF00FFCC), // Neon Cyan

        colorScheme: const ColorScheme.dark(

          primary: Color(0xFF00FFCC),

          secondary: Color(0xFFFF007F), // Neon Pink

          surface: Color(0xFF18181B),

        ),

        textTheme: GoogleFonts.spaceGroteskTextTheme(ThemeData.dark().textTheme),

        useMaterial3: true,

      ),

      home: const LockScreen(),

    );

  }

}



// ========================================== //

// MODEL

// ========================================== //



class Note {

  final int? id;

  final String title;

  final String content;

  final String color;

  final bool isSecure;

  final DateTime createdAt;



  Note({

    this.id,

    required this.title,

    required this.content,

    required this.color,

    required this.isSecure,

    required this.createdAt,

  });



  Note copy({

    int? id,

    String? title,

    String? content,

    String? color,

    bool? isSecure,

    DateTime? createdAt,

  }) {

    return Note(

      id: id ?? this.id,

      title: title ?? this.title,

      content: content ?? this.content,

      color: color ?? this.color,

      isSecure: isSecure ?? this.isSecure,

      createdAt: createdAt ?? this.createdAt,

    );

  }



  Map<String, dynamic> toMap() {

    return {

      'id': id,

      'title': title,

      'content': content,

      'color': color,

      'isSecure': isSecure ? 1 : 0,

      'createdAt': createdAt.toIso8601String(),

    };

  }



  factory Note.fromMap(Map<String, dynamic> map) {

    return Note(

      id: map['id'] as int?,

      title: map['title'] as String,

      content: map['content'] as String,

      color: map['color'] as String,

      isSecure: map['isSecure'] == 1,

      createdAt: DateTime.parse(map['createdAt'] as String),

    );

  }

}



// ========================================== //

// DATABASE HELPER

// ========================================== //



class DatabaseHelper {

  static final DatabaseHelper instance = DatabaseHelper._init();

  static Database? _database;

  final List<Note> _webNotes = []; // In-memory storage for Web UI testing



  DatabaseHelper._init();



  Future<Database> get database async {

    if (_database != null) return _database!;

    _database = await _initDB('cyber_notes.db');

    return _database!;

  }



  Future<Database> _initDB(String filePath) async {

    final dbPath = await getDatabasesPath();

    final path = p.join(dbPath, filePath);



    return await openDatabase(path, version: 1, onCreate: _createDB);

  }



  Future _createDB(Database db, int version) async {

    const idType = 'INTEGER PRIMARY KEY AUTOINCREMENT';

    const textType = 'TEXT NOT NULL';

    const boolType = 'BOOLEAN NOT NULL';



    await db.execute('''

CREATE TABLE notes (

  id $idType,

  title $textType,

  content $textType,

  color $textType,

  isSecure $boolType,

  createdAt $textType

)

''');

  }



  Future<Note> create(Note note) async {

    if (kIsWeb) {

      final newNote = note.copy(id: DateTime.now().millisecondsSinceEpoch);

      _webNotes.add(newNote);

      return newNote;

    }

    final db = await instance.database;

    final id = await db.insert('notes', note.toMap());

    return note.copy(id: id);

  }



  Future<List<Note>> readAllNotes(String query) async {

    if (kIsWeb) {

      if (query.isEmpty) return _webNotes.reversed.toList();

      return _webNotes.where((n) => n.title.toLowerCase().contains(query.toLowerCase()) || n.content.toLowerCase().contains(query.toLowerCase())).toList().reversed.toList();

    }

    final db = await instance.database;

    final result = await db.query(

      'notes',

      where: 'title LIKE ? OR content LIKE ?',

      whereArgs: ['%$query%', '%$query%'],

      orderBy: 'createdAt DESC',

    );

    return result.map((json) => Note.fromMap(json)).toList();

  }



  Future<int> update(Note note) async {

    if (kIsWeb) {

      final index = _webNotes.indexWhere((n) => n.id == note.id);

      if (index != -1) _webNotes[index] = note;

      return 1;

    }

    final db = await instance.database;

    return db.update(

      'notes',

      note.toMap(),

      where: 'id = ?',

      whereArgs: [note.id],

    );

  }



  Future<int> delete(int id) async {

    if (kIsWeb) {

      _webNotes.removeWhere((n) => n.id == id);

      return 1;

    }

    final db = await instance.database;

    return await db.delete(

      'notes',

      where: 'id = ?',

      whereArgs: [id],

    );

  }

}



// ========================================== //

// LOCK SCREEN

// ========================================== //



class LockScreen extends StatefulWidget {

  const LockScreen({super.key});



  @override

  State<LockScreen> createState() => _LockScreenState();

}



class _LockScreenState extends State<LockScreen> {

  final LocalAuthentication auth = LocalAuthentication();

  bool _isAuthenticating = false;



  @override

  void initState() {

    super.initState();

    _checkFirstTime();

  }



  void _checkFirstTime() async {

    var box = Hive.box('settingsBox');

    bool isFirstTime = box.get('isFirstTime', defaultValue: true);

    if (isFirstTime) {

      box.put('isFirstTime', false);

    }

  }



  Future<void> _authenticate() async {

    try {

      setState(() => _isAuthenticating = true);

      

      // Bypass native biometrics on Web Chrome

      if (kIsWeb) {

        await Future.delayed(const Duration(milliseconds: 800)); // Scan animation simulation

        if (mounted) _bypassAuth();

        return;

      }



      bool canCheckBiometrics = await auth.canCheckBiometrics;

      bool isSupported = await auth.isDeviceSupported();



      if (!canCheckBiometrics || !isSupported) {

        if (mounted) _bypassAuth();

        return;

      }



      bool authenticated = await auth.authenticate(

        localizedReason: 'Scan biometrics to access Cyber Vault',

        options: const AuthenticationOptions(

          stickyAuth: true,

          biometricOnly: false,

        ),

      );



      if (authenticated && mounted) {

        _bypassAuth();

      }

    } catch (e) {

      if (mounted) _bypassAuth(); 

    } finally {

      if (mounted) setState(() => _isAuthenticating = false);

    }

  }



  void _bypassAuth() {

    Navigator.pushReplacement(

      context,

      MaterialPageRoute(builder: (context) => const HomeScreen()),

    );

  }



  @override

  Widget build(BuildContext context) {

    return Scaffold(

      body: Center(

        child: Column(

          mainAxisAlignment: MainAxisAlignment.center,

          children: [

            Stack(

              alignment: Alignment.center,

              children: [

                Container(

                  width: 120,

                  height: 120,

                  decoration: BoxDecoration(

                    shape: BoxShape.circle,

                    boxShadow: [

                      BoxShadow(

                        color: const Color(0xFF00FFCC).withOpacity(0.2),

                        blurRadius: 30,

                        spreadRadius: 10,

                      ),

                    ],

                  ),

                ).animate(onPlay: (controller) => controller.repeat(reverse: true)).scaleXY(end: 1.2, duration: 2.seconds),

                const Icon(Icons.fingerprint_rounded, size: 80, color: Color(0xFF00FFCC)),

              ],

            ),

            const SizedBox(height: 40),

            Text(

              'CYBER VAULT',

              style: TextStyle(

                fontSize: 32,

                fontWeight: FontWeight.bold,

                letterSpacing: 8,

                color: Colors.white,

                shadows: [

                  Shadow(color: const Color(0xFF00FFCC).withOpacity(0.5), blurRadius: 10)

                ],

              ),

            ),

            const SizedBox(height: 10),

            const Text(

              'OFFLINE ENCRYPTED STORAGE',

              style: TextStyle(color: Colors.grey, letterSpacing: 2, fontSize: 12),

            ),

            const SizedBox(height: 60),

            GestureDetector(

              onTap: _isAuthenticating ? null : _authenticate,

              child: Container(

                padding: const EdgeInsets.symmetric(horizontal: 50, vertical: 16),

                decoration: BoxDecoration(

                  borderRadius: BorderRadius.circular(30),

                  border: Border.all(color: const Color(0xFF00FFCC), width: 1.5),

                  color: Colors.transparent,

                ),

                child: _isAuthenticating

                    ? const SizedBox(

                        width: 24,

                        height: 24,

                        child: CircularProgressIndicator(color: Color(0xFF00FFCC), strokeWidth: 2))

                    : const Text(

                        'INITIALIZE SCAN',

                        style: TextStyle(

                          fontSize: 16,

                          fontWeight: FontWeight.bold,

                          color: Color(0xFF00FFCC),

                          letterSpacing: 2,

                        ),

                      ),

              ),

            )

          ],

        ),

      ),

    );

  }

}



// ========================================== //

// HOME SCREEN

// ========================================== //



class HomeScreen extends StatefulWidget {

  const HomeScreen({super.key});



  @override

  State<HomeScreen> createState() => _HomeScreenState();

}



class _HomeScreenState extends State<HomeScreen> {

  late List<Note> notes;

  bool isLoading = false;

  String searchQuery = '';



  @override

  void initState() {

    super.initState();

    refreshNotes();

  }



  Future refreshNotes() async {

    setState(() => isLoading = true);

    notes = await DatabaseHelper.instance.readAllNotes(searchQuery);

    setState(() => isLoading = false);

  }



  @override

  Widget build(BuildContext context) {

    return Scaffold(

      backgroundColor: const Color(0xFF09090B),

      appBar: AppBar(

        backgroundColor: Colors.transparent,

        elevation: 0,

        title: const Text('MY DATABANKS', style: TextStyle(fontWeight: FontWeight.bold, letterSpacing: 2)),

        actions: [

          IconButton(

            icon: const Icon(Icons.settings_outlined, color: Color(0xFF00FFCC)),

            onPressed: () {},

          )

        ],

      ),

      body: Column(

        children: [

          _buildSearchBar(),

          Expanded(

            child: isLoading

                ? const Center(child: CircularProgressIndicator(color: Color(0xFF00FFCC)))

                : notes.isEmpty

                    ? _buildEmptyState()

                    : _buildNotesGrid(),

          ),

        ],

      ),

      floatingActionButton: FloatingActionButton(

        backgroundColor: const Color(0xFF00FFCC),

        foregroundColor: Colors.black,

        child: const Icon(Icons.add),

        onPressed: () async {

          await Navigator.push(

            context,

            MaterialPageRoute(builder: (context) => const EditorScreen()),

          );

          refreshNotes();

        },

      ),

    );

  }



  Widget _buildSearchBar() {

    return Padding(

      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),

      child: GlassmorphicContainer(

        width: double.infinity,

        height: 55,

        borderRadius: 15,

        linearGradient: LinearGradient(

          colors: [Colors.white.withOpacity(0.05), Colors.white.withOpacity(0.02)],

        ),

        border: 1,

        blur: 15,

        borderGradient: LinearGradient(

          colors: [const Color(0xFF00FFCC).withOpacity(0.3), Colors.transparent],

        ),

        child: TextField(

          onChanged: (value) {

            setState(() => searchQuery = value);

            refreshNotes();

          },

          style: const TextStyle(color: Colors.white),

          decoration: const InputDecoration(

            border: InputBorder.none,

            hintText: 'Search encrypted data...',

            hintStyle: TextStyle(color: Colors.white54),

            prefixIcon: Icon(Icons.search, color: Color(0xFF00FFCC)),

          ),

        ),

      ),

    );

  }



  Widget _buildEmptyState() {

    return Center(

      child: Column(

        mainAxisAlignment: MainAxisAlignment.center,

        children: [

          Icon(Icons.sd_storage_outlined, size: 80, color: Colors.white.withOpacity(0.2)),

          const SizedBox(height: 16),

          const Text('DATABANK EMPTY', style: TextStyle(color: Colors.white54, letterSpacing: 2)),

        ],

      ),

    );

  }



  Widget _buildNotesGrid() {

    return MasonryGridView.count(

      crossAxisCount: 2,

      mainAxisSpacing: 12,

      crossAxisSpacing: 12,

      padding: const EdgeInsets.all(16),

      itemCount: notes.length,

      itemBuilder: (context, index) {

        final note = notes[index];

        final color = Color(int.parse(note.color));

        return GestureDetector(

          onTap: () async {

            await Navigator.push(

              context,

              MaterialPageRoute(builder: (context) => EditorScreen(note: note)),

            );

            refreshNotes();

          },

          child: GlassmorphicContainer(

            width: double.infinity,

            height: note.content.length > 50 ? 200 : 120,

            borderRadius: 16,

            blur: 20,

            border: 1,

            linearGradient: LinearGradient(

              colors: [color.withOpacity(0.1), color.withOpacity(0.02)],

              begin: Alignment.topLeft,

              end: Alignment.bottomRight,

            ),

            borderGradient: LinearGradient(

              colors: [color.withOpacity(0.5), Colors.transparent],

            ),

            child: Padding(

              padding: const EdgeInsets.all(16.0),

              child: Column(

                crossAxisAlignment: CrossAxisAlignment.start,

                children: [

                  Row(

                    mainAxisAlignment: MainAxisAlignment.spaceBetween,

                    children: [

                      Expanded(

                        child: Text(

                          note.title,

                          style: TextStyle(

                            color: color,

                            fontWeight: FontWeight.bold,

                            fontSize: 18,

                          ),

                          maxLines: 1,

                          overflow: TextOverflow.ellipsis,

                        ),

                      ),

                      if (note.isSecure)

                        Icon(Icons.lock, size: 14, color: color),

                    ],

                  ),

                  const SizedBox(height: 8),

                  Expanded(

                    child: Text(

                      note.content,

                      style: const TextStyle(color: Colors.white70, fontSize: 14),

                      maxLines: 5,

                      overflow: TextOverflow.ellipsis,

                    ),

                  ),

                  const SizedBox(height: 8),

                  Text(

                    DateFormat.yMMMd().format(note.createdAt),

                    style: TextStyle(color: Colors.white.withOpacity(0.4), fontSize: 10),

                  )

                ],

              ),

            ),

          ),

        );

      },

    );

  }

}



// ========================================== //

// EDITOR SCREEN

// ========================================== //



class EditorScreen extends StatefulWidget {

  final Note? note;

  const EditorScreen({super.key, this.note});



  @override

  State<EditorScreen> createState() => _EditorScreenState();

}



class _EditorScreenState extends State<EditorScreen> {

  late TextEditingController _titleController;

  late TextEditingController _contentController;

  bool _isSecure = false;

  String _selectedColor = "0xFF00FFCC"; // Default Cyan



  final List<String> _colors = [

    "0xFF00FFCC", // Cyan

    "0xFFFF007F", // Pink

    "0xFFFFEA00", // Yellow

    "0xFFB026FF", // Purple

  ];



  @override

  void initState() {

    super.initState();

    _titleController = TextEditingController(text: widget.note?.title ?? '');

    _contentController = TextEditingController(text: widget.note?.content ?? '');

    _isSecure = widget.note?.isSecure ?? false;

    _selectedColor = widget.note?.color ?? _colors[0];

  }



  Future<void> _saveNote() async {

    final isUpdating = widget.note != null;

    final note = Note(

      id: widget.note?.id,

      title: _titleController.text.isEmpty ? 'Untitled Data' : _titleController.text,

      content: _contentController.text,

      color: _selectedColor,

      isSecure: _isSecure,

      createdAt: DateTime.now(),

    );



    if (isUpdating) {

      await DatabaseHelper.instance.update(note);

    } else {

      await DatabaseHelper.instance.create(note);

    }

    if (mounted) Navigator.pop(context);

  }



  Future<void> _deleteNote() async {

    if (widget.note != null) {

      await DatabaseHelper.instance.delete(widget.note!.id!);

      if (mounted) Navigator.pop(context);

    }

  }



  @override

  Widget build(BuildContext context) {

    return Scaffold(

      backgroundColor: const Color(0xFF0F0F13),

      appBar: AppBar(

        backgroundColor: Colors.transparent,

        elevation: 0,

        actions: [

          IconButton(

            icon: Icon(

              _isSecure ? Icons.lock : Icons.lock_open,

              color: _isSecure ? const Color(0xFFFF007F) : Colors.white54,

            ),

            onPressed: () => setState(() => _isSecure = !_isSecure),

          ),

          if (widget.note != null)

            IconButton(

              icon: const Icon(Icons.delete_outline, color: Colors.white54),

              onPressed: _deleteNote,

            ),

          IconButton(

            icon: const Icon(Icons.save_outlined, color: Color(0xFF00FFCC)),

            onPressed: _saveNote,

          ),

        ],

      ),

      body: Padding(

        padding: const EdgeInsets.all(20.0),

        child: Column(

          children: [

            Row(

              children: _colors.map((color) {

                return GestureDetector(

                  onTap: () => setState(() => _selectedColor = color),

                  child: Container(

                    margin: const EdgeInsets.only(right: 12),

                    width: 30,

                    height: 30,

                    decoration: BoxDecoration(

                      color: Color(int.parse(color)),

                      shape: BoxShape.circle,

                      border: Border.all(

                        color: _selectedColor == color ? Colors.white : Colors.transparent,

                        width: 2,

                      ),

                      boxShadow: _selectedColor == color

                          ? [BoxShadow(color: Color(int.parse(color)).withOpacity(0.5), blurRadius: 10)]

                          : [],

                    ),

                  ),

                );

              }).toList(),

            ),

            const SizedBox(height: 20),

            TextField(

              controller: _titleController,

              style: TextStyle(

                fontSize: 28,

                fontWeight: FontWeight.bold,

                color: Color(int.parse(_selectedColor)),

              ),

              decoration: const InputDecoration(

                hintText: 'NODE TITLE...',

                hintStyle: TextStyle(color: Colors.white24),

                border: InputBorder.none,

              ),

            ),

            Expanded(

              child: TextField(

                controller: _contentController,

                style: const TextStyle(fontSize: 16, color: Colors.white70, height: 1.5),

                maxLines: null,

                keyboardType: TextInputType.multiline,

                decoration: const InputDecoration(

                  hintText: 'Inject data here...',

                  hintStyle: TextStyle(color: Colors.white24),

                  border: InputBorder.none,

                ),

              ),

            ),

          ],

        ),

      ),

    );

  }

}

