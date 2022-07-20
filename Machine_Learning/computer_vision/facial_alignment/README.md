# Face Detection & Alignment
### **1. Face Detection**
- Compare 3 different face detection models and evaluate/compare their performances
  - Haar Cascade Face recognition (OpenCV)
  - Frontal face detector (OpenCV)
  - Face Mesh Model (Mediapipe)

<p align="middle">
  <img src="images/facemesh1.png" width="500" />
  <img src="images/facemesh2.png" width="500" /> 
</p>

### **2. Face Alignment**
- Using Face Mesh Model, extract right & left eye position
- Compute the angle between two eye position
- Rotate the original image correspondingly


## Sample Input & Sample Output

<p align="middle">
  <img src="images/face1.jpg" width="400" />
  <img src="images/face1_out.png" width="400" /> 
</p>
<p align="middle">
  <img src="images/face2.jpg" width="500" />
  <img src="images/face2_out.png" width="500" /> 
</p>
<p align="middle">
  <img src="images/face3.jpg" width="500" />
  <img src="images/face3_out.png" width="500" /> 
</p>
<p align="middle">
  <img src="images/face4.jpg" width="500" />
  <img src="images/face4_out.png" width="500" /> 
</p>
