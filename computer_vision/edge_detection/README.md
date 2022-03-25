# Convolution, Filtering, Denoising & Canny Edge Detection

By using only low-level primitives in numpy, implement basic convolution, denoising, and edge detection operations from scratch.


 ## Sample Input & Output Images
 Input & Output Images
<p align="middle">
  <img src="/images/image1_in.png" width="100" />
  <img src="/images/img1_out.png" width="100" /> 
</p>

<p align="middle">
  <img src="/images/image2_in.jpg" width="100" />
  <img src="/images/image2_out.jpg" width="100" /> 
</p>

<p align="middle">
  <img src="/images/image3_in.jpg" width="100" />
  <img src="/images/image3_out.jpg" width="100" /> 
</p>

<p align="middle">
  <img src="/images/image4_in.jpg" width="100" />
  <img src="/images/image4_out.png" width="100" /> 
</p>

## Functions
- **Convolution**
  - Code for the nested loops of the convolustions using only basic loop constructs, array indexing, multiplication, and addition operators.
- **Filtering (Gaussian & Bilateral)**
  - Gaussian filter 
    - Defined by G(x,y) = 1 / sqrt(2 * pi * sigma^2) * exp( -(x^2 + y^2) / (2 * sigma^2) )
  - Bilateral filter
    - BF[I]_p = 1/(W_p)sum_{q in S}G_s(||p-q||)G_r(|I_p-I_q|)I_q
    - 1/(W_p) is normalize factor, G_s(||p-q||) is spatial Guassian term, G_r(|I_p-I_q|) is range Guassian term.
- **Smoothing and Downsampling**
  - Smooth images with low pass filter, e.g, gaussian filter, to remove the high frequency signal that would otherwise causes aliasing in the downsampled outcome.
  - Downsample smoothed images by keeping every kth samples.
- **Sobel Gradient Operator**
  - The Sobel operator estimates gradients dx(horizontal), dy(vertical), of an image I as:
<pre>
         [ 1  0  -1 ]
   dx =  [ 2  0  -2 ] (*) I
         [ 1  0  -1 ]

         [  1  2  1 ]
   dy =  [  0  0  0 ] (*) I
         [ -1 -2 -1 ]
 </pre>
 
- **Edge Detection**
  - **Nonmax Suppression**
    - With an estimate of edge strength (mag) and direction (theta) at each pixel, suppress edge responses that are not a local maximum along the direction perpendicular to the edge
  - **Edge Linking and Hysterisis Thresholding**
    - Given an edge magnitude map (mag) which is thinned by nonmaximum suppression, first compute the low threshold and high threshold so that any pixel below low threshold will be thrown away, and any pixel above high threshold is a strong edge and will be preserved in the final edge map. The pixels that
      fall in-between are considered as weak edges. We then add weak edges to true edges if they connect to a strong edge along the gradient direction.
  - **Canny Edge Detection**
    1) Compute gradients in x- and y-directions at every location using the Sobel operator.
    2) Estimate edge strength (gradient magnitude) and direction.
    3) Perform nonmaximum suppression of the edge strength map, thinning it in the direction perpendicular to that of a local edge.
    4) Compute the high threshold and low threshold of edge strength map to classify the pixels as strong edges, weak edges and non edges. Then link weak edges to strong edges
