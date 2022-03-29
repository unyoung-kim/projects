# Interest Points and Feature Descriptors

Design and implement interest point detection, feature descriptor extraction, feature matching, and apply those functions to the task of object detection. 
After matching descriptors between a template image of an object and a test image containing an example of the same object category, the code predicts the location (bounding box) of the object in the test image.

## Sample Outputs

<p align="middle">
  <img src="images/img1.png" width="300" />
</p>

<p align="middle">
  <img src="images/img2.png" width="300" />
</p>

## Functions & Design Choices

- **Harris Corner Detector**
  1. Apply Gaussian Filter
  2. Apply Sobel Gradients
  3. For each pixel, consider a (4*scale+1)×(4*scale+1) window to compute Harris cornerness value 
  4. For each pixel, apply nonmaximum suppression over (2*scale+1) ×(2*scale+1) window 
  5. Select the highest 2% of points for maximum threshold 

  The Harris Corner Value, R, could be computed as following
  <img src="images/img3.png" width="200" />
  
- **Feature Descriptor**
  1. Implement a SIFT-like feature descriptor by binning orientation energy in spatial cells surrounding an interest point
  2. 3 x 3 spatial grid consisting of cell of a set width (see below) surrounding an interest point, marked
   by () in the diagram below.  Using 8 orientation bins, spaced evenly in [pi,-pi] yields a feature vector with 3 * 3 * 8 = 72 dimensions. 
  3. Each grid with width = 3, Total dimension 27x27
  
- **Feature Matching**
  1. Compute the Euclidean distance of the direction magnitude for every interest point of the test image. 
  2. The score of each match is computed by d1/d2 (d1: closest distance, d2: 2nd closest distance)
   
- **Hough Transform**
- **Object Detection**
