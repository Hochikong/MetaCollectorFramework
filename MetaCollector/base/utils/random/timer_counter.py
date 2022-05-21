from datetime import datetime, timedelta


class TimerCounter(object):
    def __init__(self, max_wait_counter: int, max_time_delta: int, time_delta_type: str):
        """
        初始化计时器

        :param max_wait_counter: 内置计数器的目标最大计数值，当计数器的值大于该值，返回True并把计数器重置为0
        :param max_time_delta: 时间差，自类初始化开始到某一时刻的时间差，如果超过这个差值，返回True并把内置的时间记录更新为此刻的时间
        :param time_delta_type: 时间差单位，days、seconds、minutes、hours
        """
        self.time_delta_enum = self.get_time_delta_types()
        self.__max_count = max_wait_counter
        self.__max_time_delta = max_time_delta
        self.__time_delta_type = ''

        if time_delta_type in self.time_delta_enum:
            self.__time_delta_type = time_delta_type
        else:
            raise NotImplementedError("time_delta_type类型{}不被支持".format(time_delta_type))

        self.__counter = 0
        self.__current = datetime.now()

    @staticmethod
    def get_time_delta_types() -> list:
        return ['days', 'seconds', 'minutes', 'hours']

    def check_counter(self) -> bool:
        """
        为内置计数器增加1，如果计数器或时间超过阈值，则返回True并重置两个值，否则返回False

        :return:
        """
        self.__counter += 1
        print("Counter = {}".format(self.__counter))
        if self.counter_out_bound() or self.time_out_bound():
            self.__counter = 0
            self.__current = datetime.now()
            return True
        else:
            return False

    def counter_out_bound(self) -> bool:
        """
        如果counter的值大于阈值，返回True，否则False

        :return:
        """
        return self.__counter > self.__max_count

    def time_out_bound(self) -> bool:
        """
        如果旧的时间记录与当前时间的差值大于阈值，返回True，否则False

        :return:
        """
        delta = None
        if self.__time_delta_type == 'days':
            delta = timedelta(days=self.__max_time_delta)
        if self.__time_delta_type == 'seconds':
            delta = timedelta(seconds=self.__max_time_delta)
        if self.__time_delta_type == 'minutes':
            delta = timedelta(minutes=self.__max_time_delta)
        if self.__time_delta_type == 'hours':
            delta = timedelta(minutes=self.__max_time_delta)

        return (self.__current + delta) < datetime.now()
