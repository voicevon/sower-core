from global_const import app_config

import sys
sys.path.append(app_config.path.text_color)
from color_print import const


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
        print('                      ' + const.print_color.control.bold + const.print_color.fore.yellow + const.print_color.background.blue + w + const.print_color.control.reset)
    print(const.print_color.control.reset)


if True:
    # welcome = get_welcome_a()
    print_welcome(get_head())
    print_welcome(get_welcome_b())
    print_welcome(get_legs())


    from manager import SowerManager
    system = SowerManager()
    system.setup()
    while True:
        system.main_loop()

    # '(\_______/)'
    # ' (= ^.^ =)'
    # '  (")_(")'


