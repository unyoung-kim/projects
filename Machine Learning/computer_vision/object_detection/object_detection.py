import numpy as np
from edge_detection import *
from cmath import pi

"""
   INTEREST POINT OPERATOR 

   Implement a Harris corner detector 

   Arguments:
      image       - a grayscale image in the form of a 2D numpy array
      max_points  - maximum number of interest points to return
      scale       - (optional, for your use only) scale factor at which to
                    detect interest points
      mask        - (optional, for your use only) foreground mask constraining
                    the regions to extract interest points
   Returns:
      xs          - numpy array of shape (N,) containing x-coordinates of the
                    N detected interest points (N <= max_points)
      ys          - numpy array of shape (N,) containing y-coordinates
      scores      - numpy array of shape (N,) containing a real-valued
                    measurement of the relative strength of each interest point
                    Greater scores indicate a stroner detector response
"""
def find_interest_points(image, max_points = 200, scale = 1.0, mask = None):
   # check that image is grayscale
   assert image.ndim == 2, 'image should be grayscale'
   ##########################################################################
   # TODO: YOUR CODE HERE

   # 1. Set the variables
   harris_constant = 0.05
   scale = int(scale) *2

   y_size = image.shape[0]
   x_size = image.shape[1]
   corner_list = np.zeros([y_size, x_size])

   image = denoise_gaussian(image)

   # 2. Compute the gradient
   dy, dx = sobel_gradients(image)
   Ixx = dx**2
   Ixy = dx*dy
   Iyy = dy**2

   # 3. For each pixel, consider a 2*scale+1 window around it and compute the cornerness function.
   # for y in range(int(scale), y_size-scale):
   #    for x in range(scale, x_size-scale):
   for y in range(0, y_size):
      for x in range(0, x_size):      
         window_Ixx = Ixx[y-scale : y+scale+1, x-scale : x+scale+1]
         window_Ixy = Ixy[y-scale : y+scale+1, x-scale : x+scale+1]
         window_Iyy = Iyy[y-scale : y+scale+1, x-scale : x+scale+1]

         Sum_xx = window_Ixx.sum()
         Sum_xy = window_Ixy.sum()
         Sum_yy = window_Iyy.sum()

         determinant = (Sum_xx * Sum_yy) - (Sum_xy**2)
         trace = Sum_xx + Sum_yy

         r = determinant - harris_constant * (trace**2)

         corner_list[y][x] = r

   # 4. Apply non-max suppression across 3x3 window
   for y in range(1, y_size-1):
      for x in range(1, x_size-1):

         window = corner_list[y-1:y+2, x-1:x+2]
         if window.max() != corner_list[y][x]:
            corner_list[y][x] = 0

   # 4. Compute Threshold (Try changing this parameter)
   threshold = np.quantile(corner_list, 0.98)

   # If there are more than 200 points, modify the theshold
   interest_points = corner_list > threshold
   count = interest_points.sum()
   if count > max_points:
      threshold = np.quantile(corner_list, 1- (max_points/(y_size * x_size)))

   # 6. Find all pixels that exceed the threshold and are local maxima
   scores = []
   xs = []
   ys = []

   for i in range(y_size):
      for j in range(x_size):
         if corner_list[i,j] > threshold:
            xs.append(j)
            ys.append(i)
            scores.append(corner_list[y,x])

   xs = np.array(xs)
   ys = np.array(ys)
   scores = np.array(scores)
   #raise NotImplementedError('find_interest_points')
   ##########################################################################
   return xs, ys, scores

"""
  Converts Orientation into index (helper function for feature descriptor)
  Argument:
      orientation: Angle between -pi to pi

   Returns:
      index between 0-7. 
"""

def orientation_to_index(orientation):

   if -pi <= orientation < -(3*pi/4):
      return 0    
   elif -(3*pi)/4 <= orientation < -(pi/2):
      return 1
   elif -(pi)/2 <= orientation < -(pi/4):
      return 2
   elif -(pi)/4 <= orientation < 0:
      return 3
   elif 0 <= orientation < pi/4:
      return 4
   elif pi/4 <= orientation < pi/2:
      return 5
   elif pi/2 <= orientation < (3*pi)/4:
      return 6
   else:
      return 7

#When given the center of the grid, compute the sum of orientation magnitude over 9x9 kernal
def ninexnine_orientation(mag, theta, x,y):
   b=[-4,-3,-2,-1,0,1,2,3,4]
   a=[-4,-3,-2,-1,0,1,2,3,4]

   theta = np.array(theta)
   mag = np.array(mag)

   grids = []
   orientation_sum = [0,0,0,0,0,0,0,0]

   for i in range(len(b)):
      for j in range(len(a)):
         grids.append([b[i],a[j]])

   for i in grids:
      y_coor = int(i[0]+y)
      x_coor = int(i[1]+x)
      if y_coor >= theta.shape[0] or x_coor >= theta.shape[1]:
         orientation = 0
         magnitude = 0
      else:
         orientation = orientation_to_index(theta[y_coor,x_coor])
         magnitude = mag[y_coor, x_coor]

      orientation_sum[orientation] += magnitude
   
   return orientation_sum

"""
   FEATURE DESCRIPTOR 

   SIFT-like feature descriptor by binning orientation energy
   in spatial cells surrounding an interest point.

   A reasonable default design is to consider a 3 x 3 spatial grid consisting
   of cell of a set width (see below) surrounding an interest point, marked
   by () in the diagram below.  Using 8 orientation bins, spaced evenly in
   [-pi,pi), yields a feature vector with 3 * 3 * 8 = 72 dimensions.

             ____ ____ ____
            |    |    |    |
            |    |    |    |
            |____|____|____|
            |    |    |    |
            |    | () |    |
            |____|____|____|
            |    |    |    |
            |    |    |    |
            |____|____|____|

                 |----|
                  width

  Arguments:
      image    - a grayscale image in the form of a 2D numpy
      xs       - numpy array of shape (N,) containing x-coordinates
      ys       - numpy array of shape (N,) containing y-coordinates
      scale    - scale factor

   Returns:
      feats    - a numpy array of shape (N,K), containing K-dimensional
                 feature descriptors at each of the N input locations
                 (using the default scheme suggested above, K = 72)
"""
def extract_features(image, xs, ys, scale = 1.0):
   # check that image is grayscale
   assert image.ndim == 2, 'image should be grayscale'
   ##########################################################################
   # TODO: YOUR CODE HERE

   # 1. Compute orientation and magnitude for each pixels
   dy, dx = sobel_gradients(image)
   theta = np.arctan(np.divide(dy, dx, out=np.zeros(dy.shape), where=dx!=0))
   mag = np.sqrt((dy**2) + (dx**2))
   K = int((2*scale+1)**2 * 8)

   y_size = image.shape[0]
   x_size = image.shape[1]

   feats = np.zeros([len(xs), K])

   # 2. For each interest points, assign 9x9 grid
   for i in range(len(xs)):
      x = xs[i]
      y = ys[i]

      b = np.arange(-scale, scale+1)
      a = np.arange(-scale, scale+1)

      grids = []

      for j in range(len(b)):
         for k in range(len(a)):
            grids.append([b[j],a[k]])
      
      #For each cells in the grid, find the orientation and magnitude
      for q in range(len(grids)):
         grid = grids[j]
         y_grid = int(y+(grid[0]*9))
         x_grid = int(x+(grid[1]*9))
         
         magnitude_sum = ninexnine_orientation(mag, theta, x_grid, y_grid)

         feats[i][q*8:(q+1)*8] = magnitude_sum

   #raise NotImplementedError('extract_features')
   ##########################################################################
   return feats

"""
DISTANCE

Helper function for Feature matching. Computes distance between two orientation vectors

Arguments:
   feat1 - (8,) array containing orientation of an interest point
   feat2 - (8,) array containing orientation of an interest point
"""
def distance(feat1, feat2):
   # Calculate the distance of 8 orientation bins
   dist = 0 
   for i in range(72):
      dist += (feat1[i]-feat2[i])**2
   
   # Square root for distance
   dist = dist**(1.0/2)

   return dist


"""
   FEATURE MATCHING 

   Given two sets of feature descriptors, extracted from two different images,
   compute the best matching feature in the second set for each feature in the
   first set.

   Arguments:
      feats0   - a numpy array of shape (N0, K), containing N0 K-dimensional
                 feature descriptors (generated via extract_features())
      feats1   - a numpy array of shape (N1, K), containing N1 K-dimensional
                 feature descriptors (generated via extract_features())
      scores0  - a numpy array of shape (N0,) containing the scores for the
                 interest point locations at which feats0 was extracted
                 (generated via find_interest_point())
      scores1  - a numpy array of shape (N1,) containing the scores for the
                 interest point locations at which feats1 was extracted
                 (generated via find_interest_point())

   Returns:
      matches  - a numpy array of shape (N0,) containing, for each feature
                 in feats0, the index of the best matching feature in feats1
      scores   - a numpy array of shape (N0,) containing a real-valued score
                 for each match
"""
def match_features(feats0, feats1, scores0, scores1):
   ##########################################################################
   # TODO: YOUR CODE HERE
   
   # 1. Find the number of interest points for both images
   num0 = feats0.shape[0]
   num1 = feats1.shape[0]

   # 2. For each feature descriptor in feats0, compare with those in feats1
   # Find two lowest distance for each feature descriptor in feats0 to compute the distance ratio
   distance1 = 100000000000
   distance2 = 100000000000
   matches = []
   scores = []

   for i in range(num0):
      for j in range(num1):

         dist = distance(feats0[i], feats1[j])
         
         if dist < distance1:
            distance2 = distance1
            distance1 = dist
            index1 = j
            
         elif dist < distance2:
            distance2 = dist
            
      matches.append(int(index1))
      if distance2 == 0:
         scores.append(0)
      else:
         scores.append(distance1/distance2)

      index1=0
      distance1=100000000000
      distance2=100000000000
   
   matches = np.array(matches)
   scores = np.array(scores)

   #raise NotImplementedError('match_features')
   ##########################################################################
   return matches, scores


def correct_match_pdf(distance_ratio):
   if 0.2<=distance_ratio <=0.3:
      return 0.05
   elif 0.3<=distance_ratio <=0.4:
      return 0.25
   elif 0.4<=distance_ratio <=0.5:
      return 0.29
   elif 0.5<=distance_ratio <=0.6:
      return 0.18
   elif 0.6<=distance_ratio <=0.7:
      return 0.09
   elif 0.7<=distance_ratio <=0.8:
      return 0
   elif 0.8<=distance_ratio <=0.9:
      return 0
   else:
      return 0
      
"""
   HOUGH TRANSFORM 

   Assuming two images of the same scene are related primarily by
   translational motion, use a predicted feature correspondence to
   estimate the overall translation vector t = [tx ty].

   In order to accumulate votes, discretize the translation parameter space into bins.

   Arguments:
      xs0     - numpy array of shape (N0,) containing x-coordinates of the
                interest points for features in the first image
      ys0     - numpy array of shape (N0,) containing y-coordinates of the
                interest points for features in the first image
      xs1     - numpy array of shape (N1,) containing x-coordinates of the
                interest points for features in the second image
      ys1     - numpy array of shape (N1,) containing y-coordinates of the
                interest points for features in the second image
      matches - a numpy array of shape (N0,) containing, for each feature in
                the first image, the index of the best match in the second
      scores  - a numpy array of shape (N0,) containing a real-valued score
                for each pair of matched features

   Returns:
      tx      - predicted translation in x-direction between images
      ty      - predicted translation in y-direction between images
      votes   - a matrix storing vote tallies; this output is provided for
                your own convenience and you are free to design its format
"""
def hough_votes(xs0, ys0, xs1, ys1, matches, scores):
   ##########################################################################
   # TODO: YOUR CODE HERE
   votes = []

   # 1. For each pair of interest points, record the translation vector and its weights
   for i in range(len(xs0)):
      x0, y0 = xs0[i], ys0[i]
      x1, y1 = xs1[matches[i]], ys1[matches[i]]

      ty = 5 * round((y1-y0)/5)
      tx = 5 * round((x1-x0)/5)
      
      voted = False 
      for vote in votes:

         if vote[0] == ty and vote[1] == tx:
            vote[2] += correct_match_pdf(scores[i])
            voted = True
            break
      
      if voted == False:
         if correct_match_pdf(scores[i]) != 0 and tx>=0 and ty >= 0:
            votes.append([ty, tx, correct_match_pdf(scores[i])])

   # 2. Find the translation vector that has the highest votes
   tallies = 0
   for vote in votes:
      if vote[2] > tallies:
         tallies = vote[2]
         ty = vote[0]
         tx = vote[1]

   # 3. Find tx and ty value with the highest vote. 
   votes = np.array(votes)
   # max_vote = votes[:,2].max()
 
   max_vote = 0
   for vote in votes:
      if vote[2] > max_vote:
         max_vote = vote[2]
         ty = vote[0]
         tx = vote[1]

   
   # raise NotImplementedError('hough_votes')
   ##########################################################################
   return tx, ty, votes

"""
    OBJECT DETECTION 

    Implement an object detection system which, given multiple object
    templates, localizes the object in the input image by feature
    matching and hough voting.

    Arguments:
        template_images - a list of gray scale images. Each image is in the
                          form of a 2d numpy array which is cropped to tightly
                          cover the object.

        template_masks  - a list of binary masks having the same shape as the
                          template_image.  Each mask is in the form of 2d numpy
                          array specyfing the foreground mask of object in the
                          corresponding template image.

        test_img        - a gray scale test image in the form of 2d numpy array
                          containing the object category of interest.

    Returns:
         bbox           - a numpy array of shape (4,) specifying the detected
                          bounding box in the format of
                             (x_min, y_min, x_max, y_max)

"""
def object_detection(template_images, template_masks, test_img):
   ##########################################################################
   # TODO: YOUR CODE HERE
   x_min = 0
   y_min = 0
   x_max = 0
   y_max = 0

   for i in range(len(template_images)):
      template_count = i
      # 1. Leave only the foreground of the template image
      template_img = template_images[i] * template_masks[i]

      template_y = np.array(template_images[i]).shape[0]
      template_x = np.array(template_images[i]).shape[1]

      # 2. Extract Interest Point from template and test images
      xs_template, ys_template, scores_template = find_interest_points(template_img, scale=1.0)
      xs_test, ys_test, scores_test = find_interest_points(test_img, scale=1.0)

      # 3. Extract Feature Descriptors of the interest points of both template and test images
      template_features = extract_features(template_img ,xs_template, ys_template, scale=1.0)
      test_features= extract_features(test_img, xs_test, ys_test, scale=1.0)

      # 4. Match features of template and test Images
      matches, scores = match_features(template_features, test_features, scores_template, scores_test)

      # 5. Implement Hough Transformation
      tx, ty, votes = hough_votes(xs_template, ys_template, xs_test, ys_test, matches, scores)

      x_min += tx-(template_x)/2
      y_min += ty-(template_y)/2
      x_max += tx+(template_x)/2
      y_max += ty+(template_y)/2

   #6. Average the coordiantes of the box
   x_min /= (i+1)
   y_min /= (i+1)
   x_max /= (i+1)
   y_max /= (i+1)

   bbox = (x_min, y_min, x_max, y_max)

   #raise NotImplementedError('object_detection')
   ##########################################################################
   return bbox
