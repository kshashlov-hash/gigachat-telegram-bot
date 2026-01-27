class ElectricCircuit:
    def __init__(self, voltage, resistance):
        """Конструктор инициализации"""
        self.voltage = voltage
        self.resistance = resistance

    @classmethod
    def copy(cls, other):
        """Конструктор копирования"""
        return cls(other.voltage, other.resistance)

    def info(self):
        """Формирование строки с информацией"""
        return (f"Напряжение: {self.voltage} В, "
                f"Сопротивление: {self.resistance} Ом")

    def calculate_current(self):
        """Вычислить ток по закону Ома"""
        if self.resistance == 0:
            return float('inf')
        return self.voltage / self.resistance


class WorkCalculator(ElectricCircuit):
    def __init__(self, voltage, resistance, time_seconds):
        """Конструктор класса-потомка"""
        super().__init__(voltage, resistance)
        self.time_seconds = time_seconds

    def calculate_work(self):
        """Вычислить работу, выполненную резистором"""
        if self.resistance == 0:
            return float('inf')
        current = self.calculate_current()
        return (current ** 2) * self.resistance * self.time_seconds

    def info(self):
        """Дополненная информация об объекте"""
        base_info = super().info()
        return f"{base_info}, Время: {self.time_seconds} с"


# Пример использования
if __name__ == "__main__":
    u = float(input("Введите напряжение (В): "))
    r = float(input("Введите сопротивление (Ом): "))
    t = float(input("Введите время работы (с): "))

    device = WorkCalculator(u, r, t)

    print("\nИнформация об объекте:")
    print(device.info())

    print(f"Ток: {device.calculate_current():.3f} А")
    print(f"Работа резистора: {device.calculate_work():.3f} Дж")