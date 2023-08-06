from time import sleep, ctime

def run_at(hour:int, minute:int = 0, second:int = 0) -> None:
    if type(hour) != int or type(minute) != int or type(second) != int:
        raise TypeError('Function takes integer but string given')

    hour_n = -1
    minute_n = -1
    second_n = -1

    while hour != hour_n or minute != minute_n or second != second_n:
        time_now = ctime().split(' ')
        clock_now = time_now[3].split(':')

        hour_n = int(clock_now[0])
        minute_n = int(clock_now[1])
        second_n = int(clock_now[2])

        sleep(1)
