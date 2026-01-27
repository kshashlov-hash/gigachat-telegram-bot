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
        """Формирование строки с информацией об объекте"""
        return (f"Напряжение: {self.voltage} В, "
                f"Сопротивление: {self.resistance} Ом")

    def calculate_current(self):
        """Функция обработки значений — вычисление тока"""
        if self.resistance == 0:
            return float('inf')  # защита от деления на 0
        return self.voltage / self.resistance


# Пример использования
if __name__ == "__main__":
    # Создание объекта
    u = float(input("Введите напряжение (В): "))
    r = float(input("Введите сопротивление (Ом): "))

    circuit = ElectricCircuit(u, r)

    print("\nИнформация об объекте:")
    print(circuit.info())

    print(f"Ток в цепи: {circuit.calculate_current():.3f} А")

    # Пример создания копии
    circuit_copy = ElectricCircuit.copy(circuit)
    print("\nКопия объекта:")
    print(circuit_copy.info())