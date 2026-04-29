class KeyboardKey:
    Backspace = 8        # Backspace键    
    Tab = 9                # Tab键
    Return = 13            # 回车键
    Pause = 19            # PAUSE键

    Lshift = 16            # SHIFT键        
    Control = 17        # CONTROL键
    Menu = 18            # ALT键
    CapsLock = 20        # CAPS LOCK键(大小写键)
    Escape = 27            # Esc键
    Space = 32            # 空格键
    PgUp = 33            # Page Up键
    PgDown = 34            # Page Down键
    End = 35            # End键
    Home = 36            # Home键

    Left = 37            # 方向左键(←)
    Up = 38                # 方向上键(↑)
    Right = 39            # 方向右键(→)
    Down = 40            # 方向下键(↓)
    Insert = 45            # Insert键
    Delete = 46            # Delete键

    Num0 = 48                # 数字0(大键盘不是小键盘，48~57同)
    Num1 = 49                # 数字1
    Num2 = 50                # 数字2
    Num3 = 51                # 数字3
    Num4 = 52                # 数字4
    Num5 = 53                # 数字5
    Num6 = 54                # 数字6
    Num7 = 55                # 数字7
    Num8 = 56                # 数字8
    Num9 = 57                # 数字9

    A = 65                # A键
    B = 66                # B键
    C = 67                # C键
    D = 68                # D键
    E = 69                # E键                
    F = 70                # F键
    G = 71                # G键
    H = 72                # H键
    I = 73                # I键
    J = 74                # J键
    K = 75                # K键
    L = 76                # L键
    M = 77                # M键
    N = 78                # N键
    O = 79                # O键
    P = 80                # P键
    Q = 81                # Q键
    R = 82                # R键
    S = 83                # S键
    T = 84                # T键
    U = 85                # U键
    V = 86                # V键
    W = 87                # W键
    X = 88                # X键
    Y = 89                # Y键
    Z = 90                # Z键

    Numpad0 = 96        # 数字0(小键盘，96~111同)
    Numpad1 = 97        # 数字1
    Numpad2 = 98        # 数字2
    Numpad3 = 99        # 数字3
    Numpad4 = 100        # 数字4
    Numpad5 = 101        # 数字5
    Numpad6 = 102        # 数字6
    Numpad7 = 103        # 数字7
    Numpad8 = 104        # 数字8
    Numpad9 = 105        # 数字9
    Multiply = 106        # 乘号键(×)
    Add = 107            # 加号键(+)

    Subtract = 109        # 减号键(-)
    Decimal = 110        # 小数点(.)
    Divide = 111        # 除法键(/)
    F1 = 112            # 功能键F1
    F2 = 113            # 功能键F2
    F3 = 114            # 功能键F3
    F4 = 115            # 功能键F4
    F5 = 116            # 功能键F5
    F6 = 117            # 功能键F6
    F7 = 118            # 功能键F7
    F8 = 119            # 功能键F8
    F9 = 120            # 功能键F9
    F10 = 121            # 功能键F10
    F11 = 122            # 功能键F11
    F12 = 123            # 功能键F12
    F13 = 124            # 功能键F13

    NumLock = 144        # Num Lock键
    Scroll = 145        # Scroll Lock键

    Semicolon = 186        # : ; 键
    Equals = 187        # = + 键
    Comma = 188            # , < 键
    Minus = 189            # - _ 键
    Period = 190        # . > 键
    Slash = 191            # / ? 键
    Grave = 192            # ` ~ 键

    Lbracket = 219        # [ { 键
    Backslash = 220        # \ | 键
    Rbracket = 221        # ] } 键
    Apostraphe = 222    # ' " 键
    

class MouseKey:
    Left = -99         # 鼠标左键
    Right = -98     # 鼠标右键
    Middle = -97     # 鼠标中键


class GamepadKey:     # Xbox layout
    A = 1                        # A键
    B = 2                        # B键
    X = 3                        # X键
    Y = 4                        # Y键
    Up = 5                    # 向上方向键
    Down = 6                # 向下方向键
    Left = 7                # 向左方向键
    Right = 8                # 向右方向键
    LS = 9                        # LS键
    RS = 10                        # RS键
    LB = 11                        # LB键
    RB = 12                        # RB键
    View = 13                    # VIEW键
    Menu = 14                    # MENU键
    

class GamepadAxis:
    LSX = 0                     # 左摇杆X轴
    LSY = 1                     # 左摇杆Y轴
    RSX = 2                     # 右摇杆X轴
    RSY = 3                     # 右摇杆Y轴
    LT = 4                      # 左触发器
    RT = 5                      # 右触发器
    

class ValueType:
    Bool = 0
    Float = 1
    

class TriggerType:
    Release = 'release'
    Press = 'press'
    Value = 'value'
    Hold = 'hold'
    Combination = 'combination'
    Repeat = 'repeat'