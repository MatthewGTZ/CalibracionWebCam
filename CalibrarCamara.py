import os
import numpy as np
import cv2 as cv
import glob
import pickle

# Configuración del tablero de ajedrez
chessboardSize = (8, 6)  # Número de esquinas interiores del patrón (columnas, filas)
square_size = 27  # Tamaño de cada cuadrado en mm

# Criterios de terminación para cornerSubPix
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Preparar puntos 3D del mundo real
objp = np.zeros((chessboardSize[0] * chessboardSize[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:chessboardSize[0], 0:chessboardSize[1]].T.reshape(-1, 2)
objp *= square_size

# Almacenar puntos 3D y 2D de todas las imágenes
objpoints = []  # Puntos 3D en el mundo real
imgpoints = []  # Puntos 2D en las imágenes

# Ruta a las imágenes capturadas
images = glob.glob('D:/Trabajo/3dcamaras/Imagenes_cal/camara1/*.png')

# Detectar esquinas del patrón de ajedrez en las imágenes
for image_path in images:
    img = cv.imread(image_path)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Detectar esquinas del tablero de ajedrez
    ret, corners = cv.findChessboardCorners(gray, chessboardSize, None)

    if ret:
        # Refinar esquinas y almacenar puntos
        objpoints.append(objp)
        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)

        # Dibujar las esquinas en la imagen
        cv.drawChessboardCorners(img, chessboardSize, corners2, ret)
        cv.imshow('Esquinas detectadas', img)
        cv.waitKey(100)
    else:
        print(f"No se detectó el patrón en la imagen: {image_path}")

cv.destroyAllWindows()

# Calibrar la cámara
print("Calibrando la cámara...")
ret, cameraMatrix, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

# Crear la carpeta de resultados si no existe
output_folder = "D:/Trabajo/3dcamaras/ResultadosCamara1"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Guardar los resultados
pickle.dump(cameraMatrix, open(f"{output_folder}/cameraMatrix.pkl", "wb"))
pickle.dump(dist, open(f"{output_folder}/dist.pkl", "wb"))
print(f"Calibración completada. Resultados guardados en: {output_folder}")

# Mostrar los resultados
print("Matriz intrínseca (cameraMatrix):\n", cameraMatrix)
print("Coeficientes de distorsión (dist):\n", dist)

# Verificar la calibración corrigiendo una imagen
test_image = 'D:/Trabajo/3dcamaras/Imagenes_cal/camara1/img0.png'  # Cambia según tus imágenes
img = cv.imread(test_image)
h, w = img.shape[:2]
newCameraMatrix, roi = cv.getOptimalNewCameraMatrix(cameraMatrix, dist, (w, h), 1, (w, h))

# Corregir distorsión
undistorted_img = cv.undistort(img, cameraMatrix, dist, None, newCameraMatrix)

# Recortar la imagen
x, y, w, h = roi
undistorted_img = undistorted_img[y:y+h, x:x+w]

# Guardar y mostrar la imagen corregida
cv.imwrite(f"{output_folder}/undistorted_image.png", undistorted_img)
cv.imshow("Imagen corregida", undistorted_img)
cv.waitKey(0)
cv.destroyAllWindows()

# Calcular el error de reproyección
print("Calculando el error de reproyección...")
mean_error = 0
for i in range(len(objpoints)):
    imgpoints2, _ = cv.projectPoints(objpoints[i], rvecs[i], tvecs[i], cameraMatrix, dist)
    error = cv.norm(imgpoints[i], imgpoints2, cv.NORM_L2) / len(imgpoints2)
    mean_error += error
print(f"Error total de reproyección: {mean_error / len(objpoints):.5f}")
