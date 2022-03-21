from cmath import pi
import numpy as np

"""
   Mirror an image about its border.
   Arguments:
      image - a 2D numpy array of shape (sx, sy)
      wx    - a scalar specifying width of the top/bottom border
      wy    - a scalar specifying width of the left/right border
   Returns:
      img   - a 2D numpy array of shape (sx + 2*wx, sy + 2*wy) containing
              the original image centered in its interior and a surrounding
              border of the specified width created by mirroring the interior
"""
def mirror_border(image, wx = 1, wy = 1):
   assert image.ndim == 2, 'image should be grayscale'
   sx, sy = image.shape
   # mirror top/bottom
   top    = image[:wx:,:]
   bottom = image[(sx-wx):,:]
   img = np.concatenate( \
      (top[::-1,:], image, bottom[::-1,:]), \
      axis=0 \
   )
   # mirror left/right
   left  = img[:,:wy]
   right = img[:,(sy-wy):]
   img = np.concatenate( \
      (left[:,::-1], img, right[:,::-1]), \
      axis=1 \
   )
   return img


"""
   Pad an image with zeros about its border.
   Arguments:
      image - a 2D numpy array of shape (sx, sy)
      wx    - a scalar specifying width of the top/bottom border
      wy    - a scalar specifying width of the left/right border
   Returns:
      img   - a 2D numpy array of shape (sx + 2*wx, sy + 2*wy) containing
              the original image centered in its interior and a surrounding
              border of zeros
"""
def pad_border(image, wx = 1, wy = 1):
   assert image.ndim == 2, 'image should be grayscale'
   sx, sy = image.shape
   img = np.zeros((sx+2*wx, sy+2*wy))
   img[wx:(sx+wx),wy:(sy+wy)] = image
   return img


"""
   Remove the border of an image.
   Arguments:
   image - a 2D numpy array of shape (sx, sy)
      wx    - a scalar specifying width of the top/bottom border
      wy    - a scalar specifying width of the left/right border
   Returns:
      img   - a 2D numpy array of shape (sx - 2*wx, sy - 2*wy), extracted by
              removing a border of the specified width from the sides of the
              input image
"""
def trim_border(image, wx = 1, wy = 1):
   assert image.ndim == 2, 'image should be grayscale'
   sx, sy = image.shape
   img = np.copy(image[wx:(sx-wx),wy:(sy-wy)])
   return img


"""
   Return an approximation of a 1-dimensional Gaussian filter.
   The returned filter approximates:
   g(x) = 1 / sqrt(2 * pi * sigma^2) * exp( -(x^2) / (2 * sigma^2) )
   for x in the range [-3*sigma, 3*sigma]
"""
def gaussian_1d(sigma = 1.0):
   width = np.ceil(3.0 * sigma)
   x = np.arange(-width, width + 1)
   g = np.exp(-(x * x) / (2 * sigma * sigma))
   g = g / np.sum(g)          # normalize filter to sum to 1 ( equivalent
   g = np.atleast_2d(g)       # to multiplication by 1 / sqrt(2*pi*sigma^2) )
   return g


"""
Convolve a 2D image with a 2D filter.
   Arguments:
      image  - a 2D numpy array
      filt   - a 1D or 2D numpy array, with odd dimensions
      mode   - 'zero': preprocess using pad_border or 'mirror': preprocess using 
mirror_border.

   Returns:
      result - a 2D numpy array of the same shape as image, containing the
               result of convolving the image with filt
"""
def conv_2d(image, filt, mode='zero'):
   # make sure that both image and filter are 2D arrays
   assert image.ndim == 2, 'image should be grayscale'
   filt = np.atleast_2d(filt)

   # 1. Check Filter and Image Size 
   x_image ,y_image =image.shape[0], image.shape[1]
   x_filter, y_filter = filt.shape[0], filt.shape[1]

   # 2. Check mode and preprocess the image accordingly
   if mode == 'zero':
      image = pad_border(image, wx = (x_filter//2) + 1, wy = (y_filter//2)+1)
   elif mode == 'mirror':
      image = mirror_border(image, wx = (x_filter//2) + 1, wy = (y_filter//2)+1)
   else:
      raise ValueError('conv_2d: Invalid mode')

   # 3. Create Output
   result = np.zeros((x_image, y_image))

   # 4. Implement convolution
   for x in range(x_image):
      for y in range(y_image):
         result[x,y] = (filt * image[x: x+x_filter , y : y+y_filter]).sum()

   return result


"""
   GAUSSIAN DENOISING
   Denoise an image by convolving it with a 2D Gaussian filter.
   Convolve the input image with a 2D filter G(x,y) defined by:
   G(x,y) = 1 / sqrt(2 * pi * sigma^2) * exp( -(x^2 + y^2) / (2 * sigma^2) )

   Arguments:
      image - a 2D numpy array
      sigma - standard deviation of the Gaussian

   Returns:
      img   - denoised image, a 2D numpy array of the same shape as the input
"""
def denoise_gaussian(image, sigma = 1.0):

   # 1. Create a 2D Gaussian filter
   width = np.ceil(3.0 * sigma)
   x = np.arange(-width, width + 1)
   gx = np.exp(-(x * x) / (2 * sigma * sigma))
   y = np.arange(-width, width+1)
   y = np.reshape(y, (y.shape[0],1))
   gy = np.exp(-(y * y) / (2 * sigma * sigma))
   g_2d = gx * gy
   g_2d = g_2d / np.sum(g_2d) 
   
   # 2. Implement convolution using the 2D Gaussian Filter
   img = conv_2d(image, g_2d)

   return img


"""
    BILATERAL DENOISING 
    Denoise an image by applying a bilateral filter
  
    Arguments:
        image       - input image
        sigma_s     - spatial param (pixels), spatial extent of the kernel,
                       size of the considered neighborhood.
        sigma_r     - range param (not normalized, a propotion of 0-255),
                       denotes minimum amplitude of an edge

    Returns:
        img   - denoised image, a 2D numpy array of the same shape as the input
"""
def denoise_bilateral(image, sigma_s=1, sigma_r=25.5):
    assert image.ndim == 2, 'image should be grayscale'

   #  # 1. Create Bi-lateral Filter
    reg_constant=1e-8
    gaussian = lambda r2, sigma: (np.exp( -0.5*r2/sigma**2 )*3).astype(int)*1.0/3.0
    width = int(np.ceil(3.0 * sigma_s))
    
    wgt_sum = np.ones( image.shape )*reg_constant
    x_image ,y_image =image.shape[0], image.shape[1]
    img = np.zeros((x_image, y_image))
    for shft_x in range(-width,width+1):
        for shft_y in range(-width,width+1):
            # compute the spatial weight
            w = gaussian( shft_x**2+shft_y**2, sigma_s )
            # shift by the offsets
            off = np.roll(image, [shft_y, shft_x], axis=[0,1] )
            # compute the value weight
            Iw = w*gaussian( (off-image)**2, sigma_r )
            # accumulate the results
            img += off*Iw
            wgt_sum += Iw
    
    img = img/wgt_sum

    return img


"""
   SMOOTHING AND DOWNSAMPLING 
   Smooth an image by applying a gaussian filter, followed by downsampling with a 
factor k.

   Arguments:
     image - a 2D numpy array
     downsample_factor - an integer specifying downsample rate

   Returns:
     result - downsampled image, a 2D numpy array with spatial dimension reduced
"""
def smooth_and_downsample(image, downsample_factor = 2):
    ##########################################################################
    # TODO: YOUR CODE HERE
    result = denoise_gaussian(image, downsample_factor/pi)
    result = result[::downsample_factor,::downsample_factor]
    #raise NotImplementedError('smooth_and_downsample')
    ##########################################################################
    return result


"""
   SOBEL GRADIENT OPERATOR (5 Points)
   Compute an estimate of the horizontal and vertical gradients of an image
   by applying the Sobel operator.
   The Sobel operator estimates gradients dx(horizontal), dy(vertical), of
   an image I as:
         [ 1  0  -1 ]
   dx =  [ 2  0  -2 ] (*) I
         [ 1  0  -1 ]
         [  1  2  1 ]
   dy =  [  0  0  0 ] (*) I
         [ -1 -2 -1 ]
   where (*) denotes convolution.

   Arguments:
      image - a 2D numpy array

   Returns:
      dx    - gradient in x-direction at each point
              (a 2D numpy array, the same shape as the input image)
      dy    - gradient in y-direction at each point
              (a 2D numpy array, the same shape as the input image)
"""
def sobel_gradients(image):

   x_filt = np.array([[1,0,-1],[2,0,-2],[1,0,-1]])
   dx = conv_2d(image, x_filt, mode = 'zero')
   y_filt = np.array([[1,2,1],[0,0,0],[-1,-2,-1]])
   dy = conv_2d(image, y_filt, mode = 'zero')
 
   return dx, dy


"""
   NONMAXIMUM SUPPRESSION 

   Arguments:
      mag    - a 2D numpy array, containing edge strength (magnitude)
      theta  - a 2D numpy array, containing edge direction in [0, 2*pi)

   Returns:
      nonmax - a 2D numpy array, containing edge strength (magnitude), where
               pixels that are not a local maximum of strength along an
               edge have been suppressed (assigned a strength of zero)
"""
def nonmax_suppress(mag, theta):

   x_mag, y_mag = mag.shape[0], mag.shape[1]
   nonmax = np.copy(mag)

   for x in range(1, x_mag-1):
      for y in range(1, y_mag-1):
         direction = theta[x,y]%pi
         if 0<=direction<=(pi/8) or ((7*pi)/8)<direction<=pi:
            sig_x, sig_y = 1,0
         elif (pi/8)<direction<=((3*pi)/8):
            sig_x, sig_y = -1,1
         elif ((3*pi)/8)<direction<=((5*pi)/8):
            sig_x, sig_y = 0,1
         else:
            sig_x, sig_y = 1,-1
         # Compare the edge strength with two points that are perpendicular to the edge direction
         check1, check2 = mag[x+sig_x, y+sig_y], mag[x-sig_x, y-sig_y]
         if nonmax[x,y] > check1 and nonmax[x,y] > check2:
            nonmax[x+sig_x, y+sig_y] = 0
            nonmax[x-sig_x, y-sig_y] = 0
         else:
            nonmax[x,y]=0

   nonmax = trim_border(nonmax)
   nonmax = pad_border(nonmax)
  
   return nonmax


"""
   HYSTERESIS EDGE LINKING 

   Given an edge magnitude map (mag) which is thinned by nonmaximum suppression,
   first compute the low threshold and high threshold so that any pixel below
   low threshold will be thrown away, and any pixel above high threshold is
   a strong edge and will be preserved in the final edge map. The pixels that
   fall in-between are considered as weak edges. We then add weak edges to
   true edges if they connect to a strong edge along the gradient direction.
   Since the thresholds are highly dependent on the statistics of the edge
   magnitude distribution, consider features like maximum edge
   magnitude or the edge magnitude histogram in order to compute the high
   threshold.  

   For the edge linking, the weak edges caused by true edges will connect up
   with a neighbouring strong edge pixel.  To track theses edges, we
   investigate the 8 neighbours of strong edges.  Once we find the weak edges,
   located along strong edges' gradient direction, we will mark them as strong
   edges.  

   Arguments:
     nonmax - a 2D numpy array, containing edge strength (magnitude) which is 
thined by nonmaximum suppression
     theta  - a 2D numpy array, containing edeg direction in [0, 2*pi)

   Returns:
     edge   - a 2D numpy array, containing edges map where the edge pixel is 1 and 
0 otherwise.
"""

def hysteresis_edge_linking(nonmax, theta):

   count_zero = (nonmax==0).sum()
   total = nonmax.shape[0] * nonmax.shape[1]
   threshold = count_zero/total
   high_threshold = np.quantile(nonmax, 1- ((1-threshold)/6))
   low_threshold = np.quantile(nonmax, threshold+ ((1-threshold)/6))
   x_nonmax, y_nonmax = nonmax.shape[0], nonmax.shape[1]
   edge = np.copy(nonmax)
   # 1. Edges below low threshold - Drop (0)
   #    Edges above high threshold - Mark as strong edges (1)
   #    Anything in between - Mark as weak edges (0.5)
   for x in range(x_nonmax):
      for y in range(y_nonmax):
         if edge[x,y] <= low_threshold:
            edge[x,y] = 0
         elif edge[x,y] >= high_threshold:
            edge[x,y] = 1
         else:
            edge[x,y] = 0.5
   
   # 2. Edge linking
   for x in range(1, x_nonmax-1):
      for y in range(1, y_nonmax-1):
         if edge[x,y] == 1:
      
            direction = theta[x,y]%pi
            if 0<=direction<=(pi/8) or ((7*pi)/8)<direction<=pi:
               sig_x, sig_y = 0,1
            elif (pi/8)<direction<=((3*pi)/8):
               sig_x, sig_y = 1,-1
            elif ((3*pi)/8)<direction<=((5*pi)/8):
               sig_x, sig_y = 1,0
            else:
               sig_x, sig_y = -1,1
            
            check1, check2 = edge[x+sig_x, y+sig_y], edge[x-sig_x, y-sig_y]
            
            if check1 == 0.5:
               edge[x+sig_x, y+sig_y] = 1
            if check2 == 0.5:
               edge[x-sig_x, y-sig_y] = 1
   for x in range(1, x_nonmax-1):
      for y in range(1, y_nonmax-1):
         if edge[x,y] == 0.5:
            edge[x,y] = 0
   
   return edge


"""
   CANNY EDGE DETECTOR

   Given an input image:
   (1) Compute gradients in x- and y-directions at every location using the
       Sobel operator.  See sobel_gradients() above.
   (2) Estimate edge strength (gradient magnitude) and direction.
   (3) Perform nonmaximum suppression of the edge strength map, thinning it
       in the direction perpendicular to that of a local edge.
       See nonmax_suppress() above.
   (4) Compute the high threshold and low threshold of edge strength map
       to classify the pixels as strong edges, weak edges and non edges.
       Then link weak edges to strong edges
   Return the original edge strength estimate (max), the edge
   strength map after nonmaximum suppression (nonmax) and the edge map
   after edge linking (edge)

   Arguments:
      image    - a 2D numpy array

   Returns:
      mag      - a 2D numpy array, same shape as input, edge strength at each pixel
      nonmax   - a 2D numpy array, same shape as input, edge strength after 
nonmaximum suppression
      edge     - a 2D numpy array, same shape as input, edges map where edge pixel 
is 1 and 0 otherwise.
"""
def canny(image):

   # 1. Find the sobel gradient
   dx, dy = sobel_gradients(image)

   # 2. Compute the Edge strength and direction
   mag = np.sqrt((dx**2) + (dy**2))
   theta = np.arctan(dx/dy)
   
   # 3. Perform nonmax suppresion
   nonmax = nonmax_suppress(mag, theta)
   
   # 4. Perform Edge Linking 
   edge = hysteresis_edge_linking(nonmax, theta)
   
   return mag, nonmax, edge