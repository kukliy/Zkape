import random
import time
from threading import Thread
from zkape import ZAT
import re


if __name__ == "__main__":


    with open('data/wallet.txt', 'r') as f:
        private_keys = [i for i in [w.strip() for w in f] if i != '']
    with open('data/proxy.txt', 'r') as f:
        proxy = [i for i in [p.strip() for p in f] if i != '']
    with open('data/config.txt', 'r') as f:
        try:
            config = [i for i in [p.strip() for p in f] if i != '']
            interval = re.findall(r'[0-9]+', config[0])

            start = int(interval[0])
            stop = int(interval[1])

        except Exception as e:
            print(f"\033[31m{e}\033[0m")
            print('The interval will be = 10,30\n')
            start = 10
            stop = 30


    choice = 2
    if len(proxy)==0:
        input('You have not provided any proxies.\nPress ENTER to continue, in which case YOUR proxy IP will be used '
              'for all accounts')
        proxy = None
        choice = 1

    elif len(proxy) !=len(private_keys):

        input(f'The number of proxies (\033[31m{len(proxy)}\033[0m) does not match the number of private_keys (\033[31m{len(private_keys)}\033[0m).\nTo '
              f'continue press '
              f'ENTER, '
              f'in this case 1 '
              'proxy will be used for all accounts')
        proxy = proxy[0]
        choice = 1

    choice_do = int(input('What you want to do:\n1 - Check eligibility\n2 - Clime tokens\n3 - Swap $ZAT to $ETH\n4 - Clime tokens and '
                      'swap to $ETH\n'))

    if int(choice_do) not in range(1, 5):
        print('Incorrect number')
        exit()


    zat_s = []
    for i in range(0, len(private_keys)):

        if choice == 1:
            zat_s.append(ZAT(private_keys[i], proxy))

        else:
            zat_s.append(ZAT(private_keys[i], proxy[i]))


    if choice_do == 1:

        for zat in zat_s:
            if choice ==1:
                zat.clime_data()
                time.sleep(2)
            else:
                t = Thread(target=zat.clime_data)
                t.start()
                time.sleep(1)


    elif choice_do == 2:

        for zat in zat_s:
            if choice ==1:
                zat.clime()
                time.sleep(5)
            else:
                t = Thread(target=zat.clime)
                t.start()
                time.sleep(random.randint(start, stop))

    elif choice_do == 3:

        for zat in zat_s:
            if choice == 1:
                zat.swap()
                time.sleep(2)
            else:
                t = Thread(target=zat.swap())
                t.start()
                time.sleep(random.randint(start, stop))


    elif choice_do == 4:

        for zat in zat_s:
            if choice == 1:
                zat.all()

            else:
                t = Thread(target=zat.all())
                t.start()
                time.sleep(random.randint(start, stop))












    exit()







