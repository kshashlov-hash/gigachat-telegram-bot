import math


def calculate_harmonics():
    w = 14.45

    u_list = [0.169, 0.321, 0.277, 0.212, 0.135, 0.060, -0.004, -0.049, -0.071, -0.070, -0.053]
    f_list = [0, 0, 0, 0, 0, 0, 3.14, 3.14, 3.14, 3.14, 3.14]

    t_inputs = list(map(float, input("Значения t через пробел: ").split()))

    results = []

    for t in t_inputs:
        val = u_list[0]
        for n in range(1, 11):
            val += u_list[n] * math.cos(n * w * t + f_list[n])
        results.append(val)

    return results


final_values = calculate_harmonics()
print("U:", [round(v, 4) for v in final_values])
