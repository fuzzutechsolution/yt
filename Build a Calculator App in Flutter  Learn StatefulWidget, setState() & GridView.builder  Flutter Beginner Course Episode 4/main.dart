import 'dart:ui';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

void main() {
  // Ensure framework visual bindings are initialized
  WidgetsFlutterBinding.ensureInitialized();

  // Constrain system overlays/orientations for clean rendering on mobile viewports
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
      systemNavigationBarColor: Colors.transparent,
      systemNavigationBarIconBrightness: Brightness.dark,
    ),
  );

  runApp(const PremiumCalculatorApp());
}

/// The root application class defining global material properties.
class PremiumCalculatorApp extends StatelessWidget {
  const PremiumCalculatorApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Premium Calculator',
      debugShowCheckedModeBanner: false,
      theme: PremiumTheme.lightTheme,
      home: const CalculatorScreen(),
    );
  }
}

/// Premium design color tokens inspired by Apple, Material 3, and Linear.app.
class AppColors {
  AppColors._();

  // Background and Canvas
  static const Color backgroundStart = Color(0xFFF0F4FF);
  static const Color backgroundEnd = Color(0xFFE4E9F7);
  
  // Card & Panel Surfaces
  static const Color glassBackground = Color(0x99FFFFFF); // Opacity for BackdropFilter
  static const Color cardSurface = Colors.white;
  static const Color surfaceMuted = Color(0xFFF4F4F6);
  
  // Borders & Dividers
  static const Color borderLight = Color(0x1F000000); // Soft black border
  static const Color borderSubtle = Color(0x0A000000);
  
  // Text Colors
  static const Color textPrimary = Color(0xFF1C1C1E);   // Off-black
  static const Color textSecondary = Color(0xFF8E8E93); // Muted grey
  static const Color textTertiary = Color(0xFFC7C7CC);  // Placeholder grey
  
  // Accents and Key Interaction Colors
  static const Color accentBlue = Color(0xFF007AFF);    // Apple Blue
  static const Color accentOrange = Color(0xFFFF9500);  // Apple Orange
  static const Color accentRed = Color(0xFFFF3B30);     // Apple Red
  static const Color accentGreen = Color(0xFF34C759);   // Apple Green

  // Keypad Colors
  static const Color numKeyBackground = Color(0xD9FFFFFF); // 85% opacity white
  static const Color opKeyBackground = Color(0xE6F2F2F7);  // 90% opacity light grey
  static const Color equalKeyBackground = Color(0xFF007AFF);
  static const Color equalKeyText = Colors.white;
  
  // Button Gradients
  static const LinearGradient premiumBlueGradient = LinearGradient(
    colors: [Color(0xFF007AFF), Color(0xFF0051D2)],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );

  static const LinearGradient glassGradient = LinearGradient(
    colors: [Color(0xF2FFFFFF), Color(0xCCFFFFFF)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
}

/// Premium drop-shadow and depth tokens for glassmorphism and elevated components.
class AppShadows {
  AppShadows._();

  // Premium floating card soft drop shadow
  static const BoxShadow cardShadow = BoxShadow(
    color: Color(0x0C000000), // 3% opacity black
    offset: Offset(0, 10),
    blurRadius: 30,
    spreadRadius: -5,
  );

  // Soft key shadow for tactical 3D feel
  static const BoxShadow keyShadow = BoxShadow(
    color: Color(0x05000000), // 2% opacity black
    offset: Offset(0, 4),
    blurRadius: 10,
    spreadRadius: 0,
  );

  // High elevation shadow for modals / dialogs
  static const BoxShadow overlayShadow = BoxShadow(
    color: Color(0x14000000), // 8% opacity black
    offset: Offset(0, 20),
    blurRadius: 40,
    spreadRadius: -8,
  );

  // Button hover / accent shadow
  static const BoxShadow accentShadow = BoxShadow(
    color: Color(0x26007AFF), // 15% opacity blue
    offset: Offset(0, 8),
    blurRadius: 20,
    spreadRadius: -2,
  );
}

/// Premium Light Theme configuration using Material 3 guidelines.
class PremiumTheme {
  PremiumTheme._();

  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      primaryColor: AppColors.accentBlue,
      scaffoldBackgroundColor: Colors.transparent, // Background will be a custom gradient canvas
      colorScheme: const ColorScheme.light(
        primary: AppColors.accentBlue,
        secondary: AppColors.accentOrange,
        surface: AppColors.cardSurface,
        onSurface: AppColors.textPrimary,
        error: AppColors.accentRed,
      ),
      
      // Premium Typography using standard system fonts with clean sizing & line spacing
      textTheme: const TextTheme(
        displayLarge: TextStyle(
          fontFamily: '.SF Pro Display',
          fontSize: 64,
          fontWeight: FontWeight.w300,
          color: AppColors.textPrimary,
          letterSpacing: -1.5,
        ),
        displayMedium: TextStyle(
          fontFamily: '.SF Pro Display',
          fontSize: 48,
          fontWeight: FontWeight.w400,
          color: AppColors.textPrimary,
          letterSpacing: -1.0,
        ),
        headlineMedium: TextStyle(
          fontFamily: '.SF Pro Text',
          fontSize: 28,
          fontWeight: FontWeight.w500,
          color: AppColors.textPrimary,
          letterSpacing: -0.5,
        ),
        titleLarge: TextStyle(
          fontFamily: '.SF Pro Text',
          fontSize: 20,
          fontWeight: FontWeight.w600,
          color: AppColors.textPrimary,
          letterSpacing: -0.2,
        ),
        bodyLarge: TextStyle(
          fontFamily: '.SF Pro Text',
          fontSize: 17,
          fontWeight: FontWeight.w400,
          color: AppColors.textPrimary,
        ),
        bodyMedium: TextStyle(
          fontFamily: '.SF Pro Text',
          fontSize: 15,
          fontWeight: FontWeight.w400,
          color: AppColors.textSecondary,
        ),
        labelLarge: TextStyle(
          fontFamily: '.SF Pro Text',
          fontSize: 15,
          fontWeight: FontWeight.w600,
          color: AppColors.accentBlue,
        ),
      ),
      
      // Floating Action Button Theme
      floatingActionButtonTheme: const FloatingActionButtonThemeData(
        backgroundColor: AppColors.accentBlue,
        foregroundColor: Colors.white,
        elevation: 4,
      ),

      // Divider Theme
      dividerTheme: const DividerThemeData(
        color: AppColors.borderSubtle,
        thickness: 1,
        space: 1,
      ),
    );
  }
}

/// A class representing a single calculation record in history.
class HistoryItem {
  final String expression;
  final String result;
  final DateTime timestamp;

  const HistoryItem({
    required this.expression,
    required this.result,
    required this.timestamp,
  });

  Map<String, dynamic> toJson() => {
        'expression': expression,
        'result': result,
        'timestamp': timestamp.toIso8601String(),
      };
}

/// The state class for our Calculator business logic, ensuring immutable updates.
class CalculatorState {
  final String expression;
  final String result;
  final String? errorMessage;
  final List<HistoryItem> history;
  final bool isEvaluationResult;

  const CalculatorState({
    this.expression = '',
    this.result = '0',
    this.errorMessage,
    this.history = const [],
    this.isEvaluationResult = false,
  });

  CalculatorState copyWith({
    String? expression,
    String? result,
    String? errorMessage,
    List<HistoryItem>? history,
    bool? isEvaluationResult,
  }) {
    return CalculatorState(
      expression: expression ?? this.expression,
      result: result ?? this.result,
      errorMessage: errorMessage, // Overwritten directly if passed as null
      history: history ?? this.history,
      isEvaluationResult: isEvaluationResult ?? this.isEvaluationResult,
    );
  }

  /// Create a clean state when error occurs.
  CalculatorState toError(String message) {
    return CalculatorState(
      expression: expression,
      result: 'Error',
      errorMessage: message,
      history: history,
      isEvaluationResult: true,
    );
  }
}

/// A robust, enterprise-grade mathematical expression parser
/// utilizing the Shunting-Yard algorithm. It parses infix notation,
/// supports operator precedence, parentheses, unary negative numbers,
/// percentages, and decimal accuracy.
class MathParser {
  MathParser._();

  /// Evaluates a string expression and returns the floating-point result.
  /// Throws a [FormatException] with a user-friendly message on failure.
  static double evaluate(String expression) {
    // 1. Normalize the expression string
    final cleanExpr = _normalizeExpression(expression);
    if (cleanExpr.isEmpty) return 0.0;

    // 2. Tokenize the expression
    final tokens = _tokenize(cleanExpr);

    // 3. Convert infix to postfix (RPN) using Shunting-Yard
    final postfix = _shuntingYard(tokens);

    // 4. Evaluate postfix expression
    return _evaluatePostfix(postfix);
  }

  static String _normalizeExpression(String expression) {
    return expression
        .replaceAll(' ', '')
        .replaceAll('×', '*')
        .replaceAll('÷', '/')
        .replaceAll('−', '-') // Unicode minus vs standard dash
        .replaceAll('—', '-');
  }

  static List<_Token> _tokenize(String expr) {
    final List<_Token> tokens = [];
    int i = 0;
    final int len = expr.length;

    while (i < len) {
      final char = expr[i];

      // Parse numbers (including decimal points)
      if (_isDigit(char) || char == '.') {
        final buffer = StringBuffer();
        bool hasDecimal = (char == '.');
        buffer.write(char);
        i++;

        while (i < len && (_isDigit(expr[i]) || expr[i] == '.')) {
          if (expr[i] == '.') {
            if (hasDecimal) {
              throw const FormatException('Multiple decimal points in a single number');
            }
            hasDecimal = true;
          }
          buffer.write(expr[i]);
          i++;
        }
        tokens.add(_Token(_TokenType.number, value: buffer.toString()));
        continue;
      }

      // Parse operators and parentheses
      if (char == '(') {
        tokens.add(const _Token(_TokenType.openParenthesis));
        i++;
      } else if (char == ')') {
        tokens.add(const _Token(_TokenType.closeParenthesis));
        i++;
      } else if (char == '%') {
        tokens.add(const _Token(_TokenType.percent));
        i++;
      } else if (_isOperator(char)) {
        // Determine if this is a unary operator (like -5 or +3)
        // A minus/plus is unary if it is at the start of expression, or follows another operator, or follows an open parenthesis
        bool isUnary = false;
        if (char == '-' || char == '+') {
          if (tokens.isEmpty) {
            isUnary = true;
          } else {
            final lastToken = tokens.last;
            isUnary = lastToken.type == _TokenType.operator ||
                lastToken.type == _TokenType.openParenthesis;
          }
        }

        if (isUnary) {
          if (char == '-') {
            tokens.add(const _Token(_TokenType.unaryMinus));
          }
          // Ignore unary plus since it does not change the sign
        } else {
          tokens.add(_Token(_TokenType.operator, value: char));
        }
        i++;
      } else {
        throw FormatException('Unexpected character: $char');
      }
    }

    return tokens;
  }

  static bool _isDigit(String char) {
    final code = char.codeUnitAt(0);
    return code >= 48 && code <= 57; // '0' - '9'
  }

  static bool _isOperator(String char) {
    return char == '+' || char == '-' || char == '*' || char == '/';
  }

  /// Shunting-Yard Algorithm to convert Infix to Reverse Polish Notation (RPN)
  static List<_Token> _shuntingYard(List<_Token> tokens) {
    final List<_Token> outputQueue = [];
    final List<_Token> operatorStack = [];

    for (final token in tokens) {
      switch (token.type) {
        case _TokenType.number:
          outputQueue.add(token);
          break;

        case _TokenType.percent:
          // Percent is a high-precedence postfix unary operator.
          // Apply immediately to the number at the end of the queue.
          outputQueue.add(token);
          break;

        case _TokenType.unaryMinus:
          operatorStack.add(token);
          break;

        case _TokenType.operator:
          while (operatorStack.isNotEmpty &&
              _shouldPopOperator(token, operatorStack.last)) {
            outputQueue.add(operatorStack.removeLast());
          }
          operatorStack.add(token);
          break;

        case _TokenType.openParenthesis:
          operatorStack.add(token);
          break;

        case _TokenType.closeParenthesis:
          bool foundOpen = false;
          while (operatorStack.isNotEmpty) {
            if (operatorStack.last.type == _TokenType.openParenthesis) {
              operatorStack.removeLast(); // discard open parenthesis
              foundOpen = true;
              break;
            }
            outputQueue.add(operatorStack.removeLast());
          }
          if (!foundOpen) {
            throw const FormatException('Unbalanced parentheses: missing open parenthesis');
          }
          break;
      }
    }

    // Pop remaining operators in stack to queue
    while (operatorStack.isNotEmpty) {
      final op = operatorStack.last;
      if (op.type == _TokenType.openParenthesis || op.type == _TokenType.closeParenthesis) {
        throw const FormatException('Unbalanced parentheses: missing close parenthesis');
      }
      outputQueue.add(operatorStack.removeLast());
    }

    return outputQueue;
  }

  static bool _shouldPopOperator(_Token tokenCurrent, _Token tokenStack) {
    if (tokenStack.type == _TokenType.openParenthesis) return false;
    
    final precCurrent = _getPrecedence(tokenCurrent);
    final precStack = _getPrecedence(tokenStack);

    if (tokenCurrent.type == _TokenType.unaryMinus) {
      // Unary minus is right-associative, so we don't pop stack operator of same precedence
      return precStack > precCurrent;
    }

    // Binary operators are left-associative
    return precStack >= precCurrent;
  }

  static int _getPrecedence(_Token token) {
    switch (token.type) {
      case _TokenType.unaryMinus:
        return 3;
      case _TokenType.operator:
        if (token.value == '*' || token.value == '/') return 2;
        if (token.value == '+' || token.value == '-') return 1;
        return 0;
      default:
        return 0;
    }
  }

  /// Evaluates the RPN/Postfix token queue
  static double _evaluatePostfix(List<_Token> postfix) {
    final List<double> evalStack = [];

    for (final token in postfix) {
      if (token.type == _TokenType.number) {
        final val = double.tryParse(token.value ?? '');
        if (val == null) throw const FormatException('Invalid number format');
        evalStack.add(val);
      } else if (token.type == _TokenType.percent) {
        if (evalStack.isEmpty) throw const FormatException('Invalid expression using %');
        final val = evalStack.removeLast();
        evalStack.add(val / 100.0);
      } else if (token.type == _TokenType.unaryMinus) {
        if (evalStack.isEmpty) throw const FormatException('Invalid unary minus expression');
        final val = evalStack.removeLast();
        evalStack.add(-val);
      } else if (token.type == _TokenType.operator) {
        if (evalStack.length < 2) {
          throw const FormatException('Insufficient operands for operation');
        }
        final b = evalStack.removeLast();
        final a = evalStack.removeLast();
        final result = _applyOperator(token.value ?? '', a, b);
        evalStack.add(result);
      }
    }

    if (evalStack.length != 1) {
      throw const FormatException('The expression is incomplete');
    }

    // Clean up negative zeroes or minor floating point rounding
    double finalVal = evalStack.first;
    if (finalVal.isNaN) throw const FormatException('Not a number');
    if (finalVal.isInfinite) throw const FormatException('Division by zero');
    
    // Avoid representation errors like 0.1 + 0.2 = 0.30000000000000004
    // We round to 12 decimal places to ensure precision while matching standard calculator expectations
    finalVal = double.parse(finalVal.toStringAsFixed(12));
    // Strip trailing zeroes
    return finalVal;
  }

  static double _applyOperator(String op, double a, double b) {
    switch (op) {
      case '+':
        return a + b;
      case '-':
        return a - b;
      case '*':
        return a * b;
      case '/':
        if (b == 0.0) {
          throw const FormatException('Division by zero');
        }
        return a / b;
      default:
        throw FormatException('Unknown operator: $op');
    }
  }
}

enum _TokenType {
  number,
  operator,
  unaryMinus,
  percent,
  openParenthesis,
  closeParenthesis,
}

class _Token {
  final _TokenType type;
  final String? value;

  const _Token(this.type, {this.value});

  @override
  String toString() {
    return 'Token($type, value: $value)';
  }
}

/// The central state manager for the calculator application, decoupling UI and math logic.
class CalculatorNotifier extends ValueNotifier<CalculatorState> {
  CalculatorNotifier() : super(const CalculatorState());

  // Set of operators for layout/input checks
  static const List<String> _operators = ['+', '−', '×', '÷'];

  /// Appends a digit or decimal to the input expression.
  void appendDigit(String digit) {
    final stateVal = value;

    if (stateVal.isEvaluationResult || stateVal.result == 'Error') {
      value = stateVal.copyWith(
        expression: digit,
        result: '0',
        isEvaluationResult: false,
      );
      return;
    }

    String currentExpr = stateVal.expression;
    if (currentExpr == '0') {
      currentExpr = digit;
    } else {
      currentExpr += digit;
    }

    value = stateVal.copyWith(
      expression: currentExpr,
      isEvaluationResult: false,
    );
  }

  /// Appends an arithmetic operator with premium space formatting.
  void appendOperator(String op) {
    final stateVal = value;
    String currentExpr = stateVal.expression;
    String opSymbol = _normalizeOpSymbol(op);

    // If an error is on screen, clear it and start fresh with 0 and the operator
    if (stateVal.result == 'Error') {
      value = stateVal.copyWith(
        expression: '0 $opSymbol ',
        result: '0',
        isEvaluationResult: false,
      );
      return;
    }

    // If evaluation just finished, chain the operator to the result
    if (stateVal.isEvaluationResult) {
      currentExpr = stateVal.result;
    }

    if (currentExpr.isEmpty) {
      // If expression is empty, allow a minus operator to indicate negative number
      if (opSymbol == '−') {
        currentExpr = '−';
      } else {
        currentExpr = '0 $opSymbol ';
      }
    } else {
      // Check if expression ends with an operator (including space padding)
      final trimmed = currentExpr.trimRight();
      bool endsWithOp = false;
      String matchedOp = '';
      for (final o in _operators) {
        if (trimmed.endsWith(o)) {
          endsWithOp = true;
          matchedOp = o;
          break;
        }
      }

      if (endsWithOp) {
        // Swap operators
        final lastOpIndex = currentExpr.lastIndexOf(matchedOp);
        if (lastOpIndex != -1) {
          currentExpr = '${currentExpr.substring(0, lastOpIndex)}$opSymbol ';
        }
      } else {
        // Normal append with spacing
        if (currentExpr.endsWith('(')) {
          // If it's after an open parenthesis, don't pad preceding space for unary operators
          if (opSymbol == '−') {
            currentExpr += opSymbol;
          }
        } else if (currentExpr == '−') {
          // Double minus or operator replacement
          if (opSymbol != '−') {
            currentExpr = '0 $opSymbol ';
          }
        } else {
          currentExpr += ' $opSymbol ';
        }
      }
    }

    value = stateVal.copyWith(
      expression: currentExpr,
      isEvaluationResult: false,
    );
  }

  /// Handles smart decimal placement.
  void appendDecimal() {
    final stateVal = value;
    String currentExpr = stateVal.expression;

    if (stateVal.isEvaluationResult || stateVal.result == 'Error') {
      value = stateVal.copyWith(
        expression: '0.',
        result: '0',
        isEvaluationResult: false,
      );
      return;
    }

    if (currentExpr.isEmpty) {
      currentExpr = '0.';
    } else {
      // Find the last number token in the expression to see if it already has a decimal
      final lastSpace = currentExpr.lastIndexOf(' ');
      final lastParen = currentExpr.lastIndexOf('(');
      final splitIndex = lastSpace > lastParen ? lastSpace : lastParen;
      
      final lastPart = splitIndex != -1 
          ? currentExpr.substring(splitIndex) 
          : currentExpr;

      if (lastPart.contains('.')) {
        // Ignore duplicate decimal in same token
        return;
      }

      // If last char is an operator or parenthesis, prefix with 0
      final lastChar = currentExpr.substring(currentExpr.length - 1);
      if (lastChar == ' ' || lastChar == '(') {
        currentExpr += '0.';
      } else {
        currentExpr += '.';
      }
    }

    value = stateVal.copyWith(
      expression: currentExpr,
      isEvaluationResult: false,
    );
  }

  /// Appends a percentage symbol.
  void appendPercent() {
    final stateVal = value;
    String currentExpr = stateVal.expression;

    if (stateVal.isEvaluationResult) {
      currentExpr = stateVal.result;
    }

    if (currentExpr.isEmpty || currentExpr.endsWith(' ') || currentExpr.endsWith('(')) {
      // Percent cannot follow operator or start expression directly without a number
      return;
    }

    value = stateVal.copyWith(
      expression: '$currentExpr%',
      isEvaluationResult: false,
    );
  }

  /// Appends balanced parenthesis.
  void appendParenthesis(String paren) {
    final stateVal = value;
    String currentExpr = stateVal.expression;

    if (stateVal.isEvaluationResult || stateVal.result == 'Error') {
      value = stateVal.copyWith(
        expression: paren == '(' ? '(' : '0',
        result: '0',
        isEvaluationResult: false,
      );
      return;
    }

    if (paren == '(') {
      if (currentExpr.isNotEmpty && 
          !currentExpr.endsWith(' ') && 
          !currentExpr.endsWith('(')) {
        // Automatically inject multiplication if open parenthesis follows a number
        currentExpr += ' × (';
      } else {
        currentExpr += '(';
      }
    } else {
      // Closing parenthesis
      // Check if we have an open parenthesis to close
      int openCount = 0;
      int closeCount = 0;
      for (int i = 0; i < currentExpr.length; i++) {
        if (currentExpr[i] == '(') openCount++;
        if (currentExpr[i] == ')') closeCount++;
      }

      if (openCount > closeCount && 
          currentExpr.isNotEmpty && 
          !currentExpr.endsWith(' ') && 
          !currentExpr.endsWith('(')) {
        currentExpr += ')';
      } else {
        // Do nothing if there's no matching open parenthesis
        return;
      }
    }

    value = stateVal.copyWith(
      expression: currentExpr,
      isEvaluationResult: false,
    );
  }

  /// Deletes the last input entry, handles operator padding.
  void deleteLast() {
    final stateVal = value;
    String currentExpr = stateVal.expression;

    if (stateVal.isEvaluationResult || currentExpr.isEmpty) {
      clearAll();
      return;
    }

    if (currentExpr.endsWith(' ')) {
      // It is an operator (ends with 'op '), strip trailing spaces and the operator
      // e.g. "5 + " -> ends with " + ", length is 3
      if (currentExpr.length >= 3) {
        currentExpr = currentExpr.substring(0, currentExpr.length - 3);
      } else {
        currentExpr = '';
      }
    } else {
      // Normal single char delete
      currentExpr = currentExpr.substring(0, currentExpr.length - 1);
    }

    value = stateVal.copyWith(
      expression: currentExpr,
      result: currentExpr.isEmpty ? '0' : stateVal.result,
      isEvaluationResult: false,
    );
  }

  /// Clears the state entirely.
  void clearAll() {
    value = CalculatorState(
      history: value.history,
    );
  }

  /// Clears computation history.
  void clearHistory() {
    value = value.copyWith(history: const []);
  }

  /// Evaluates the expression and commits the outcome to history.
  void evaluate() {
    final stateVal = value;
    final expr = stateVal.expression.trim();

    if (expr.isEmpty) return;

    try {
      final double rawResult = MathParser.evaluate(expr);
      
      // Format output cleanly: remove trailing decimal zero
      String formattedResult;
      if (rawResult == rawResult.toInt().toDouble()) {
        formattedResult = rawResult.toInt().toString();
      } else {
        formattedResult = rawResult.toString();
      }

      // Add to history
      final historyItem = HistoryItem(
        expression: stateVal.expression,
        result: formattedResult,
        timestamp: DateTime.now(),
      );

      value = stateVal.copyWith(
        result: formattedResult,
        history: [historyItem, ...stateVal.history],
        isEvaluationResult: true,
      );
    } catch (e) {
      String userFriendlyMessage = 'Invalid Expression';
      if (e is FormatException) {
        userFriendlyMessage = e.message;
      }
      value = stateVal.toError(userFriendlyMessage);
    }
  }

  String _normalizeOpSymbol(String op) {
    if (op == '*') return '×';
    if (op == '/') return '÷';
    if (op == '-') return '−';
    return op;
  }
}

/// A layout manager that adapts to different viewport widths.
/// Uses 750px as the breakpoint to transition between a single pane (mobile)
/// and a multi-pane split layout (desktop/tablet).
/// Uses builder callbacks (lazy) so only the active branch is built.
class ResponsiveLayout extends StatelessWidget {
  final WidgetBuilder mobileBuilder;
  final WidgetBuilder desktopBuilder;

  const ResponsiveLayout({
    super.key,
    required this.mobileBuilder,
    required this.desktopBuilder,
  });

  static bool isMobile(BuildContext context) =>
      MediaQuery.sizeOf(context).width < 750;

  static bool isDesktop(BuildContext context) =>
      MediaQuery.sizeOf(context).width >= 750;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth >= 750) {
          return desktopBuilder(context);
        } else {
          return mobileBuilder(context);
        }
      },
    );
  }
}

/// A premium glassmorphic container widget featuring BackdropFilter blur,
/// thin translucent borders, and soft shadows.
class GlassCard extends StatelessWidget {
  final Widget child;
  final double borderRadius;
  final double blurSigma;
  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;
  final BoxBorder? border;

  const GlassCard({
    super.key,
    required this.child,
    this.borderRadius = 24.0,
    this.blurSigma = 20.0,
    this.padding,
    this.margin,
    this.border,
  });

  @override
  Widget build(BuildContext context) {
    final containerContent = Container(
      padding: padding,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(borderRadius),
        gradient: AppColors.glassGradient,
        border: border ??
            Border.all(
              color: Colors.white.withValues(alpha: 0.35),
              width: 1.5,
            ),
      ),
      child: child,
    );

    if (kIsWeb) {
      // BackdropFilter can cause blank screens/rendering bugs on Web (e.g. HTML renderer)
      return Container(
        margin: margin,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(borderRadius),
          boxShadow: const [AppShadows.cardShadow],
        ),
        child: containerContent,
      );
    }

    return Container(
      margin: margin,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(borderRadius),
        boxShadow: const [AppShadows.cardShadow],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(borderRadius),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: blurSigma, sigmaY: blurSigma),
          child: containerContent,
        ),
      ),
    );
  }
}

/// A premium, high-fidelity display component for the calculator.
/// Displays Mac-style window decorations, current expression, and active results.
class CalculatorDisplay extends StatelessWidget {
  final String expression;
  final String result;
  final String? errorMessage;
  final VoidCallback? onHistoryPressed;

  const CalculatorDisplay({
    super.key,
    required this.expression,
    required this.result,
    this.errorMessage,
    this.onHistoryPressed,
  });

  @override
  Widget build(BuildContext context) {
    final hasError = errorMessage != null;
    final displayText = hasError ? errorMessage! : result;
    
    // Dynamically calculate font size based on results length
    double resultFontSize = 54.0;
    if (displayText.length > 8) {
      resultFontSize = 38.0;
    }
    if (displayText.length > 12) {
      resultFontSize = 28.0;
    }

    return Container(
      padding: const EdgeInsets.fromLTRB(24, 16, 24, 20),
      decoration: const BoxDecoration(
        color: Colors.transparent,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // 1. Premium Window Controls Header (Apple Style)
          Row(
            children: [
              _buildMacDot(const Color(0xFFFF5F56)), // Close
              const SizedBox(width: 8),
              _buildMacDot(const Color(0xFFFFBD2E)), // Minimize
              const SizedBox(width: 8),
              _buildMacDot(const Color(0xFF27C93F)), // Zoom
              const Spacer(),
              if (onHistoryPressed != null) ...[
                IconButton(
                  icon: const Icon(Icons.history_rounded, size: 18),
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(),
                  splashRadius: 20,
                  color: AppColors.textSecondary,
                  tooltip: 'History Logs',
                  onPressed: onHistoryPressed,
                ),
                const SizedBox(width: 12),
              ],
              // Mini SaaS label
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: AppColors.borderLight.withValues(alpha: 0.03),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(
                    color: AppColors.borderLight.withValues(alpha: 0.05),
                  ),
                ),
                child: const Row(
                  children: [
                    Icon(
                      Icons.lock_outline_rounded,
                      size: 11,
                      color: AppColors.textSecondary,
                    ),
                    SizedBox(width: 4),
                    Text(
                      'Calculator.app',
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.w500,
                        color: AppColors.textSecondary,
                        letterSpacing: 0.1,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),

          // 2 & 3. Expression + Result pinned to bottom of display
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            mainAxisSize: MainAxisSize.min,
            children: [
              // Expression Viewport
              SizedBox(
                height: 28,
                child: SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  reverse: true,
                  physics: const BouncingScrollPhysics(),
                  child: Text(
                    expression.isEmpty ? ' ' : expression,
                    style: const TextStyle(
                      color: AppColors.textSecondary,
                      fontSize: 20,
                      fontWeight: FontWeight.w400,
                      fontFamily: '.SF Pro Text',
                      letterSpacing: 0.5,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 6),

              // Result / Error Viewport
              SizedBox(
                height: 72,
                child: SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  reverse: true,
                  physics: const BouncingScrollPhysics(),
                  child: AnimatedDefaultTextStyle(
                    duration: const Duration(milliseconds: 150),
                    curve: Curves.easeOutCubic,
                    style: TextStyle(
                      color: hasError ? AppColors.accentRed : AppColors.textPrimary,
                      fontSize: resultFontSize,
                      fontWeight: FontWeight.w500,
                      fontFamily: '.SF Pro Display',
                      letterSpacing: -0.5,
                    ),
                    child: Text(displayText),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMacDot(Color color) {
    return Container(
      width: 12,
      height: 12,
      decoration: BoxDecoration(
        color: color,
        shape: BoxShape.circle,
        border: Border.all(
          color: Colors.black.withValues(alpha: 0.04),
          width: 0.5,
        ),
      ),
    );
  }
}

/// A premium, interactive button widget designed to replicate tactile feel.
/// Features micro-animations for hover, scale down on tap, and haptics.
class CalculatorButton extends StatefulWidget {
  final String text;
  final VoidCallback onPressed;
  final Color backgroundColor;
  final Color textColor;
  final bool isAccent;
  final bool isOperator;

  const CalculatorButton({
    super.key,
    required this.text,
    required this.onPressed,
    this.backgroundColor = AppColors.numKeyBackground,
    this.textColor = AppColors.textPrimary,
    this.isAccent = false,
    this.isOperator = false,
  });

  @override
  State<CalculatorButton> createState() => _CalculatorButtonState();
}

class _CalculatorButtonState extends State<CalculatorButton> {
  bool _isHovered = false;
  bool _isPressed = false;
  double _scale = 1.0;

  void _handleTapDown(TapDownDetails _) {
    HapticFeedback.lightImpact();
    setState(() {
      _isPressed = true;
      _scale = 0.92;
    });
  }

  void _handleTapUp(TapUpDetails _) {
    setState(() {
      _isPressed = false;
      _scale = 1.0;
    });
    widget.onPressed();
  }

  void _handleTapCancel() {
    setState(() {
      _isPressed = false;
      _scale = 1.0;
    });
  }

  @override
  Widget build(BuildContext context) {
    // Styling states
    Color resolvedBg = widget.backgroundColor;
    Color resolvedText = widget.textColor;

    if (widget.isAccent) {
      resolvedBg = _isPressed 
          ? const Color(0xFF0051D2) 
          : (_isHovered ? const Color(0xFF3395FF) : AppColors.accentBlue);
      resolvedText = Colors.white; // Accent buttons always have white text
    } else if (widget.isOperator) {
      resolvedBg = _isPressed
          ? const Color(0xFFD1D1D6)
          : (_isHovered ? const Color(0xFFE5E5EA) : widget.backgroundColor);
    } else {
      // Normal numbers
      resolvedBg = _isPressed
          ? const Color(0xFFE5E5EA)
          : (_isHovered ? const Color(0xFFF2F2F7) : widget.backgroundColor);
    }

    final shadowList = widget.isAccent
        ? [
            BoxShadow(
              color: AppColors.accentBlue.withValues(alpha: _isHovered ? 0.45 : 0.30),
              offset: const Offset(0, 6),
              blurRadius: 18,
              spreadRadius: -2,
            ),
          ]
        : [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.06),
              offset: const Offset(0, 2),
              blurRadius: 8,
              spreadRadius: 0,
            ),
          ];

    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => setState(() => _isHovered = true),
      onExit: (_) => setState(() => _isHovered = false),
      child: GestureDetector(
        onTapDown: _handleTapDown,
        onTapUp: _handleTapUp,
        onTapCancel: _handleTapCancel,
        child: AnimatedScale(
          scale: _scale,
          duration: const Duration(milliseconds: 80),
          curve: Curves.easeOutCubic,
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 120),
            decoration: BoxDecoration(
              color: widget.isAccent ? null : resolvedBg,
              gradient: widget.isAccent
                  ? LinearGradient(
                      colors: [
                        _isPressed
                            ? const Color(0xFF0051D2)
                            : (_isHovered ? const Color(0xFF3395FF) : const Color(0xFF1A7FFF)),
                        _isPressed
                            ? const Color(0xFF003EB3)
                            : (_isHovered ? const Color(0xFF0060E6) : const Color(0xFF005CE6)),
                      ],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    )
                  : null,
              borderRadius: BorderRadius.circular(20.0),
              border: Border.all(
                color: widget.isAccent
                    ? Colors.white.withValues(alpha: 0.20)
                    : (widget.isOperator
                        ? AppColors.borderLight.withValues(alpha: 0.10)
                        : AppColors.borderLight.withValues(alpha: 0.08)),
                width: 1.0,
              ),
              boxShadow: shadowList,
            ),
            alignment: Alignment.center,
            child: Text(
              widget.text,
              style: TextStyle(
                color: resolvedText,
                fontSize: widget.isAccent ? 24 : (widget.isOperator ? 22 : 20),
                fontWeight: widget.isAccent
                    ? FontWeight.w700
                    : (widget.isOperator ? FontWeight.w600 : FontWeight.w500),
                fontFamily: '.SF Pro Text',
                height: 1.0,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/// A premium, clean panel showing previous calculation logs.
/// Supports clicking on a log to restore it to the calculator workspace.
class HistoryPanel extends StatelessWidget {
  final List<HistoryItem> history;
  final Function(HistoryItem) onHistoryItemSelected;
  final VoidCallback onClearHistory;

  const HistoryPanel({
    super.key,
    required this.history,
    required this.onHistoryItemSelected,
    required this.onClearHistory,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        color: Colors.transparent,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Header
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
            child: Row(
              children: [
                const Icon(
                  Icons.history_rounded,
                  size: 20,
                  color: AppColors.textPrimary,
                ),
                const SizedBox(width: 8),
                const Text(
                  'Calculation Log',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    fontFamily: '.SF Pro Text',
                    color: AppColors.textPrimary,
                  ),
                ),
                const Spacer(),
                if (history.isNotEmpty)
                  TextButton.icon(
                    style: TextButton.styleFrom(
                      foregroundColor: AppColors.accentRed,
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      minimumSize: Size.zero,
                      tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    ),
                    icon: const Icon(Icons.delete_sweep_rounded, size: 16),
                    label: const Text(
                      'Clear',
                      style: TextStyle(fontSize: 12, fontWeight: FontWeight.w500),
                    ),
                    onPressed: onClearHistory,
                  ),
              ],
            ),
          ),
          const Divider(),

          // History List
          Expanded(
            child: history.isEmpty
                ? const Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.calculate_outlined,
                          size: 32,
                          color: AppColors.textTertiary,
                        ),
                        SizedBox(height: 12),
                        Text(
                          'No history logs yet',
                          style: TextStyle(
                            fontSize: 13,
                            color: AppColors.textSecondary,
                            fontWeight: FontWeight.w400,
                          ),
                        ),
                      ],
                    ),
                  )
                : ListView.separated(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    itemCount: history.length,
                    separatorBuilder: (context, index) => const SizedBox(height: 8),
                    itemBuilder: (context, index) {
                      final item = history[index];
                      return _HistoryListItem(
                        item: item,
                        onTap: () => onHistoryItemSelected(item),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}

class _HistoryListItem extends StatefulWidget {
  final HistoryItem item;
  final VoidCallback onTap;

  const _HistoryListItem({
    required this.item,
    required this.onTap,
  });

  @override
  State<_HistoryListItem> createState() => _HistoryListItemState();
}

class _HistoryListItemState extends State<_HistoryListItem> {
  bool _isHovered = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => setState(() => _isHovered = true),
      onExit: (_) => setState(() => _isHovered = false),
      child: GestureDetector(
        onTap: widget.onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: _isHovered
                ? AppColors.borderLight.withValues(alpha: 0.02)
                : Colors.transparent,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: _isHovered
                  ? AppColors.borderLight.withValues(alpha: 0.05)
                  : Colors.transparent,
              width: 1.0,
            ),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              // Expression
              Text(
                widget.item.expression,
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w400,
                  color: AppColors.textSecondary,
                  fontFamily: '.SF Pro Text',
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 4),
              // Result
              Text(
                '= ${widget.item.result}',
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                  color: AppColors.accentBlue,
                  fontFamily: '.SF Pro Display',
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// The core dashboard view displaying the responsive calculator workspace.
/// Intercepts physical keyboard inputs on desktop/web viewports.
class CalculatorScreen extends StatefulWidget {
  const CalculatorScreen({super.key});

  @override
  State<CalculatorScreen> createState() => _CalculatorScreenState();
}

class _CalculatorScreenState extends State<CalculatorScreen> {
  late final CalculatorNotifier _notifier;
  late final FocusNode _focusNode;

  @override
  void initState() {
    super.initState();
    _notifier = CalculatorNotifier();
    _focusNode = FocusNode();
    
    // Ensure keyboard focus is active immediately on load
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _focusNode.requestFocus();
    });
  }

  @override
  void dispose() {
    _notifier.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  /// Keyboard listener interception for premium desktop/web utility.
  KeyEventResult _handleKeyEvent(FocusNode node, KeyEvent event) {
    if (event is KeyDownEvent) {
      final char = event.character;
      final logicalKey = event.logicalKey;

      if (char != null && RegExp(r'[0-9]').hasMatch(char)) {
        _notifier.appendDigit(char);
        return KeyEventResult.handled;
      }
      
      if (logicalKey == LogicalKeyboardKey.period || char == '.') {
        _notifier.appendDecimal();
        return KeyEventResult.handled;
      }

      if (char == '+' || logicalKey == LogicalKeyboardKey.add) {
        _notifier.appendOperator('+');
        return KeyEventResult.handled;
      }
      if (char == '-' || logicalKey == LogicalKeyboardKey.minus || logicalKey == LogicalKeyboardKey.numpadSubtract) {
        _notifier.appendOperator('−');
        return KeyEventResult.handled;
      }
      if (char == '*' || char == 'x' || char == 'X' || logicalKey == LogicalKeyboardKey.numpadMultiply) {
        _notifier.appendOperator('×');
        return KeyEventResult.handled;
      }
      if (char == '/' || logicalKey == LogicalKeyboardKey.numpadDivide) {
        _notifier.appendOperator('÷');
        return KeyEventResult.handled;
      }
      if (char == '%') {
        _notifier.appendPercent();
        return KeyEventResult.handled;
      }
      if (char == '(') {
        _notifier.appendParenthesis('(');
        return KeyEventResult.handled;
      }
      if (char == ')') {
        _notifier.appendParenthesis(')');
        return KeyEventResult.handled;
      }
      if (logicalKey == LogicalKeyboardKey.enter || 
          logicalKey == LogicalKeyboardKey.numpadEnter || 
          char == '=') {
        _notifier.evaluate();
        return KeyEventResult.handled;
      }
      if (logicalKey == LogicalKeyboardKey.backspace) {
        _notifier.deleteLast();
        return KeyEventResult.handled;
      }
      if (logicalKey == LogicalKeyboardKey.escape || char == 'c' || char == 'C') {
        _notifier.clearAll();
        return KeyEventResult.handled;
      }
    }
    return KeyEventResult.ignored;
  }

  /// Opens the calculator history log as a frosted glass sheet on mobile layout.
  void _showMobileHistory() {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      barrierColor: Colors.black.withValues(alpha: 0.2),
      isScrollControlled: true,
      builder: (context) {
        return FractionallySizedBox(
          heightFactor: 0.75,
          child: ValueListenableBuilder<CalculatorState>(
            valueListenable: _notifier,
            builder: (context, state, _) {
              return GlassCard(
                borderRadius: 28.0,
                blurSigma: 30,
                border: Border(
                  top: BorderSide(color: Colors.white.withValues(alpha: 0.4), width: 1.5),
                  left: BorderSide(color: Colors.white.withValues(alpha: 0.4), width: 1.5),
                  right: BorderSide(color: Colors.white.withValues(alpha: 0.4), width: 1.5),
                ),
                child: Column(
                  children: [
                    // Handlebar indicator
                    Center(
                      child: Container(
                        margin: const EdgeInsets.only(top: 12, bottom: 8),
                        width: 40,
                        height: 5,
                        decoration: BoxDecoration(
                          color: AppColors.textTertiary,
                          borderRadius: BorderRadius.circular(10),
                        ),
                      ),
                    ),
                    Expanded(
                      child: HistoryPanel(
                        history: state.history,
                        onHistoryItemSelected: (item) {
                          _notifier.clearAll();
                          // Restore previous expression
                          _notifier.appendDigit(item.expression);
                          Navigator.pop(context);
                        },
                        onClearHistory: _notifier.clearHistory,
                      ),
                    ),
                  ],
                ),
              );
            },
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Focus(
      focusNode: _focusNode,
      onKeyEvent: _handleKeyEvent,
      autofocus: true,
      child: GestureDetector(
        // Keep focus active if user clicks outside inputs
        onTap: () {
          if (!_focusNode.hasFocus) {
            _focusNode.requestFocus();
          }
        },
        child: Scaffold(
          body: Container(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                colors: [AppColors.backgroundStart, AppColors.backgroundEnd],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
            ),
            child: SafeArea(
              child: ResponsiveLayout(
                mobileBuilder: (_) => _buildMobileLayout(),
                desktopBuilder: (_) => _buildDesktopLayout(),
              ),
            ),
          ),
        ),
      ),
    );
  }

  // Mobile viewport layout
  Widget _buildMobileLayout() {
    return ValueListenableBuilder<CalculatorState>(
      valueListenable: _notifier,
      builder: (context, state, _) {
        // LayoutBuilder gives us the real available width & height.
        // We split height explicitly: keypad gets 60% (clamped) and
        // the display takes the rest via Expanded. This prevents the
        // keypad's intrinsic height from overflowing on short/landscape
        // screens (e.g. 749×547), which would collapse the display to 0.
        return LayoutBuilder(
          builder: (ctx, constraints) {
            if (constraints.maxHeight == 0 || constraints.maxWidth == 0) {
              return const SizedBox.shrink();
            }

            // Keypad gets 60% of height, clamped to a sensible range
            final double keypadH =
                (constraints.maxHeight * 0.60).clamp(220.0, 400.0);

            return Center(
              child: Container(
                width: constraints.maxWidth.clamp(0, 440),
                height: constraints.maxHeight,
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                child: GlassCard(
                  borderRadius: 28.0,
                  padding: EdgeInsets.zero,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      // Display fills whatever is left after keypad
                      Expanded(
                        child: CalculatorDisplay(
                          expression: state.expression,
                          result: state.result,
                          errorMessage: state.errorMessage,
                          onHistoryPressed: _showMobileHistory,
                        ),
                      ),
                      Divider(height: 1, color: AppColors.borderSubtle),
                      // Keypad has a fixed calculated height so it never overflows
                      SizedBox(
                        height: keypadH,
                        child: Padding(
                          padding: const EdgeInsets.fromLTRB(14, 10, 14, 14),
                          child: _buildKeypadGrid(),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            );
          },
        );
      },
    );
  }

  // Tablet/Desktop viewport layout (Side-by-side dashboard)
  Widget _buildDesktopLayout() {
    return ValueListenableBuilder<CalculatorState>(
      valueListenable: _notifier,
      builder: (context, state, _) {
        return Center(
          child: SingleChildScrollView(
            child: GlassCard(
              borderRadius: 32.0,
              padding: EdgeInsets.zero,
              child: SizedBox(
                width: 780,
                height: 600,
                child: Row(
                  children: [
                    // Calculator area
                    SizedBox(
                      width: 440,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          CalculatorDisplay(
                            expression: state.expression,
                            result: state.result,
                            errorMessage: state.errorMessage,
                          ), // No history on desktop — HistoryPanel is always visible
                          const Divider(),
                          Expanded(
                            child: Padding(
                              padding: const EdgeInsets.fromLTRB(20, 20, 20, 16),
                              child: _buildKeypadGrid(),
                            ),
                          ),
                        ],
                      ),
                    ),
                    // Elegant divider
                    const VerticalDivider(),
                    // History panel area
                    Expanded(
                      child: HistoryPanel(
                        history: state.history,
                        onHistoryItemSelected: (item) {
                          _notifier.clearAll();
                          // Support quick expression restore
                          _notifier.appendDigit(item.expression);
                        },
                        onClearHistory: _notifier.clearHistory,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  /// Builds a responsive grid of buttons utilizing a custom GridView.
  Widget _buildKeypadGrid() {
    final List<_ButtonConfig> buttons = [
      _ButtonConfig('AC', _notifier.clearAll, backgroundColor: AppColors.opKeyBackground, textColor: AppColors.accentRed),
      _ButtonConfig('( )', () => _notifier.appendParenthesis('('), backgroundColor: AppColors.opKeyBackground, textColor: AppColors.accentBlue),
      _ButtonConfig('%', _notifier.appendPercent, backgroundColor: AppColors.opKeyBackground, textColor: AppColors.accentBlue),
      _ButtonConfig('÷', () => _notifier.appendOperator('/'), backgroundColor: AppColors.opKeyBackground, textColor: AppColors.accentBlue, isOperator: true),
      
      _ButtonConfig('7', () => _notifier.appendDigit('7')),
      _ButtonConfig('8', () => _notifier.appendDigit('8')),
      _ButtonConfig('9', () => _notifier.appendDigit('9')),
      _ButtonConfig('×', () => _notifier.appendOperator('*'), backgroundColor: AppColors.opKeyBackground, textColor: AppColors.accentBlue, isOperator: true),
      
      _ButtonConfig('4', () => _notifier.appendDigit('4')),
      _ButtonConfig('5', () => _notifier.appendDigit('5')),
      _ButtonConfig('6', () => _notifier.appendDigit('6')),
      _ButtonConfig('−', () => _notifier.appendOperator('-'), backgroundColor: AppColors.opKeyBackground, textColor: AppColors.accentBlue, isOperator: true),
      
      _ButtonConfig('1', () => _notifier.appendDigit('1')),
      _ButtonConfig('2', () => _notifier.appendDigit('2')),
      _ButtonConfig('3', () => _notifier.appendDigit('3')),
      _ButtonConfig('+', () => _notifier.appendOperator('+'), backgroundColor: AppColors.opKeyBackground, textColor: AppColors.accentBlue, isOperator: true),
      
      _ButtonConfig('0', () => _notifier.appendDigit('0')),
      _ButtonConfig('.', _notifier.appendDecimal),
      _ButtonConfig('⌫', _notifier.deleteLast, backgroundColor: AppColors.opKeyBackground, textColor: AppColors.textSecondary),
      _ButtonConfig('=', _notifier.evaluate, isAccent: true),
    ];

    return LayoutBuilder(
      builder: (context, constraints) {
        // Guard against zero-width on first layout pass
        if (constraints.maxWidth == 0) return const SizedBox.shrink();

        // Dynamically adjust aspect ratio so buttons look right on all screens
        final double totalSpacing = 10.0 * 3;
        final double buttonWidth = (constraints.maxWidth - totalSpacing) / 4;
        final double aspectRatio = (buttonWidth / (buttonWidth * 0.92)).clamp(0.9, 1.2);

        return GridView.builder(
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 4,
            crossAxisSpacing: 10,
            mainAxisSpacing: 10,
            childAspectRatio: aspectRatio,
          ),
          itemCount: buttons.length,
          itemBuilder: (context, index) {
            final btn = buttons[index];
            return CalculatorButton(
              text: btn.label,
              onPressed: btn.action,
              backgroundColor: btn.backgroundColor,
              textColor: btn.textColor,
              isAccent: btn.isAccent,
              isOperator: btn.isOperator,
            );
          },
        );
      },
    );
  }
}

class _ButtonConfig {
  final String label;
  final VoidCallback action;
  final Color backgroundColor;
  final Color textColor;
  final bool isAccent;
  final bool isOperator;

  const _ButtonConfig(
    this.label,
    this.action, {
    this.backgroundColor = AppColors.numKeyBackground,
    this.textColor = AppColors.textPrimary,
    this.isAccent = false,
    this.isOperator = false,
  });
}
