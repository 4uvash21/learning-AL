import numpy as np
import cv2
import gdown
from matplotlib import pyplot
# Команда обеспечивает вывод графиков в Google Colaboratory
%matplotlib inline


gdown.download('Введите сылку на фотографию jpg файла', None, quiet=True)

# Загрузка изображения
img = cv2.imread('./название jpg файла')
img2 = img.copy()

# загрузка каскада Хаара для поиска лиц
classifier_face = cv2.CascadeClassifier(cv2.data.haarcascades+ "haarcascade_frontalface_default.xml")


# загрузка каскада Хаара для поиска глаз
classifier_eye = cv2.CascadeClassifier(cv2.data.haarcascades+ "haarcascade_eye.xml")

# выполнение распознавания лиц
bboxes = classifier_face.detectMultiScale(img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

glasses_url = 'фотография очков jpg файла'
glasses_output = './название jpg файла '
gdown.download(glasses_url, glasses_output, quiet=True)
glasses = cv2.imread(glasses_output, cv2.IMREAD_UNCHANGED)

# Функция для замены белого фона на прозрачность
def replace_white_with_transparency(image):
    # Проверка наличия альфа-канала
    if image.shape[2] == 3:
        # Добавление альфа-канала
        image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

    # Заменяем белый цвет (255, 255, 255) на прозрачный (0 в альфа-канале)
    white = np.all(image[:, :, :3] == [255, 255, 255], axis=2)
    image[white, 3] = 0

    return image

# Замена белого фона на прозрачность
glasses = replace_white_with_transparency(glasses)

# формирование круг вокруг каждого обнаруженного лица
for box in bboxes:
    # формирование координат
    x, y, width, height = box
    center = (x + width//2, y+ height//2)
    axes = (width//2, height//2)
    angle = 0
    # рисование круга
    cv2.ellipse(img2, center, axes, angle, 0, 360, (255, 0, 0), 2)

    face = img2[y:y + height, x:x + width] # найденная область с лицом

    # выполнение распознавания глаз
    eyes = classifier_eye.detectMultiScale(face)
    if len(eyes) > 0:
        eye_sizes = [(w_eye * h_eye) for (x_eye, y_eye, w_eye, h_eye) in eyes]
        avg_eye_size = sum(eye_sizes) / len(eye_sizes) if len(eye_sizes) > 0 else 0

    for (x_eye,y_eye,w_eye,h_eye) in eyes:

        # определяем центр круга
        center = (x + x_eye + w_eye//2, y + y_eye + h_eye//2)

        # вычисляем радиус окружности (подобран эмпирическим путем)
        radius = int(0.4 * np.sqrt(avg_eye_size))
        color = (0, 255, 0) # цвет в RGB (интенсивность цветов красный-зеленый-синий от 0 до 255)
        thickness = 2 # толщина линии
        # рисуем круг
        cv2.circle(face, center, radius, color, thickness)

    mask = np.zeros_like(face)
    for (x_eye,y_eye,w_eye,h_eye) in eyes:
        center = (x_eye + w_eye//2, y_eye + h_eye//2)
        radius = int(0.4 * np.sqrt(avg_eye_size))
        cv2.circle(mask, center, radius, (255, 255, 255), -1)
    face_blurred = cv2.GaussianBlur(face, (99,99), 30)
    np.copyto(face, face_blurred, where=mask == 0)

    # Наложение очков
    if len(eyes) == 2:
        # Масштабирование очков до размера области между глазами
        x_eye1, y_eye1, w_eye1, h_eye1 = eyes[0]
        x_eye2, y_eye2, w_eye2, h_eye2 = eyes[1]
        if x_eye1 > x_eye2:
            x_eye1, x_eye2 = x_eye2, x_eye1
            w_eye1, w_eye2 = w_eye2, w_eye1
        eye_width = int((x_eye2 + w_eye2 - x_eye1) * 1.1)
        glasses_resized = cv2.resize(glasses, (eye_width, int(glasses.shape[0] * (eye_width / glasses.shape[1]))))

        # Проверка наличия альфа-канала
        if glasses_resized.shape[2] == 4:
            alpha_glasses = glasses_resized[:, :, 3] / 255.0
            for c in range(0, 3):
                img2[y + min(y_eye1, y_eye2):y + min(y_eye1, y_eye2) + glasses_resized.shape[0],
                     x + x_eye1:x + x_eye1 + glasses_resized.shape[1], c] = (
                    alpha_glasses * glasses_resized[:, :, c] +
                    (1 - alpha_glasses) * img2[y + min(y_eye1, y_eye2):y + min(y_eye1, y_eye2) + glasses_resized.shape[0],
                                              x + x_eye1:x + x_eye1 + glasses_resized.shape[1], c]
                )
        else:
            img2[y + min(y_eye1, y_eye2):y + min(y_eye1, y_eye2) + glasses_resized.shape[0],
                 x + x_eye1:x + x_eye1 + glasses_resized.shape[1]] = glasses_resized

fig, (ax1, ax2) = pyplot.subplots(1, 2, figsize=(12, 8))
ax1.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
ax1.xaxis.set_ticks([])
ax1.yaxis.set_ticks([])
ax1.set_title('Исходное изображение')

ax2.imshow(cv2.cvtColor(img2, cv2.COLOR_BGR2RGB))
ax2.xaxis.set_ticks([])
ax2.yaxis.set_ticks([])
ax2.set_title('Замыленное лицо и крутые очки')

pyplot.show()
