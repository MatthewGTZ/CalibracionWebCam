import cv2 as cv

chessboardSize = (8, 6)  # Ajusta según tu patrón
image_path = "D:/Trabajo/3dcamaras/Imagenes_cal/camara1/img0.png"  # Cambia por una imagen de prueba

img = cv.imread(image_path)
if img is None:
    print("Error: No se pudo cargar la imagen.")
else:
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    cv.imshow("gris",gray)
    ret, corners = cv.findChessboardCorners(gray, chessboardSize, None)

    if ret:
        print("¡Patrón detectado!")
        cv.drawChessboardCorners(img, chessboardSize, corners, ret)
        cv.imshow("Patrón encontrado", img)
        cv.waitKey(0)
    else:
        print("No se detectó el patrón en la imagen.")
        cv.waitKey(0)
cv.destroyAllWindows()