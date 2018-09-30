# Image manipulation
#
# You'll need Python 2.7 and must install these packages:
#
#   numpy, PyOpenGL, Pillow
#
# Note that file loading and saving (with 'l' and 's') do not work on
# Mac OSX, so you will have to change 'imgFilename' below, instead, if
# you want to work with different images.
#
# Note that images, when loaded, are converted to the YCbCr
# colourspace, and that you should manipulate only the Y component of
# each pixel when doing intensity changes.


import sys, os, numpy, math

try:  # Pillow
    from PIL import Image
except:
    print 'Error: Pillow has not been installed.'
    sys.exit(0)

try:  # PyOpenGL
    from OpenGL.GLUT import *
    from OpenGL.GL import *
    from OpenGL.GLU import *
except:
    print 'Error: PyOpenGL has not been installed.'
    sys.exit(0)

# Globals

windowWidth = 600  # window dimensions
windowHeight = 800

localHistoRadius = 5  # distance within which to apply local histogram equalization

# Current image

imgDir = 'images'
imgFilename = 'mandrill.png'

currentImage = Image.open(os.path.join(imgDir, imgFilename)).convert('YCbCr').transpose(Image.FLIP_TOP_BOTTOM)
tempImage = None

# File dialog (doesn't work on Mac OSX)

if sys.platform != 'darwin':
    import Tkinter, tkFileDialog

    root = Tkinter.Tk()
    root.withdraw()


# Apply brightness and contrast to tempImage and store in
# currentImage.  The brightness and constrast changes are always made
# on tempImage, which stores the image when the left mouse button was
# first pressed, and are stored in currentImage, so that the user can
# see the changes immediately.  As long as left mouse button is held
# down, tempImage will not change.

def applyBrightnessAndContrast(brightness, contrast):
    width = currentImage.size[0]
    height = currentImage.size[1]

    srcPixels = tempImage.load()
    dstPixels = currentImage.load()

    # YOUR CODE HERE
    # applyBrightnessAndContrast(255 * diffX / float(windowWidth), 1 + diffY / float(windowHeight))
    for x in range(width):
        for y in range(height):
            rgb = YCbCr2RGB(srcPixels[x, y])
            new_r = cut_off_255(rgb[0]*contrast + brightness)
            new_g = cut_off_255(rgb[1]*contrast + brightness)
            new_b = cut_off_255(rgb[2]*contrast + brightness)
            new_rgb = tuple((new_r, new_g, new_b))
            ycbcr = RGB2YCbCr(new_rgb)
            dstPixels[x, y] = ycbcr

    print 'adjust brightness = %f, contrast = %f' % (brightness, contrast)


# Perform local histogram equalization on the current image using the given radius.

def performHistoEqualization(radius):
    pixels = currentImage.load()
    width = currentImage.size[0]
    height = currentImage.size[1]

    # YOUR CODE HERE
    for x in range(width):
        for y in range(height):
            # pixels[x, y] = RGB2YCbCr(pixels[x, y])
            n_r = 0
            intensity = (pixels[x, y][0] - 16) / float(235 - 16)
            # pixel = pixels[x, y]
            if ((x - radius + 1) >= 0) and ((y - radius + 1) >= 0) and (x + radius <= width) and (y + radius <= height):
                for i in range(x-radius+1, x+radius-1, 1):
                    for j in range(y-radius+1, y+radius-1, 1):
                        if ((pixels[i, j][0] - 16) / float(235 - 16)) <= intensity:
                            n_r = n_r + 1
                pi = list(pixels[x, y])
                pi[0] = n_r * 256 / ((radius + 1)*(radius + 1))- 1
                pixels[x, y] = tuple(pi)
                # pixels[x, y] = YCbCr2RGB(pixels[x, y])

            #corner and edge case(not finished)
            # if ((x - radius + 1) < 0) or ((y - radius + 1) >= 0) or (x + radius <= width) or (y + radius <= height):
            #     for i in range(x, x + radius,1):
            #         for j in range(y, y+radius, 1):
            #             if ((pixels[i, j][0] - 16) / float(235 - 16) <= intensity):
            #                 n_r = n_r + 1
            #     pi = list(pixels[x, y])
            #     pi[0] = n_r * 256 / ((radius+1) * (radius+1)) - 1
            #     pixels[x, y] = tuple(pi)
            #     pixels[x, y] = YCbCr2RGB(pixels[x, y])
            # elif x + radius > width or y + radius > height:
            #     for i in range(x - radius + 1, width-1,1):
            #         for j in range(y - radius + 1, height - 1, 1):
            #             if ((pixels[i, j][0] - 16) / float(235 - 16) <= intensity):
            #                 n_r = n_r + 1
            #     pi = list(pixels[x, y])
            #     pi[0] = n_r * 256 / ((radius+1) * (radius+1)) - 1
            #     pixels[x, y] = tuple(pi)
            #     pixels[x, y] = YCbCr2RGB(pixels[x, y])

    print 'perform local histogram equalization with radius %d' % radius


# Scale the tempImage by the given factor and store it in
# currentImage.  Use backward projection.  This is called when the
# mouse is moved with the right button held down.

def scaleImage(factor):
    width = currentImage.size[0]
    height = currentImage.size[1]

    srcPixels = tempImage.load()
    dstPixels = currentImage.load()
    newWidth = int(width * factor)
    newHeight = int(height * factor)
    print("new dimension: " + str(newWidth) + "x" + str(newHeight))

    # if we are scaling the image smaller, we fill the remaining pixels with white
    if factor < 1:
        for x in range(width):
            for y in range(newHeight, height):
                dstPixels[x, y] = (235, 128, 128) # white in YCbCr
        for y in range(height):
            for x in range(newWidth, width):
                dstPixels[x, y] = (235, 128, 128)

    for x in range(min(width, newWidth)):
        for y in range(min(height, newHeight)):
            srcX = int(x / factor)
            srcY = int(y / factor)
            dstPixels[x, y] = srcPixels[srcX, srcY]

    print 'scale image by %f' % factor


def RGB2YCbCr(rgb):
    r = rgb[0] / float(255)
    g = rgb[1] / float(255)
    b = rgb[2] / float(255)

    y = r * 0.299 + g * 0.587 + b * 0.114
    pb = r * -0.168736 - g * 0.331264 + b * 0.5
    pr = r * 0.5 - g * 0.418688 - b * 0.081312

    y = int(16 + 219 * y)
    cb = int(128 + 224 * pb)
    cr = int(128 + 224 * pr)

    return (y, cb, cr)


def YCbCr2RGB(ycrcb):
    y = ycrcb[0]
    cb = ycrcb[1]
    cr = ycrcb[2]

    y = (y - 16) / float(219)
    pb = (cb - 128) / float(112)
    pr = (cr - 128) / float(112)

    r = wrap_around(int((y + pr * 0.701) * 255))
    g = wrap_around(int((y - pb * 0.17206 - pr * 0.35705) * 255))
    b = wrap_around(int((y + pb * 0.886) * 255))
    return (r, g, b)


def wrap_around(value):
    if value < 0:
        return value + 255
    elif value > 255:
        return value -255
    else:
        return value

def cut_off_255(value):
    if value > 255:
        return 255
    elif value < 0:
        return 0
    else:
        return value

# Set up the display and draw the current image

def display():
    # Clear window

    glClearColor(1, 1, 1, 0)
    glClear(GL_COLOR_BUFFER_BIT)

    # rebuild the image

    img = currentImage.convert('RGB')

    width = img.size[0]
    height = img.size[1]

    # Find where to position lower-left corner of image

    baseX = (windowWidth - width) / 2
    baseY = (windowHeight - height) / 2

    glWindowPos2i(baseX, baseY)

    # Get pixels and draw

    imageData = numpy.array(list(img.getdata()), numpy.uint8)

    glDrawPixels(width, height, GL_RGB, GL_UNSIGNED_BYTE, imageData)

    glutSwapBuffers()


# Handle keyboard input

def keyboard(key, x, y):
    global localHistoRadius

    if key == '\033':  # ESC = exit
        sys.exit(0)

    elif key == 'l':
        if sys.platform != 'darwin':
            path = tkFileDialog.askopenfilename(initialdir=imgDir)
            if path:
                loadImage(path)

    elif key == 's':
        if sys.platform != 'darwin':
            outputPath = tkFileDialog.asksaveasfilename(initialdir='.')
            if outputPath:
                saveImage(outputPath)

    elif key == 'h':
        performHistoEqualization(localHistoRadius)

    elif key in ['+', '=']:
        localHistoRadius = localHistoRadius + 1
        print 'radius =', localHistoRadius

    elif key in ['-', '_']:
        localHistoRadius = localHistoRadius - 1
        if localHistoRadius < 1:
            localHistoRadius = 1
        print 'radius =', localHistoRadius

    else:
        print 'key =', key  # DO NOT REMOVE THIS LINE.  It will be used during automated marking.

    glutPostRedisplay()


# Load and save images.
#
# Modify these to load to the current image and to save the current image.
#
# DO NOT CHANGE THE NAMES OR ARGUMENT LISTS OF THESE FUNCTIONS, as
# they will be used in automated marking.


def loadImage(path):
    global currentImage

    currentImage = Image.open(path).convert('YCbCr').transpose(Image.FLIP_TOP_BOTTOM)


def saveImage(path):
    global currentImage

    currentImage.transpose(Image.FLIP_TOP_BOTTOM).convert('RGB').save(path)


# Handle window reshape


def reshape(newWidth, newHeight):
    global windowWidth, windowHeight

    windowWidth = newWidth
    windowHeight = newHeight

    glutPostRedisplay()


# Mouse state on initial click

button = None
initX = 0
initY = 0


# Handle mouse click/release

def mouse(btn, state, x, y):
    global button, initX, initY, tempImage

    if state == GLUT_DOWN:
        tempImage = currentImage.copy()
        button = btn
        initX = x
        initY = y
    elif state == GLUT_UP:
        tempImage = None
        button = None

    glutPostRedisplay()


# Handle mouse motion

def motion(x, y):
    if button == GLUT_LEFT_BUTTON:

        diffX = x - initX
        diffY = y - initY

        applyBrightnessAndContrast(255 * diffX / float(windowWidth), 1 + diffY / float(windowHeight))

    elif button == GLUT_RIGHT_BUTTON:

        initPosX = initX - float(windowWidth) / 2.0
        initPosY = initY - float(windowHeight) / 2.0
        initDist = math.sqrt(initPosX * initPosX + initPosY * initPosY)
        if initDist == 0:
            initDist = 1

        newPosX = x - float(windowWidth) / 2.0
        newPosY = y - float(windowHeight) / 2.0
        newDist = math.sqrt(newPosX * newPosX + newPosY * newPosY)

        scaleImage(newDist / initDist)

    glutPostRedisplay()


# Run OpenGL

glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(windowWidth, windowHeight)
glutInitWindowPosition(50, 50)

glutCreateWindow('imaging')

glutDisplayFunc(display)
glutKeyboardFunc(keyboard)
glutReshapeFunc(reshape)
glutMouseFunc(mouse)
glutMotionFunc(motion)

glutMainLoop()
