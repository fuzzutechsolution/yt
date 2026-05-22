import 'dart:async';

import 'dart:math';

import 'package:flutter/material.dart';



void main() {

  runApp(const CyberGestureApp());

}



class CyberGestureApp extends StatelessWidget {

  const CyberGestureApp({super.key});



  @override

  Widget build(BuildContext context) {

    return MaterialApp(

      title: 'Project Antigravity // CyberGesture',

      debugShowCheckedModeBanner: false,

      theme: ThemeData(

        brightness: Brightness.dark,

        primaryColor: const Color(0xFF00FF9D),

        scaffoldBackgroundColor: const Color(0xFF0A0A0C),

        fontFamily: 'Courier',

      ),

      home: const CyberHUD(),

    );

  }

}



class CyberHUD extends StatefulWidget {

  const CyberHUD({super.key});



  @override

  State<CyberHUD> createState() => _CyberHUDState();

}



class _CyberHUDState extends State<CyberHUD> with TickerProviderStateMixin {

  String _currentStatus = "CALIBRATING SENSORS...";

  double _scanningLineY = 0.0;

  late AnimationController _scanController;

  late AnimationController _pulseController;

  List<Offset> _aiNodes = [];

  Timer? _timer;

  

  // Simulated AI Logic values

  final Random _rnd = Random();

  String _detectedGesture = "AWAITING INPUT";

  Color _statusColor = const Color(0xFF00F0FF);



  @override

  void initState() {

    super.initState();

    // Scanner Animation

    _scanController = AnimationController(vsync: this, duration: const Duration(seconds: 2))..repeat(reverse: true);

    _scanController.addListener(() {

      setState(() {

        _scanningLineY = _scanController.value * MediaQuery.of(context).size.height;

      });

    });



    // Pulse Animation

    _pulseController = AnimationController(vsync: this, duration: const Duration(milliseconds: 800))..repeat(reverse: true);



    // Simulate AI Nodes

    _timer = Timer.periodic(const Duration(milliseconds: 500), (timer) {

      if (mounted) {

        setState(() {

          _aiNodes.clear();

          for (int i = 0; i < 5; i++) {

            _aiNodes.add(Offset(_rnd.nextDouble() * 300 + 50, _rnd.nextDouble() * 500 + 100));

          }

          if (_currentStatus == "CALIBRATING SENSORS...") {

            _currentStatus = "SYSTEM ONLINE // AI ACTIVE";

          }

        });

      }

    });

  }



  @override

  void dispose() {

    _scanController.dispose();

    _pulseController.dispose();

    _timer?.cancel();

    super.dispose();

  }



  void _triggerGesture(String gesture, Color color) {

    setState(() {

      _detectedGesture = "GESTURE: $gesture";

      _statusColor = color;

    });

    // Reset after 2 seconds

    Future.delayed(const Duration(seconds: 2), () {

      if (mounted) {

        setState(() {

          _detectedGesture = "AWAITING INPUT";

          _statusColor = const Color(0xFF00F0FF);

        });

      }

    });

  }



  @override

  Widget build(BuildContext context) {

    return Scaffold(

      body: GestureDetector(

        // Simulating gesture detection via swipes & taps purely for cinematic UI effect

        onPanUpdate: (details) {

          if (details.delta.dx > 10) _triggerGesture("SWIPE RIGHT // NEXT", const Color(0xFF00FF9D));

          if (details.delta.dx < -10) _triggerGesture("SWIPE LEFT // BACK", const Color(0xFFFF007F));

          if (details.delta.dy < -10) _triggerGesture("OPEN PALM // STOP", const Color(0xFFFFCC00));

        },

        onDoubleTap: () => _triggerGesture("THUMBS UP // CONFIRM", const Color(0xFF00FF9D)),

        child: Stack(

          children: [

            // Background Grid (Matrix aesthetic)

            CustomPaint(

              size: MediaQuery.of(context).size,

              painter: CyberGridPainter(),

            ),

            

            // Simulated Camera Bounding Boxes

            ..._aiNodes.map((node) => Positioned(

              left: node.dx,

              top: node.dy,

              child: AnimatedBuilder(

                animation: _pulseController,

                builder: (context, child) {

                  return Container(

                    width: 30,

                    height: 30,

                    decoration: BoxDecoration(

                      border: Border.all(color: const Color(0xFF00FF9D).withOpacity(_pulseController.value), width: 2),

                      shape: BoxShape.rectangle,

                    ),

                    child: Center(

                      child: Container(

                        width: 4, height: 4, color: const Color(0xFFFF007F),

                      ),

                    ),

                  );

                }

              ),

            )),



            // Scanning Line

            Positioned(

              top: _scanningLineY,

              left: 0, right: 0,

              child: Container(

                height: 2,

                decoration: BoxDecoration(

                  boxShadow: [BoxShadow(color: const Color(0xFF00F0FF), blurRadius: 10, spreadRadius: 2)],

                  color: const Color(0xFF00F0FF),

                ),

              ),

            ),



            // Top HUD

            Positioned(

              top: 50, left: 20, right: 20,

              child: Container(

                padding: const EdgeInsets.all(15),

                decoration: BoxDecoration(

                  color: Colors.black.withOpacity(0.5),

                  border: Border.all(color: _statusColor, width: 1),

                  borderRadius: BorderRadius.circular(10),

                ),

                child: Column(

                  crossAxisAlignment: CrossAxisAlignment.start,

                  children: [

                    Text("NODE: ALPHA-7", style: TextStyle(color: _statusColor, fontWeight: FontWeight.bold)),

                    const SizedBox(height: 5),

                    Text(_currentStatus, style: const TextStyle(color: Colors.white, fontSize: 12)),

                  ],

                ),

              ),

            ),



            // Center Dynamic Detection Widget

            Center(

              child: AnimatedDefaultTextStyle(

                duration: const Duration(milliseconds: 300),

                style: TextStyle(

                  fontSize: _detectedGesture != "AWAITING INPUT" ? 28 : 18,

                  fontWeight: FontWeight.bold,

                  color: _statusColor,

                  letterSpacing: 2,

                  shadows: [Shadow(color: _statusColor, blurRadius: 10)],

                ),

                child: Text(_detectedGesture),

              ),

            ),



            // Bottom HUD

            Positioned(

              bottom: 40, left: 20, right: 20,

              child: Row(

                mainAxisAlignment: MainAxisAlignment.spaceBetween,

                children: [

                  _buildHudBox("HAND", "SEARCHING"),

                  _buildHudBox("CONFIDENCE", "${(80 + _rnd.nextInt(19))}%"),

                  _buildHudBox("LATENCY", "12ms"),

                ],

              ),

            ),

          ],

        ),

      ),

    );

  }



  Widget _buildHudBox(String title, String val) {

    return Container(

      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),

      decoration: BoxDecoration(

        border: Border(left: BorderSide(color: const Color(0xFFFF007F), width: 3)),

        color: Colors.white.withOpacity(0.05),

      ),

      child: Column(

        crossAxisAlignment: CrossAxisAlignment.start,

        children: [

          Text(title, style: const TextStyle(color: Colors.grey, fontSize: 10)),

          const SizedBox(height: 2),

          Text(val, style: const TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold)),

        ],

      ),

    );

  }

}



class CyberGridPainter extends CustomPainter {

  @override

  void paint(Canvas canvas, Size size) {

    var paint = Paint()

      ..color = const Color(0xFF00F0FF).withOpacity(0.05)

      ..strokeWidth = 1.0;

    

    for (double i = 0; i < size.width; i += 40) {

      canvas.drawLine(Offset(i, 0), Offset(i, size.height), paint);

    }

    for (double i = 0; i < size.height; i += 40) {

      canvas.drawLine(Offset(0, i), Offset(size.width, i), paint);

    }

  }



  @override

  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;

}

