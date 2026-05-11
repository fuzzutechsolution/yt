import 'dart:async';
import 'dart:math';
import 'dart:ui';

import 'package:flutter/material.dart';

void main() {
  runApp(const FuzzuWeatherApp());
}

class FuzzuWeatherApp extends StatelessWidget {
  const FuzzuWeatherApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'FuzzuTech Weather',
      theme: ThemeData(
        brightness: Brightness.dark,
        fontFamily: 'Roboto',
        scaffoldBackgroundColor: Colors.black,
      ),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage>
    with TickerProviderStateMixin {
  late AnimationController glowController;
  late AnimationController floatController;
  late AnimationController rotateController;

  late Animation<double> glowAnimation;
  late Animation<double> floatAnimation;

  final List<ParticleModel> particles = [];

  @override
  void initState() {
    super.initState();

    glowController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat(reverse: true);

    floatController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 4),
    )..repeat(reverse: true);

    rotateController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 20),
    )..repeat();

    glowAnimation = Tween<double>(
      begin: 0.3,
      end: 1,
    ).animate(glowController);

    floatAnimation = Tween<double>(
      begin: -12,
      end: 12,
    ).animate(
      CurvedAnimation(
        parent: floatController,
        curve: Curves.easeInOut,
      ),
    );

    generateParticles();
  }

  void generateParticles() {
    for (int i = 0; i < 40; i++) {
      particles.add(
        ParticleModel(
          x: Random().nextDouble(),
          y: Random().nextDouble(),
          size: Random().nextDouble() * 5 + 2,
          speed: Random().nextDouble() * 0.003 + 0.001,
        ),
      );
    }

    Timer.periodic(const Duration(milliseconds: 16), (timer) {
      for (var p in particles) {
        p.y -= p.speed;

        if (p.y < 0) {
          p.y = 1;
          p.x = Random().nextDouble();
        }
      }

      if (mounted) {
        setState(() {});
      }
    });
  }

  @override
  void dispose() {
    glowController.dispose();
    floatController.dispose();
    rotateController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;

    return Scaffold(
      body: Stack(
        children: [
          /// BACKGROUND
          Container(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  Color(0xff050816),
                  Color(0xff0B1026),
                  Color(0xff130F40),
                  Color(0xff1F1C4D),
                ],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
            ),
          ),

          /// ROTATING GLOW
          Center(
            child: RotationTransition(
              turns: rotateController,
              child: Container(
                width: 380,
                height: 380,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: RadialGradient(
                    colors: [
                      Colors.cyan.withOpacity(0.4),
                      Colors.transparent,
                    ],
                  ),
                ),
              ),
            ),
          ),

          /// PARTICLES
          ...particles.map(
            (p) => Positioned(
              left: p.x * size.width,
              top: p.y * size.height,
              child: Container(
                width: p.size,
                height: p.size,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: Colors.white.withOpacity(0.7),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.cyan.withOpacity(0.8),
                      blurRadius: 10,
                    ),
                  ],
                ),
              ),
            ),
          ),

          /// MAIN CONTENT
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  /// TOP BAR
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Icon(
                        Icons.menu_rounded,
                        size: 30,
                        color: Colors.white,
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 18,
                          vertical: 10,
                        ),
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(30),
                          color: Colors.white.withOpacity(0.08),
                          border: Border.all(
                            color: Colors.cyanAccent.withOpacity(0.5),
                          ),
                        ),
                        child: const Row(
                          children: [
                            Icon(
                              Icons.location_on,
                              color: Colors.cyanAccent,
                              size: 18,
                            ),
                            SizedBox(width: 6),
                            Text(
                              "Mumbai",
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 40),

                  /// GLASS CARD
                  Expanded(
                    child: Center(
                      child: AnimatedBuilder(
                        animation: glowAnimation,
                        builder: (context, child) {
                          return Transform.translate(
                            offset: Offset(
                              0,
                              floatAnimation.value,
                            ),
                            child: Container(
                              width: double.infinity,
                              constraints: const BoxConstraints(
                                maxWidth: 360,
                              ),
                              padding: const EdgeInsets.all(25),
                              decoration: BoxDecoration(
                                borderRadius: BorderRadius.circular(40),
                                border: Border.all(
                                  color: Colors.cyanAccent.withOpacity(
                                    glowAnimation.value,
                                  ),
                                  width: 2,
                                ),
                                gradient: LinearGradient(
                                  colors: [
                                    Colors.white.withOpacity(0.12),
                                    Colors.white.withOpacity(0.04),
                                  ],
                                  begin: Alignment.topLeft,
                                  end: Alignment.bottomRight,
                                ),
                                boxShadow: [
                                  BoxShadow(
                                    color: Colors.cyanAccent.withOpacity(
                                      glowAnimation.value * 0.6,
                                    ),
                                    blurRadius: 35,
                                    spreadRadius: 3,
                                  ),
                                ],
                              ),
                              child: ClipRRect(
                                borderRadius: BorderRadius.circular(40),
                                child: BackdropFilter(
                                  filter: ImageFilter.blur(
                                    sigmaX: 18,
                                    sigmaY: 18,
                                  ),
                                  child: Column(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      const SizedBox(height: 10),

                                      /// WEATHER ICON
                                      TweenAnimationBuilder(
                                        tween: Tween<double>(
                                          begin: 0.9,
                                          end: 1.05,
                                        ),
                                        duration: const Duration(seconds: 2),
                                        curve: Curves.easeInOut,
                                        builder:
                                            (context, double value, child) {
                                          return Transform.scale(
                                            scale: value,
                                            child: ShaderMask(
                                              shaderCallback: (bounds) {
                                                return const LinearGradient(
                                                  colors: [
                                                    Colors.cyanAccent,
                                                    Colors.purpleAccent,
                                                  ],
                                                ).createShader(bounds);
                                              },
                                              child: const Icon(
                                                Icons.thunderstorm_rounded,
                                                size: 150,
                                                color: Colors.white,
                                              ),
                                            ),
                                          );
                                        },
                                      ),

                                      const SizedBox(height: 10),

                                      /// TEMP
                                      ShaderMask(
                                        shaderCallback: (bounds) {
                                          return const LinearGradient(
                                            colors: [
                                              Colors.cyanAccent,
                                              Colors.white,
                                            ],
                                          ).createShader(bounds);
                                        },
                                        child: const Text(
                                          "26°C",
                                          style: TextStyle(
                                            fontSize: 72,
                                            fontWeight: FontWeight.bold,
                                            color: Colors.white,
                                          ),
                                        ),
                                      ),

                                      const SizedBox(height: 10),

                                      const Text(
                                        "Thunder Storm",
                                        style: TextStyle(
                                          fontSize: 22,
                                          color: Colors.white70,
                                          fontWeight: FontWeight.w500,
                                        ),
                                      ),

                                      const SizedBox(height: 8),

                                      Text(
                                        "Tuesday • 12 May 2026",
                                        style: TextStyle(
                                          color: Colors.white.withOpacity(0.6),
                                        ),
                                      ),

                                      const SizedBox(height: 35),

                                      /// INFO ROW
                                      Row(
                                        mainAxisAlignment:
                                            MainAxisAlignment.spaceBetween,
                                        children: [
                                          weatherInfo(
                                            Icons.air,
                                            "Wind",
                                            "18 km/h",
                                          ),
                                          weatherInfo(
                                            Icons.water_drop,
                                            "Humidity",
                                            "82%",
                                          ),
                                          weatherInfo(
                                            Icons.visibility,
                                            "Visibility",
                                            "6 km",
                                          ),
                                        ],
                                      ),

                                      const SizedBox(height: 35),

                                      /// BUTTON
                                      GestureDetector(
                                        onTap: () {},
                                        child: Container(
                                          width: double.infinity,
                                          padding:
                                              const EdgeInsets.symmetric(
                                            vertical: 18,
                                          ),
                                          decoration: BoxDecoration(
                                            borderRadius:
                                                BorderRadius.circular(30),
                                            gradient: const LinearGradient(
                                              colors: [
                                                Colors.cyanAccent,
                                                Colors.purpleAccent,
                                              ],
                                            ),
                                            boxShadow: [
                                              BoxShadow(
                                                color: Colors.cyanAccent
                                                    .withOpacity(0.6),
                                                blurRadius: 25,
                                              ),
                                            ],
                                          ),
                                          child: const Center(
                                            child: Text(
                                              "View Forecast",
                                              style: TextStyle(
                                                color: Colors.black,
                                                fontWeight: FontWeight.bold,
                                                fontSize: 18,
                                              ),
                                            ),
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ),
                          );
                        },
                      ),
                    ),
                  ),

                  const SizedBox(height: 20),

                  /// BOTTOM TEXT
                  Text(
                    "Designed by FuzzuTech",
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.5),
                      letterSpacing: 1,
                    ),
                  ),

                  const SizedBox(height: 10),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget weatherInfo(
    IconData icon,
    String title,
    String value,
  ) {
    return Column(
      children: [
        Icon(
          icon,
          color: Colors.cyanAccent,
          size: 28,
        ),
        const SizedBox(height: 8),
        Text(
          title,
          style: TextStyle(
            color: Colors.white.withOpacity(0.7),
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
      ],
    );
  }
}

class ParticleModel {
  double x;
  double y;
  double size;
  double speed;

  ParticleModel({
    required this.x,
    required this.y,
    required this.size,
    required this.speed,
  });
}