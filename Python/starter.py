import sys
sys.path.append('/home/xm/pylib')  # for custom's jetson nano 
from terminal_font import TerminalFont



def get_welcome_a():
    welcome = []
    welcome.append('                                                           ')
    welcome.append('     (\ (\                                                 ')
    welcome.append('  *  ( -.-)   * * * * * * * * * * * * * * * * *            ')
    welcome.append('  *  O_(")(")                                    *         ')
    welcome.append('  *                 Sower and Robot                *       ')
    welcome.append('  *                     Version 0.01                  *    ')
    welcome.append('  *                                                     *  ')
    welcome.append('  *     Copyright @2020 Shandong Perfect PTE.LTD.       *  ')
    welcome.append('  *           http://voicevon.vicp.io:7005              *  ')
    welcome.append('  *                                                     *  ')
    welcome.append('  *                                                     *  ')
    welcome.append('  *                System is loading...                 *  ')
    welcome.append('  *                                                     *  ')
    welcome.append('  * * * * * * * * * * * * * * * * * * * * * * * * * * * *  ')
    welcome.append('                                                           ')
    return welcome

def get_head():
    head = []
    head.append('  *                .-"""-.                     ')
    head.append('  *               / .===. \                          ')
    head.append('  *               \/ 6 6 \/                                        ')
    head.append('  *               ( \___/ )        ')
    head.append('  *  ________ooo__ \_____/ ______________               ')
    head.append('  * /                                    \             ')
    return head

def get_legs():
    leg = []
    leg.append('     \___________________________ooo______/ ')
    leg.append('                      |  |  |   ')
    leg.append('                      |__|__|   ')
    leg.append('                      |  |  |   ')
    leg.append('                      |__|__|   ')
    leg.append("                      /-'Y'-\    ")
    leg.append('                     (__/ \__)  ')
    return leg

def get_welcome_b():
    welcome = []
    welcome.append('  * |                Sower and Robot                *       ')
    welcome.append('  * |                    Version 0.01                  *    ')
    welcome.append('  * |                                                    *  ')
    welcome.append('  * |    Copyright @2020 Shandong Perfect PTE.LTD.       *  ')
    welcome.append('  *           http://voicevon.vicp.io:7005              *  ')
    welcome.append('  *                                                     *  ')
    welcome.append('  *                                                     *  ')
    welcome.append('  *                System is loading...                 *  ')
    welcome.append('  *                                                     *  ')
    welcome.append('  * * * * * * * * * * * * * * * * * * * * * * * * * * * *  ')
    # xx = welcome.extend (get_legs()    )                                                  
    return welcome
    
def print_welcome(welcome):
    # print(welcome)
    for w in welcome:
        print('                      ' + TerminalFont.Color.Control.bold + TerminalFont.Color.Fore.yellow + TerminalFont.Color.Background.blue + w + TerminalFont.Color.Control.reset)
    print(TerminalFont.Color.Control.reset)


if True:
    # welcome = get_welcome_a()
    print_welcome(get_head())
    print_welcome(get_welcome_b())
    print_welcome(get_legs())

    print('sys.version = %s' % sys.version)
    print('sys.executable = %s' % sys.executable)
    print('-----------------------------------------------------------')

    from manager import SowerManager
    system = SowerManager()
    system.spin()
    # '(\_______/)'
    # ' (= ^.^ =)'
    # '  (")_(")'


