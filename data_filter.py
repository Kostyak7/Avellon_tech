import statistics as st


class AbstractDataFilter:
    def __init__(self, data: list):
        self.init_data = data

    def set_data(self, data_: list) -> None:
        self.init_data = data_

    def set_params(self, *args, **kwargs): ...

    def get_data(self): ...


class ArithmeticMeanFilter(AbstractDataFilter):
    def __init__(self, data: list):
        super().__init__(data)
        self.buffer_size = 10

    def set_params(self, buffer_size: int) -> None:
        self.buffer_size = buffer_size

    def get_data(self) -> list:
        data = self.init_data[:]
        sum_el = 0
        for i in range(self.buffer_size):
            sum_el += self.init_data[i]
        mv = self.buffer_size // 2
        for i in range(len(self.init_data) - self.buffer_size):
            data[i + mv] = sum_el / self.buffer_size
            sum_el += self.init_data[i + self.buffer_size] - self.init_data[i]
        return data


class MedianFilter(AbstractDataFilter):
    def __init__(self, data: list):
        super().__init__(data)
        self.buffer_size = 7

    def set_params(self, buffer_size: int) -> None:
        self.buffer_size = buffer_size

    def get_data(self) -> list:
        data = self.init_data[:]
        buffer = [data[0]] * self.buffer_size
        for i in range(len(data)):
            buffer = buffer[1:]
            buffer.append(data[i])
            data[i] = st.median_grouped(buffer)
        return data


class ExpEasyMeanFilter(AbstractDataFilter):
    def __init__(self, data: list):
        super().__init__(data)
        self.s_k = 0.2
        self.max_k = 0.9
        self.d = 1.5

    def set_params(self, s_k: float, max_k: float, d: float) -> None:
        self.s_k = s_k
        self.max_k = max_k
        self.d = d

    def get_data(self) -> list:
        data = self.init_data[:]
        fit = data[0]
        for i in range(len(data)):
            k = self.s_k if (abs(data[i] - fit) < self.d) else self.max_k
            fit += (data[i] - fit) * k
            data[i] = fit
        return data


class NormaliseFilter(AbstractDataFilter):
    def __init__(self, data: list):
        super().__init__(data)
        self.buffer_size = 7
        self.s_k = 0.2
        self.max_k = 0.9
        self.d = 1.5

    def set_params(self, buffer_size: int, s_k: float, max_k: float, d: float) -> None:
        self.buffer_size = buffer_size
        self.s_k = s_k
        self.max_k = max_k
        self.d = d

    def get_data(self) -> list:
        data = self.init_data[:]
        median_filter = MedianFilter(data)
        median_filter.set_params(self.buffer_size)
        exp_filter = ExpEasyMeanFilter(median_filter.get_data())
        exp_filter.set_params(self.s_k, self.max_k, self.d)
        return exp_filter.get_data()


class KalmanFilter(AbstractDataFilter):
    def __init__(self, data: list):
        super().__init__(data)
        self.q = 0.25
        self.r = 0.7

    def set_params(self, q: float, r: float) -> None:
        pass

    def get_data(self) -> list:
        data = self.init_data[:]
        accumulated_error = 1
        kalman_adc_old = 0
        for i in range(len(data)):
            old_input = data[i] * 0.382 + kalman_adc_old * 0.618 if abs(data[i] - kalman_adc_old) / 50 > 0.25 else kalman_adc_old
            old_error_all = (accumulated_error ** 2 + self.q ** 2) ** (1 / 2)
            H = old_error_all ** 2 / (old_error_all ** 2 + self.r ** 2)
            kalman_adc = old_input + H * (data[i] - old_input)
            accumulated_error = ((1 - H) * old_error_all ** 2) ** (1 / 2)
            kalman_adc_old = kalman_adc
        return data
