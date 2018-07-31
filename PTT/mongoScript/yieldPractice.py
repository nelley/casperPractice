#-*- encoding=utf8 -*-
'''
an example for looping yield multiple value

'''
import math

def is_prime(number):
    if number > 1:
        if number == 2:
            return True
        if number % 2 == 0:
            return False
        for current in range(3, int(math.sqrt(number) + 1), 2):
            if number % current == 0:
                return False
        return True
    return False

def get_primes(number):
    while True:
        print('here is get primes=%s' % number)
        if is_prime(number):
            yield number, True    #通過yield將number與執行權返回給solve_number_10
        number += 1         #第二次for循環時會從這裡開始執行,number會保持上次的狀態（3）,然後加到4後回到While迴圈

def solve_number_10():
    total = 2
    for next_prime, x in get_primes(3):    #for循環得到返回值3,然後for循環請求下一個值
        if next_prime < 20:
            print 'next_prime=%s, boolean=%s' % (next_prime, x)
            total += next_prime
        else:
            print(total)
            return


if __name__ == '__main__':

    solve_number_10()



