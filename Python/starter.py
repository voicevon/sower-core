from global_const import app_config

import sys
sys.path.append(app_config.path.text_color)
from color_print import const



    # '(\ (\'

    # '( -.-)'
    
    # 'o__(")(")'
welcome=[]
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
for w in welcome:
    print('                      ' +const.print_color.control.bold + const.print_color.fore.yellow + const.print_color.background.blue + w + const.print_color.control.reset)
print(const.print_color.control.reset)

if True:
    from manager import SowerManager
    system = SowerManager()
    system.start()
    while True:
        system.main_loop()

    # '(\_______/)'
    # ' (= ^.^ =)'
    # '  (")_(")'


