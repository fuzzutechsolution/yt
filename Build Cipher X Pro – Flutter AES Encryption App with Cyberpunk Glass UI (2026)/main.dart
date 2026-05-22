import 'package:flutter/material.dart';

import 'package:google_fonts/google_fonts.dart';

import 'package:flutter_animate/flutter_animate.dart';

import 'package:encrypt/encrypt.dart' as encrypt;

import 'dart:ui';

import 'package:flutter/services.dart';



void main() {

  runApp(const CipherXProApp());

}



class CipherXProApp extends StatelessWidget {

  const CipherXProApp({super.key});



  @override

  Widget build(BuildContext context) {

    return MaterialApp(

      title: 'Cipher X Pro',

      debugShowCheckedModeBanner: false,

      theme: ThemeData(

        brightness: Brightness.dark,

        scaffoldBackgroundColor: const Color(0xFF0F0F1B), // Deep Cyber Blue/Black

        primaryColor: Colors.cyanAccent,

        colorScheme: ColorScheme.dark(

          primary: Colors.cyanAccent,

          secondary: Colors.purpleAccent,

          surface: const Color(0xFF1E1E2E), // Card background

          background: const Color(0xFF0F0F1B),

        ),

        textTheme: GoogleFonts.rajdhaniTextTheme(

          Theme.of(context).textTheme.apply(bodyColor: Colors.white, displayColor: Colors.white),

        ),

        useMaterial3: true,

      ),

      home: const HomeScreen(),

    );

  }

}



// ==========================================

// SCREEN: HOME SCREEN

// ==========================================



class HomeScreen extends StatefulWidget {

  const HomeScreen({super.key});



  @override

  State<HomeScreen> createState() => _HomeScreenState();

}



class _HomeScreenState extends State<HomeScreen> {

  final TextEditingController _textController = TextEditingController();

  final TextEditingController _keyController = TextEditingController();

  final TextEditingController _outputController = TextEditingController(); // For result



  String _statusMessage = "";

  bool _isSuccess = false;

  bool _isEncryptMode = true; // Toggle between encrypt/decrypt



  @override

  void dispose() {

    _textController.dispose();

    _keyController.dispose();

    _outputController.dispose();

    super.dispose();

  }



  void _handleEncryption() {

    final text = _textController.text;

    final key = _keyController.text;



    if (text.isEmpty || key.isEmpty) {

      _showStatus("Please enter both text and a secret key!", false);

      return;

    }



    try {

      String result;

      if (_isEncryptMode) {

        result = EncryptionService.encryptData(text, key);

        _showStatus("Encrypted Successfully", true);

      } else {

        result = EncryptionService.decryptData(text, key);

        _showStatus("Decrypted Successfully", true);

      }

      setState(() {

        _outputController.text = result;

      });

    } catch (e) {

      _showStatus("Error: ${e.toString()}", false);

    }

  }



  void _showStatus(String msg, bool success) {

    setState(() {

      _statusMessage = msg;

      _isSuccess = success;

    });

    

    // Auto clear after 3 seconds

    Future.delayed(Duration(seconds: 3), () {

      if (mounted) setState(() => _statusMessage = "");

    });



    ScaffoldMessenger.of(context).showSnackBar(

      SnackBar(

        content: Text(msg),

        backgroundColor: success ? Colors.green.withOpacity(0.8) : Colors.red.withOpacity(0.8),

        behavior: SnackBarBehavior.floating,

        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),

      ),

    );

  }



  void _copyToClipboard() {

    if (_outputController.text.isEmpty) return;

    Clipboard.setData(ClipboardData(text: _outputController.text));

    _showStatus("Copied to Clipboard!", true);

  }



  @override

  Widget build(BuildContext context) {

    // ignore: unused_local_variable

    final size = MediaQuery.of(context).size;

    

    return Scaffold(

      body: Stack(

        children: [

          // Background - Cyberpunk Gradient Mesh (Static for performance, can be animated)

          Positioned.fill(

            child: Container(

              decoration: const BoxDecoration(

                gradient: LinearGradient(

                  colors: [Color(0xFF0F0F1B), Color(0xFF1A1A2E)],

                  begin: Alignment.topCenter,

                  end: Alignment.bottomCenter,

                ),

              ),

            ),

          ),

          // Glow Orbs

          Positioned(

            top: -100,

            left: -100,

            child: Container(

              width: 300,

              height: 300,

              decoration: BoxDecoration(

                shape: BoxShape.circle,

                color: Colors.purpleAccent.withOpacity(0.2),

                boxShadow: [BoxShadow(color: Colors.purpleAccent, blurRadius: 100, spreadRadius: 50)],

              ),

            ),

          ),

          Positioned(

            bottom: -50,

            right: -50,

            child: Container(

              width: 250,

              height: 250,

              decoration: BoxDecoration(

                shape: BoxShape.circle,

                color: Colors.cyanAccent.withOpacity(0.2),

                boxShadow: [BoxShadow(color: Colors.cyanAccent, blurRadius: 100, spreadRadius: 40)],

              ),

            ),

          ),



          // Main Content

          SafeArea(

            child: SingleChildScrollView(

              padding: const EdgeInsets.all(24.0),

              child: Column(

                crossAxisAlignment: CrossAxisAlignment.stretch,

                children: [

                  const SizedBox(height: 20),

                  // Header

                  Center(

                    child: Text(

                      "CIPHER X PRO",

                      style: GoogleFonts.orbitron(

                        fontSize: 32,

                        fontWeight: FontWeight.bold,

                        color: Colors.white,

                        letterSpacing: 4,

                        shadows: [

                          Shadow(color: Colors.cyanAccent, blurRadius: 20),

                        ],

                      ),

                    ).animate().fadeIn().scale(),

                  ),

                  const SizedBox(height: 10),

                  Center(

                    child: Text(

                      "SECURE YOUR REALITY",

                      style: GoogleFonts.rajdhani(

                        fontSize: 16,

                        color: Colors.grey[400],

                        letterSpacing: 2,

                      ),

                    ).animate().fadeIn(delay: 300.ms),

                  ),



                  const SizedBox(height: 40),



                  // Mode Toggle

                  Row(

                    mainAxisAlignment: MainAxisAlignment.center,

                    children: [

                      _buildModeButton("ENCRYPT", true),

                      const SizedBox(width: 20),

                      _buildModeButton("DECRYPT", false),

                    ],

                  ),



                  const SizedBox(height: 30),



                  // Input Section

                  GlassCard(

                    child: Column(

                      children: [

                        _buildTextField(

                          controller: _textController,

                          label: _isEncryptMode ? "Secret Message" : "Encrypted Hash",

                          icon: Icons.message,

                          maxLines: 3,

                        ),

                        const SizedBox(height: 20),

                        _buildTextField(

                          controller: _keyController,

                          label: "Secret Key (Password)",

                          icon: Icons.vpn_key,

                          isPassword: true,

                        ),

                      ],

                    ),

                  ).animate().slideY(begin: 0.2, end: 0).fadeIn(),



                  const SizedBox(height: 30),



                  // Action Button

                  NeonButton(

                    label: _isEncryptMode ? "LOCK DATA" : "UNLOCK DATA",

                    baseColor: _isEncryptMode ? Colors.cyanAccent : Colors.purpleAccent,

                    onPressed: _handleEncryption,

                  ).animate().shake(delay: 1000.ms), // Shake attention



                  const SizedBox(height: 30),



                  // Result Section

                  if (_outputController.text.isNotEmpty)

                    GlassCard(

                      baseColor: _isSuccess ? Colors.green : Colors.red,

                      child: Column(

                        children: [

                          Row(

                            mainAxisAlignment: MainAxisAlignment.spaceBetween,

                            children: [

                              Text(

                                "RESULT",

                                style: GoogleFonts.orbitron(

                                  color: Colors.white70,

                                  fontWeight: FontWeight.bold,

                                ),

                              ),

                              IconButton(

                                icon: const Icon(Icons.copy, color: Colors.white),

                                onPressed: _copyToClipboard,

                              ),

                            ],

                          ),

                          const Divider(color: Colors.white24),

                          SelectableText(

                            _outputController.text,

                            style: GoogleFonts.firaCode(

                              color: Colors.white,

                              fontSize: 14,

                            ),

                          ),

                        ],

                      ),

                    ).animate().scale(duration: 400.ms),

                ],

              ),

            ),

          ),

        ],

      ),

    );

  }



  Widget _buildModeButton(String label, bool isEncrypt) {

    final isSelected = _isEncryptMode == isEncrypt;

    final color = isEncrypt ? Colors.cyanAccent : Colors.purpleAccent;

    

    return GestureDetector(

      onTap: () {

        setState(() {

          _isEncryptMode = isEncrypt;

          _outputController.clear();

          _statusMessage = "";

        });

      },

      child: AnimatedContainer(

        duration: const Duration(milliseconds: 300),

        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),

        decoration: BoxDecoration(

          color: isSelected ? color.withOpacity(0.2) : Colors.transparent,

          borderRadius: BorderRadius.circular(30),

          border: Border.all(

            color: isSelected ? color : Colors.white24,

            width: 1.5,

          ),

          boxShadow: isSelected ? [BoxShadow(color: color.withOpacity(0.4), blurRadius: 15)] : [],

        ),

        child: Text(

          label,

          style: GoogleFonts.rajdhani(

            fontSize: 16,

            fontWeight: FontWeight.bold,

            color: isSelected ? Colors.white : Colors.grey,

            letterSpacing: 1.5,

          ),

        ),

      ),

    );

  }



  Widget _buildTextField({

    required TextEditingController controller,

    required String label,

    required IconData icon,

    bool isPassword = false,

    int maxLines = 1,

  }) {

    return TextField(

      controller: controller,

      obscureText: isPassword, // In a real app, adding a toggle visibility icon is UX best practice

      maxLines: maxLines,

      style: const TextStyle(color: Colors.white),

      cursorColor: Colors.cyanAccent,

      decoration: InputDecoration(

        labelText: label,

        labelStyle: TextStyle(color: Colors.grey[400]),

        prefixIcon: Icon(icon, color: Colors.cyanAccent),

        enabledBorder: OutlineInputBorder(

          borderSide: BorderSide(color: Colors.white24),

          borderRadius: BorderRadius.circular(12),

        ),

        focusedBorder: OutlineInputBorder(

          borderSide: BorderSide(color: Colors.cyanAccent, width: 2),

          borderRadius: BorderRadius.circular(12),

        ),

        filled: true,

        fillColor: Colors.black12,

      ),

    );

  }

}



// ==========================================

// SERVICE: ENCRYPTION

// ==========================================



class EncryptionService {

  // Use AES (Advanced Encryption Standard)

  // Mode: CBC (Cipher Block Chaining) - Better security than ECB

  // Padding: PKCS7 - Standard



  /// Encrypts the plainText using the provided secretKey.

  /// Returns a concatenation of the IV and the Encrypted Data, ensuring unique outputs for same inputs.

  static String encryptData(String plainText, String secretKey) {

    try {

      final key = _deriveKey(secretKey);

      final iv = encrypt.IV.fromLength(16); // Generate random IV

      final encrypter = encrypt.Encrypter(encrypt.AES(key, mode: encrypt.AESMode.cbc));



      final encrypted = encrypter.encrypt(plainText, iv: iv);



      // Return IV + Encrypted Data (Base64 encoded) to allow decryption

      // Format: IV:EncryptedData

      return "${iv.base64}:${encrypted.base64}"; 

    } catch (e) {

      throw Exception("Encryption Failed: ${e.toString()}");

    }

  }



  /// Decrypts the encryptedText using the provided secretKey.

  /// Expects the format: IV:EncryptedData

  static String decryptData(String encryptedText, String secretKey) {

    try {

      final parts = encryptedText.split(':');

      if (parts.length != 2) {

        throw Exception("Invalid encrypted format. Expected IV:Data");

      }



      final key = _deriveKey(secretKey);

      final iv = encrypt.IV.fromBase64(parts[0]);

      final encrypted = encrypt.Encrypted.fromBase64(parts[1]);

      

      final encrypter = encrypt.Encrypter(encrypt.AES(key, mode: encrypt.AESMode.cbc));

      

      return encrypter.decrypt(encrypted, iv: iv);

    } catch (e) {

      // In a real app, handle padding errors or key mismatch specifically

      throw Exception("Decryption Failed: possibly wrong key or corrupted data");

    }

  }



  /// Derives a 32-byte (256-bit) key from any string input.

  /// In a real production app, use PBKDF2. Here we use simple padding/truncation for clarity.

  static encrypt.Key _deriveKey(String password) {

    // Pad or truncate to exactly 32 characters

    String keyString = password.padRight(32, '*'); // Simple padding

    if (keyString.length > 32) {

      keyString = keyString.substring(0, 32);

    }

    return encrypt.Key.fromUtf8(keyString);

  }

}



// ==========================================

// WIDGET: GLASS CARD

// ==========================================



class GlassCard extends StatelessWidget {

  final Widget child;

  final double width;

  final double? height;

  final double borderRadius;

  final Color baseColor;



  const GlassCard({

    Key? key,

    required this.child,

    this.width = double.infinity,

    this.height,

    this.borderRadius = 16.0,

    this.baseColor = Colors.white,

  }) : super(key: key);



  @override

  Widget build(BuildContext context) {

    return Container(

      width: width,

      height: height,

      decoration: BoxDecoration(

        color: baseColor.withOpacity(0.05), // Very subtle fill

        borderRadius: BorderRadius.circular(borderRadius),

        boxShadow: [

          BoxShadow(

            color: Colors.black.withOpacity(0.1),

            blurRadius: 10,

            spreadRadius: 2,

            offset: Offset(0, 4),

          ),

        ],

        border: Border.all(

          color: baseColor.withOpacity(0.1), 

          width: 1.0, 

        ), 

      ),

      child: ClipRRect(

        borderRadius: BorderRadius.circular(borderRadius),

        child: BackdropFilter(

          filter: ImageFilter.blur(sigmaX: 10.0, sigmaY: 10.0), // High blur for frosted glass

          child: Padding(

            padding: EdgeInsets.all(20),

            child: child,

          ),

        ),

      ),

    );

  }

}



// ==========================================

// WIDGET: NEON BUTTON

// ==========================================



class NeonButton extends StatefulWidget {

  final String label;

  final VoidCallback onPressed;

  final Color baseColor;



  const NeonButton({

    Key? key,

    required this.label,

    required this.onPressed,

    this.baseColor = Colors.cyanAccent,

  }) : super(key: key);



  @override

  _NeonButtonState createState() => _NeonButtonState();

}



class _NeonButtonState extends State<NeonButton> with SingleTickerProviderStateMixin {

  bool _isHovered = false;

  late AnimationController _controller;

  late Animation<double> _scaleAnimation;



  @override

  void initState() {

    super.initState();

    _controller = AnimationController(

      vsync: this,

      duration: Duration(milliseconds: 200),

      lowerBound: 0.0,

      upperBound: 0.1,

    );

    _scaleAnimation = Tween<double>(begin: 1.0, end: 1.05).animate(

      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),

    );

  }



  @override

  void dispose() {

    _controller.dispose();

    super.dispose();

  }



  @override

  Widget build(BuildContext context) {

    return MouseRegion(

      onEnter: (_) => _startHover(),

      onExit: (_) => _endHover(),

      child: GestureDetector(

        onTapDown: (_) => _controller.reverse(), // Press effect

        onTapUp: (_) {

          _controller.forward();

          widget.onPressed();

        },

        child: AnimatedBuilder(

          animation: _controller,

          builder: (context, child) {

            return Transform.scale(

              scale: _scaleAnimation.value,

              child: Container(

                padding: EdgeInsets.symmetric(horizontal: 24, vertical: 16),

                decoration: BoxDecoration(

                  borderRadius: BorderRadius.circular(12),

                  // Background Gradient

                  gradient: LinearGradient(

                    colors: [

                      widget.baseColor.withOpacity(0.8),

                      widget.baseColor.withOpacity(0.6),

                    ],

                    begin: Alignment.topLeft,

                    end: Alignment.bottomRight,

                  ),

                  // Neon Glow Shadow

                  boxShadow: [

                    BoxShadow(

                      color: widget.baseColor.withOpacity(0.6),

                      blurRadius: _isHovered ? 20 : 10,

                      spreadRadius: _isHovered ? 4 : 1,

                      offset: Offset(0, 0),

                    ),

                  ],

                  border: Border.all(

                    color: Colors.white.withOpacity(0.5),

                    width: 1.0,

                  ),

                ),

                child: Center(

                  child: Text(

                    widget.label.toUpperCase(),

                    style: TextStyle(

                      color: Colors.white,

                      fontSize: 16,

                      fontWeight: FontWeight.bold,

                      letterSpacing: 1.5,

                      shadows: [

                        Shadow(

                          blurRadius: 10.0,

                          color: widget.baseColor,

                          offset: Offset(0, 0),

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

    );

  }



  void _startHover() {

    setState(() => _isHovered = true);

    _controller.forward();

  }



  void _endHover() {

    setState(() => _isHovered = false);

    _controller.reverse();

  }

}

