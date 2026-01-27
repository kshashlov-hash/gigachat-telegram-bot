# ========== ЛАБОРАТОРНАЯ РАБОТА №3 ==========
# Установи библиотеки: pip install numpy opencv-python matplotlib scikit-learn

import os
import numpy as np
import cv2
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

print("=== Начало выполнения лабораторной работы ===")

# ========== ЗАДАНИЕ 1: ФИЛЬТРАЦИЯ ИЗОБРАЖЕНИЯ ==========
print("\n--- Задание 1: Фильтрация изображения ---")

# 1. Загрузка изображения в оттенках серого
print("1. Загрузка изображения 'fig.jpg'...")
img = cv2.imread('fig.jpg', cv2.IMREAD_GRAYSCALE)
if img is None:
    print("ОШИБКА: Файл 'fig.jpg' не найден!")
    # Создаём тестовое изображение если файла нет
    img = np.random.randint(0, 255, (200, 300), dtype=np.uint8)
    cv2.imwrite('fig.jpg', img)
    print("Создано тестовое изображение 'fig.jpg'")

# 2. Применение фильтров Собеля
print("2. Применение фильтров Собеля...")
sobel_x = np.array([[-1, 0, 1],
                    [-2, 0, 2],
                    [-1, 0, 1]])

sobel_y = np.array([[-1, -2, -1],
                    [0, 0, 0],
                    [1, 2, 1]])

grad_x = cv2.filter2D(img.astype(np.float32), -1, sobel_x)
grad_y = cv2.filter2D(img.astype(np.float32), -1, sobel_y)

# Сохраняем результаты
cv2.imwrite('fig_grad_x.jpg', np.abs(grad_x))
cv2.imwrite('fig_grad_y.jpg', np.abs(grad_y))
print("   Сохранены: fig_grad_x.jpg, fig_grad_y.jpg")

# 3. Величина градиента
print("3. Вычисление величины градиента...")
grad_magnitude = np.sqrt(grad_x ** 2 + grad_y ** 2)
grad_magnitude = np.uint8(255 * grad_magnitude / np.max(grad_magnitude))
cv2.imwrite('fig_grad_m.jpg', grad_magnitude)
print("   Сохранено: fig_grad_m.jpg")

# ========== ЗАДАНИЕ 2: PCA ДЛЯ АНАЛИЗА ЛИЦ ==========
print("\n--- Задание 2: PCA для анализа лиц ---")


def load_faces(path, train=True):
    """Загрузка изображений лиц"""
    images = []
    labels = []
    for i in range(1, 41):
        for j in range(1, 11):
            if train and j > 6:  # тестовые
                continue
            if not train and j <= 6:  # тренировочные
                continue
            img_path = os.path.join(path, f'{i}_{j}.png')
            if not os.path.exists(img_path):
                print(f"Предупреждение: файл {img_path} не найден")
                continue
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                img_flat = img.flatten()
                images.append(img_flat)
                labels.append(i)
    return np.array(images), np.array(labels)


# Загрузка датасета
print("1. Загрузка датасета лиц...")
train_path = 'D:/PyCharm 2025.2.3/Face_dataset'

# Проверяем существование папки
if not os.path.exists(train_path):
    print(f"ОШИБКА: Папка '{train_path}' не найдена!")
    print("Создаем тестовый датасет...")
    os.makedirs(train_path, exist_ok=True)
    # Создаем тестовые изображения
    for i in range(1, 5):
        for j in range(1, 11):
            img = np.random.randint(0, 255, (56, 46), dtype=np.uint8)
            cv2.imwrite(os.path.join(train_path, f'{i}_{j}.png'), img)
    print("Создан тестовый датасет из 4 классов")

X_train, y_train = load_faces(train_path, train=True)
X_test, y_test = load_faces(train_path, train=False)
print(f"   Загружено: {X_train.shape[0]} тренировочных и {X_test.shape[0]} тестовых изображений")

# ========== СОБСТВЕННАЯ РЕАЛИЗАЦИЯ PCA ==========
print("\n2. Реализация PCA...")


def pca_manual(X, n_components):
    """Собственная реализация PCA"""
    # Центрирование данных
    mean_face = np.mean(X, axis=0)
    X_centered = X - mean_face

    # Ковариационная матрица
    cov = np.cov(X_centered, rowvar=False)

    # Собственные значения и векторы
    eigenvalues, eigenvectors = np.linalg.eigh(cov)

    # Сортируем по убыванию
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    # Выбираем первые n компонент
    components = eigenvectors[:, :n_components]

    return mean_face, components, eigenvalues


# Выполняем PCA
mean_face, eigenfaces, eigenvalues = pca_manual(X_train, n_components=100)

# Сохраняем среднее лицо
mean_img = mean_face.reshape(56, 46).astype(np.uint8)
cv2.imwrite('mean.png', mean_img)
print("   Сохранено среднее лицо: mean.png")

# Сохраняем первые 3 собственных лица
for i in range(3):
    eigenface = eigenfaces[:, i]
    # Нормализация
    eigenface_img = 255 * (eigenface - np.min(eigenface)) / (np.max(eigenface) - np.min(eigenface))
    eigenface_img = eigenface_img.reshape(56, 46).astype(np.uint8)
    cv2.imwrite(f'{i + 1}.png', eigenface_img)
print("   Сохранены собственные лица: 1.png, 2.png, 3.png")

# ========== РЕКОНСТРУКЦИЯ ИЗОБРАЖЕНИЯ ==========
print("\n3. Реконструкция изображения 7_2.png...")


def reconstruct(face, mean_face, eigenfaces, n_components):
    """Реконструкция лица с использованием PCA"""
    face_centered = face - mean_face
    weights = np.dot(face_centered, eigenfaces[:, :n_components])
    reconstructed = mean_face + np.dot(weights, eigenfaces[:, :n_components].T)
    return reconstructed


def mse(original, reconstructed):
    """Вычисление MSE"""
    return np.mean((original - reconstructed) ** 2)


# Загружаем изображение для реконструкции
test_img_path = os.path.join(train_path, '7_2.png')
if os.path.exists(test_img_path):
    test_img = cv2.imread(test_img_path, cv2.IMREAD_GRAYSCALE)
    test_img_flat = test_img.flatten()

    # Реконструируем с разным количеством компонент
    for n in [3, 100]:
        reconstructed = reconstruct(test_img_flat, mean_face, eigenfaces, n)
        rec_img = reconstructed.reshape(56, 46).astype(np.uint8)
        cv2.imwrite(f'7_2_n{n}.png', rec_img)

        # Вычисляем MSE
        mse_value = mse(test_img_flat, reconstructed)
        print(f"   Реконструкция с n={n}: сохранено 7_2_n{n}.png, MSE = {mse_value:.2f}")
else:
    print("   Изображение 7_2.png не найдено, пропускаем реконструкцию")

# ========== KNN КЛАССИФИКАЦИЯ ==========
print("\n4. Классификация методом KNN...")


def project_data(X, mean_face, eigenfaces, n_components):
    """Проецирование данных в пространство PCA"""
    X_centered = X - mean_face
    return np.dot(X_centered, eigenfaces[:, :n_components])


print("   Точность классификации:")
print("   n\\k |   k=1   |   k=3   ")
print("   " + "-" * 25)

# Проецируем данные и классифицируем
for n in [3, 100]:
    accuracies = []

    # Проецируем данные
    X_train_proj = project_data(X_train, mean_face, eigenfaces, n)
    X_test_proj = project_data(X_test, mean_face, eigenfaces, n)

    for k in [1, 3]:
        knn = KNeighborsClassifier(n_neighbors=k)
        knn.fit(X_train_proj, y_train)
        y_pred = knn.predict(X_test_proj)
        acc = accuracy_score(y_test, y_pred)
        accuracies.append(acc)

    print(f"   {n:3d} | {accuracies[0]:.4f}  | {accuracies[1]:.4f}")

# ========== БОНУС: ВИЗУАЛИЗАЦИЯ (дополнительно) ==========
print("\n--- Бонус: Визуализация результатов ---")

# Создаём визуализацию если установлен matplotlib
try:
    import matplotlib.pyplot as plt

    # 1. Визуализация градиентов
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))

    axes[0, 0].imshow(img, cmap='gray')
    axes[0, 0].set_title('Оригинальное изображение')
    axes[0, 0].axis('off')

    axes[0, 1].imshow(cv2.imread('fig_grad_x.jpg', cv2.IMREAD_GRAYSCALE), cmap='gray')
    axes[0, 1].set_title('Горизонтальный градиент (Sobel X)')
    axes[0, 1].axis('off')

    axes[1, 0].imshow(cv2.imread('fig_grad_y.jpg', cv2.IMREAD_GRAYSCALE), cmap='gray')
    axes[1, 0].set_title('Вертикальный градиент (Sobel Y)')
    axes[1, 0].axis('off')

    axes[1, 1].imshow(cv2.imread('fig_grad_m.jpg', cv2.IMREAD_GRAYSCALE), cmap='gray')
    axes[1, 1].set_title('Величина градиента')
    axes[1, 1].axis('off')

    plt.tight_layout()
    plt.savefig('gradients_visualization.png', dpi=150)
    print("   Сохранена визуализация градиентов: gradients_visualization.png")

    # 2. Визуализация собственных лиц
    fig2, axes2 = plt.subplots(1, 4, figsize=(12, 3))

    axes2[0].imshow(mean_img, cmap='gray')
    axes2[0].set_title('Среднее лицо')
    axes2[0].axis('off')

    for i in range(3):
        eigenface_img = cv2.imread(f'{i + 1}.png', cv2.IMREAD_GRAYSCALE)
        axes2[i + 1].imshow(eigenface_img, cmap='gray')
        axes2[i + 1].set_title(f'Собственное лицо {i + 1}')
        axes2[i + 1].axis('off')

    plt.tight_layout()
    plt.savefig('eigenfaces_visualization.png', dpi=150)
    print("   Сохранена визуализация собственных лиц: eigenfaces_visualization.png")

except ImportError:
    print("   Matplotlib не установлен, пропускаем визуализацию")
    print("   Установи: pip install matplotlib")

# ========== СОХРАНЕНИЕ РЕЗУЛЬТАТОВ В ТЕКСТОВЫЙ ФАЙЛ ==========
print("\n--- Сохранение результатов ---")

with open('lab3_results.txt', 'w', encoding='utf-8') as f:
    f.write("РЕЗУЛЬТАТЫ ЛАБОРАТОРНОЙ РАБОТЫ №3\n")
    f.write("=" * 40 + "\n\n")

    f.write("1. ФИЛЬТРАЦИЯ ИЗОБРАЖЕНИЯ:\n")
    f.write(f"   - Размер изображения: {img.shape}\n")
    f.write("   - Сохраненные файлы:\n")
    f.write("     * fig_grad_x.jpg\n")
    f.write("     * fig_grad_y.jpg\n")
    f.write("     * fig_grad_m.jpg\n\n")

    f.write("2. АНАЛИЗ ЛИЦ МЕТОДОМ PCA:\n")
    f.write(f"   - Тренировочных изображений: {X_train.shape[0]}\n")
    f.write(f"   - Тестовых изображений: {X_test.shape[0]}\n")
    f.write(f"   - Размерность данных: {X_train.shape[1]}\n")
    f.write("   - Сохраненные файлы:\n")
    f.write("     * mean.png (среднее лицо)\n")
    f.write("     * 1.png, 2.png, 3.png (первые 3 собственных лица)\n\n")

    f.write("3. РЕКОНСТРУКЦИЯ ИЗОБРАЖЕНИЯ 7_2.png:\n")
    if os.path.exists(test_img_path):
        for n in [3, 100]:
            f.write(f"   - n={n}: файл 7_2_n{n}.png\n")
    f.write("\n")

    f.write("4. КЛАССИФИКАЦИЯ KNN:\n")
    f.write("   n\\k |   k=1   |   k=3   \n")
    f.write("   " + "-" * 25 + "\n")

    # Повторяем вычисления для записи
    for n in [3, 100]:
        X_train_proj = project_data(X_train, mean_face, eigenfaces, n)
        X_test_proj = project_data(X_test, mean_face, eigenfaces, n)
        accuracies = []
        for k in [1, 3]:
            knn = KNeighborsClassifier(n_neighbors=k)
            knn.fit(X_train_proj, y_train)
            y_pred = knn.predict(X_test_proj)
            acc = accuracy_score(y_test, y_pred)
            accuracies.append(acc)
        f.write(f"   {n:3d} | {accuracies[0]:.4f}  | {accuracies[1]:.4f}\n")

print("   Сохранены итоговые результаты: lab3_results.txt")
print("\n=== Лабораторная работа успешно выполнена! ===")
print("Проверь созданные файлы:")
print("- Градиенты: fig_grad_x.jpg, fig_grad_y.jpg, fig_grad_m.jpg")
print("- PCA: mean.png, 1.png, 2.png, 3.png")
print("- Реконструкции: 7_2_n3.png, 7_2_n100.png (если было исходное изображение)")
print("- Результаты: lab3_results.txt")
print("- Визуализации: gradients_visualization.png, eigenfaces_visualization.png (если установлен matplotlib)")
