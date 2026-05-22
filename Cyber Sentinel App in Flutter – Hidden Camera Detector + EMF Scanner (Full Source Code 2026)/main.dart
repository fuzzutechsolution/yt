import 'dart:async';

import 'dart:math' as math;

import 'package:flutter/foundation.dart' show kIsWeb; // Add this

import 'package:flutter/material.dart';

import 'package:flutter/services.dart';

import 'package:google_fonts/google_fonts.dart';

import 'package:sensors_plus/sensors_plus.dart';

import 'package:vibration/vibration.dart';

import 'package:flutter_animate/flutter_animate.dart';

import 'package:camera/camera.dart';



// -----------------------------------------------------------------------------

// GLOBAL VARS & MAIN

// -----------------------------------------------------------------------------

List<CameraDescription> _cameras = [];



Future<void> main() async {

  WidgetsFlutterBinding.ensureInitialized();

  try {

    _cameras = await availableCameras();

  } catch (e) {

    debugPrint("Camera error: $e");

  }

  SystemChrome.setEnabledSystemUIMode(SystemUiMode.immersiveSticky);

  runApp(const CyberSentinelApp());

}



class CyberSentinelApp extends StatelessWidget {

  const CyberSentinelApp({super.key});



  @override

  Widget build(BuildContext context) {

    return MaterialApp(

      debugShowCheckedModeBanner: false,

      title: 'CyberSentinel',

      theme: ThemeData.dark().copyWith(

        scaffoldBackgroundColor: const Color(0xFF050505),

        primaryColor: const Color(0xFF00FFC2),

        textTheme: GoogleFonts.rajdhaniTextTheme(ThemeData.dark().textTheme),

        colorScheme: const ColorScheme.dark(

          primary: Color(0xFF00FFC2),

          secondary: Color(0xFFFF0055),

          surface: Color(0xFF101010),

        ),

      ),

      home: const MainScannerScreen(),

    );

  }

}



// -----------------------------------------------------------------------------

// MAIN SCANNER SCREEN

// -----------------------------------------------------------------------------

class MainScannerScreen extends StatefulWidget {

  const MainScannerScreen({super.key});



  @override

  State<MainScannerScreen> createState() => _MainScannerScreenState();

}



class _MainScannerScreenState extends State<MainScannerScreen>

    with TickerProviderStateMixin {

  // Sensor Data

  double _magnitude = 0.0;

  List<double> _history = List.filled(100, 0.0);

  StreamSubscription<MagnetometerEvent>? _subscription;

  

  // Detection Status

  bool _isHighAlert = false;

  String _statusText = "SEARCHING...";

  Color _statusColor = const Color(0xFF00FFC2);



  // Mode: 0 = EMF Scanner, 1 = IR Vision (Mock)

  int _modeIndex = 0;

  CameraController? _cameraController;



  late AnimationController _pulseController;

  late AnimationController _radarController;



  @override

  void initState() {

    super.initState();

    _initSensors();

    _initControllers();

  }



  void _initSensors() {

    _subscription = magnetometerEvents.listen((MagnetometerEvent event) {

      double mag = math.sqrt(event.x * event.x + event.y * event.y + event.z * event.z);

      // Normalized roughly usually ~40-50uT is background

      setState(() {

        _magnitude = mag;

        _history.removeAt(0);

        _history.add(mag);

      });

      _analyzeData(mag);

    });

  }



  void _initControllers() {

    _pulseController = AnimationController(

      vsync: this,

      duration: const Duration(seconds: 1),

    )..repeat(reverse: true);



    _radarController = AnimationController(

        vsync: this, duration: const Duration(seconds: 4))

      ..repeat();

  }



  void _initCamera() {

    if (_cameras.isEmpty) return;

    _cameraController = CameraController(

        _cameras[0], ResolutionPreset.medium, enableAudio: false);

    _cameraController!.initialize().then((_) {

      if (!mounted) return;

      setState(() {});

    });

  }



  Future<void> _analyzeData(double val) async {

    if (val > 80.0) { // Threshold for "High" magnetic field

      if (!_isHighAlert) {

        setState(() {

          _isHighAlert = true;

          _statusText = "ANOMALY DETECTED";

          _statusColor = const Color(0xFFFF0055);

        });



        // Safety check for vibration

        try {

          if (!kIsWeb && (await Vibration.hasVibrator() ?? false)) {

             Vibration.vibrate(duration: 200, amplitude: 255);

          }

        } catch (e) {

          debugPrint("Vibration not supported: $e");

        }

      }

    } else {

      if (_isHighAlert) {

        setState(() {

          _isHighAlert = false;

          _statusText = "SCANNING AREA";

          _statusColor = const Color(0xFF00FFC2);

        });

      }

    }

  }



  @override

  void dispose() {

    _subscription?.cancel();

    _pulseController.dispose();

    _radarController.dispose();

    _cameraController?.dispose();

    super.dispose();

  }



  // ---------------------------------------------------------------------------

  // UI BUILD

  // ---------------------------------------------------------------------------

  @override

  Widget build(BuildContext context) {

    return Scaffold(

      body: Stack(

        children: [

          // BACKGROUND LAYER

          Positioned.fill(

            child: _modeIndex == 1 && _cameraController != null && _cameraController!.value.isInitialized

                ? ColorFiltered(

                    colorFilter: const ColorFilter.mode(

                        Colors.redAccent, BlendMode.modulate), // IR Effect

                    child: Transform.scale(

                      scale: 1.2,

                      child: CameraPreview(_cameraController!),

                    ),

                  )

                : Container(

                    decoration: const BoxDecoration(

                      gradient: RadialGradient(

                        colors: [Color(0xFF0D1F2D), Colors.black],

                        radius: 1.2,

                        center: Alignment.center,

                      ),

                    ),

                    child: CustomPaint(

                      painter: GridPainter(),

                    ),

                  ),

          ),



          // CONTENT LAYER

          SafeArea(

            child: Column(

              children: [

                _buildTopBar(),

                Expanded(

                  child: _modeIndex == 0 ? _buildEMFScanner() : _buildIRScanner(),

                ),

                _buildBottomControls(),

              ],

            ),

          ),



          // VIGNETTE OVERLAY for Cyberpunk feel

          IgnorePointer(

            child: Container(

              decoration: BoxDecoration(

                gradient: RadialGradient(

                  colors: [Colors.transparent, Colors.black.withOpacity(0.8)],

                  radius: 1.0,

                  stops: const [0.7, 1.0],

                ),

              ),

            ),

          ),

        ],

      ),

    );

  }



  Widget _buildTopBar() {

    return Container(

      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),

      child: Row(

        mainAxisAlignment: MainAxisAlignment.spaceBetween,

        children: [

          Row(

            children: [

              Icon(Icons.shield_outlined, color: _statusColor, size: 28)

                  .animate(onPlay: (c) => c.repeat())

                  .shimmer(duration: 2000.ms, color: Colors.white),

              const SizedBox(width: 10),

              GestureDetector(

                onTap: () {

                  // DEMO MODE for Viral Video Recording

                  setState(() {

                    _magnitude = 120.0 + (math.Random().nextDouble() * 20); // Fake high value

                  });

                  _analyzeData(_magnitude);

                  

                  Future.delayed(const Duration(milliseconds: 500), () {

                     setState(() {

                       _magnitude = 45.0; // Return to normal

                     });

                     _analyzeData(_magnitude);

                  });

                },

                child: Text(

                  "CYBER SENTINEL",

                  style: GoogleFonts.orbitron(

                    fontSize: 18,

                    fontWeight: FontWeight.bold,

                    letterSpacing: 2,

                    color: Colors.white,

                  ),

                ),

              ),

            ],

          ),

          Container(

            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),

            decoration: BoxDecoration(

              border: Border.all(color: _statusColor.withOpacity(0.5)),

              borderRadius: BorderRadius.circular(4),

              color: _statusColor.withOpacity(0.1),

            ),

            child: Text(

              _statusText,

              style: TextStyle(

                  color: _statusColor, fontSize: 12, fontWeight: FontWeight.bold),

            ),

          ),

        ],

      ),

    );

  }



  Widget _buildEMFScanner() {

    return Column(

      mainAxisAlignment: MainAxisAlignment.center,

      children: [

        // RADAR / GAUGE

        Stack(

          alignment: Alignment.center,

          children: [

            // Rotating Radar

            RotationTransition(

              turns: _radarController,

              child: Container(

                width: 280,

                height: 280,

                decoration: BoxDecoration(

                  shape: BoxShape.circle,

                  gradient: SweepGradient(

                    colors: [

                      Colors.transparent,

                      _statusColor.withOpacity(0.1),

                      _statusColor.withOpacity(0.5),

                    ],

                    stops: const [0.5, 0.9, 1.0],

                  ),

                ),

              ),

            ),

            // Outer Ring

            Container(

              width: 300,

              height: 300,

              decoration: BoxDecoration(

                shape: BoxShape.circle,

                border: Border.all(color: Colors.white12, width: 2),

              ),

            ),

            // Inner Core

            AnimatedContainer(

              duration: const Duration(milliseconds: 200),

              width: 150 + (_magnitude - 40).clamp(0, 50),

              height: 150 + (_magnitude - 40).clamp(0, 50),

              decoration: BoxDecoration(

                shape: BoxShape.circle,

                color: _statusColor.withOpacity(0.1),

                boxShadow: [

                  BoxShadow(

                    color: _statusColor.withOpacity(0.4),

                    blurRadius: 30,

                    spreadRadius: 5,

                  )

                ],

              ),

              child: Center(

                child: Column(

                  mainAxisSize: MainAxisSize.min,

                  children: [

                    Text(

                      _magnitude.toStringAsFixed(1),

                      style: GoogleFonts.rajdhani(

                        fontSize: 48,

                        fontWeight: FontWeight.bold,

                        color: Colors.white,

                      ),

                    ),

                    Text(

                      "µT",

                      style: GoogleFonts.rajdhani(

                        fontSize: 14,

                        color: Colors.white54,

                      ),

                    ),

                  ],

                ),

              ),

            ),

          ],

        ),

        const SizedBox(height: 40),

        // GRAPH

        SizedBox(

          height: 100,

          width: double.infinity,

          child: CustomPaint(

            painter: GraphPainter(_history, _statusColor),

          ),

        ),

      ],

    );

  }



  Widget _buildIRScanner() {

    return Center(

      child: Column(

        mainAxisAlignment: MainAxisAlignment.center,

        children: [

          Container(

            width: 250,

            height: 250,

            decoration: BoxDecoration(

              border: Border.all(color: Colors.redAccent.withOpacity(0.5), width: 2),

            ),

            child: Stack(

              children: [

                // Crosshair

                Center(

                  child: Container(width: 20, height: 1, color: Colors.red),

                ),

                Center(

                  child: Container(width: 1, height: 20, color: Colors.red),

                ),

                // Corner Brackets

                const Align(alignment: Alignment.topLeft, child: Icon(Icons.crop_free, color: Colors.red)),

                const Align(alignment: Alignment.topRight, child: Icon(Icons.crop_free, color: Colors.red)),

                const Align(alignment: Alignment.bottomLeft, child: Icon(Icons.crop_free, color: Colors.red)),

                const Align(alignment: Alignment.bottomRight, child: Icon(Icons.crop_free, color: Colors.red)),

              ],

            ),

          ),

          const SizedBox(height: 20),

          Text(

            "IR VISION ACTIVE\nLOOK For GLINTING LENSES",

            textAlign: TextAlign.center,

            style: GoogleFonts.orbitron(color: Colors.redAccent, letterSpacing: 1),

          )

              .animate(onPlay: (c) => c.repeat(reverse: true))

              .fadeIn(duration: 500.ms),

        ],

      ),

    );

  }



  Widget _buildBottomControls() {

    return Container(

      padding: const EdgeInsets.all(20),

      child: Row(

        mainAxisAlignment: MainAxisAlignment.spaceEvenly,

        children: [

          _buildModeBtn(

            label: "EMF SCAN",

            icon: Icons.wifi_tethering,

            isSelected: _modeIndex == 0,

            onTap: () {

              setState(() {

                _modeIndex = 0;

                _cameraController?.dispose();

                _cameraController = null;

              });

            },

          ),

          _buildModeBtn(

            label: "IR VISION",

            icon: Icons.visibility,

            isSelected: _modeIndex == 1,

            onTap: () {

              setState(() {

                _modeIndex = 1;

              });

              _initCamera();

            },

          ),

        ],

      ),

    );

  }



  Widget _buildModeBtn({

    required String label,

    required IconData icon,

    required bool isSelected,

    required VoidCallback onTap,

  }) {

    return GestureDetector(

      onTap: onTap,

      child: AnimatedContainer(

        duration: const Duration(milliseconds: 300),

        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),

        decoration: BoxDecoration(

          color: isSelected ? _statusColor.withOpacity(0.2) : Colors.transparent,

          border: Border.all(

            color: isSelected ? _statusColor : Colors.white24,

            width: 1.5,

          ),

          borderRadius: BorderRadius.circular(8),

          boxShadow: isSelected

              ? [BoxShadow(color: _statusColor.withOpacity(0.3), blurRadius: 10)]

              : [],

        ),

        child: Column(

          children: [

            Icon(icon, color: isSelected ? Colors.white : Colors.white54),

            const SizedBox(height: 5),

            Text(

              label,

              style: GoogleFonts.rajdhani(

                color: isSelected ? Colors.white : Colors.white54,

                fontWeight: FontWeight.bold,

              ),

            ),

          ],

        ),

      ),

    );

  }

}



// -----------------------------------------------------------------------------

// PAINTERS

// -----------------------------------------------------------------------------

class GridPainter extends CustomPainter {

  @override

  void paint(Canvas canvas, Size size) {

    final paint = Paint()

      ..color = Colors.white.withOpacity(0.05)

      ..strokeWidth = 1;



    // Horizontal Lines

    for (double i = 0; i < size.height; i += 40) {

      canvas.drawLine(Offset(0, i), Offset(size.width, i), paint);

    }

    // Vertical Lines

    for (double i = 0; i < size.width; i += 40) {

      canvas.drawLine(Offset(i, 0), Offset(i, size.height), paint);

    }

  }



  @override

  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;

}



class GraphPainter extends CustomPainter {

  final List<double> history;

  final Color color;



  GraphPainter(this.history, this.color);



  @override

  void paint(Canvas canvas, Size size) {

    final paint = Paint()

      ..color = color

      ..strokeWidth = 2

      ..style = PaintingStyle.stroke;



    final path = Path();

    final widthStep = size.width / (history.length - 1);



    for (int i = 0; i < history.length; i++) {

      // Normalize: assume max 150uT for graph height

      final normalizedH = (history[i] / 150).clamp(0.0, 1.0);

      final y = size.height - (normalizedH * size.height);

      final x = i * widthStep;



      if (i == 0) {

        path.moveTo(x, y);

      } else {

        path.lineTo(x, y);

      }

    }

    canvas.drawPath(path, paint);



    // Glow under graph

    final fillPaint = Paint()

      ..shader = LinearGradient(

        colors: [color.withOpacity(0.3), Colors.transparent],

        begin: Alignment.topCenter,

        end: Alignment.bottomCenter,

      ).createShader(Rect.fromLTWH(0, 0, size.width, size.height))

      ..style = PaintingStyle.fill;



    path.lineTo(size.width, size.height);

    path.lineTo(0, size.height);

    path.close();

    canvas.drawPath(path, fillPaint);

  }



  @override

  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;

}

