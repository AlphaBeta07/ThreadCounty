# MIT App Inventor Instructions for ThreadCounty Mobile App

This document provides detailed instructions for building the ThreadCounty mobile app using MIT App Inventor. The mobile app will connect to our Flask backend for fabric thread counting.

## 1. Setting Up the Project

1. Go to [MIT App Inventor](https://appinventor.mit.edu/) and create a new project named "ThreadCounty"
2. Set the app's screen properties:
   - Title: "ThreadCounty"
   - Screen Orientation: Portrait
   - Theme: Device Default (Dark)

## 2. Design Components

### Screen1 (Main Screen)

#### Components to add:
1. **Arrangement** (Vertical) - Main container
   - Width: Fill parent
   - Height: Fill parent
   - AlignHorizontal: Center
   - Background Color: Dark Gray (#212529)

2. **Label** - App Title
   - Text: "ThreadCounty"
   - FontSize: 24
   - FontBold: True
   - TextColor: White
   - AlignHorizontal: Center

3. **HorizontalArrangement** - Button container
   - Width: Fill parent
   - Height: Automatic
   - AlignHorizontal: Center
   - Padding: 10px

4. **Button** - Camera Button
   - Text: "Take Photo"
   - Width: 150px
   - Height: 60px
   - Shape: Rounded
   - BackgroundColor: #28a745 (Green)

5. **Button** - Gallery Button
   - Text: "Choose from Gallery"
   - Width: 150px
   - Height: 60px
   - Shape: Rounded
   - BackgroundColor: #17a2b8 (Blue)

6. **Label** - Instructions
   - Text: "Take or select a clear photo of fabric for thread counting"
   - FontSize: 14
   - TextColor: Light Gray
   - AlignHorizontal: Center

7. **HorizontalArrangement** - Settings container
   - Width: Fill parent
   - Height: Automatic
   - AlignHorizontal: Center
   - Padding: 10px

8. **Label** - Unit Label
   - Text: "Unit:"
   - Width: 80px
   - TextColor: White

9. **ListPicker** - Unit Selection
   - ElementsFromString: "cm,inch"
   - Text: "cm"
   - Width: 100px

10. **Label** - Reference Length Label
    - Text: "Reference Length:"
    - Width: 120px
    - TextColor: White

11. **TextBox** - Reference Length Input
    - Text: "1.0"
    - NumbersOnly: True
    - Width: 80px

12. **Button** - History Button
    - Text: "View History"
    - Width: Fill parent
    - BackgroundColor: #6c757d (Gray)

13. **WebViewer** - For displaying processing status
    - Width: Fill parent
    - Height: 200px
    - Visible: False

14. **Camera** - For taking photos
    - (Non-visible component)

15. **ActivityStarter** - For picking images from gallery
    - (Non-visible component)

16. **Web** - For API communication
    - (Non-visible component)

17. **TinyDB** - For local storage
    - (Non-visible component)

18. **Notifier** - For displaying messages
    - (Non-visible component)

### ResultsScreen

Create a new screen named "ResultsScreen" with the following components:

1. **VerticalArrangement** - Main container
   - Width: Fill parent
   - Height: Fill parent
   - AlignHorizontal: Center
   - Background Color: Dark Gray (#212529)

2. **Label** - Screen Title
   - Text: "Analysis Results"
   - FontSize: 24
   - FontBold: True
   - TextColor: White
   - AlignHorizontal: Center

3. **Image** - Result Image
   - Width: Fill parent
   - Height: 200px
   - AlignHorizontal: Center

4. **HorizontalArrangement** - Thread Counts Container
   - Width: Fill parent
   - Height: Automatic
   - AlignHorizontal: Center

5. **VerticalArrangement** - Warp Container
   - Width: 30%
   - Height: Automatic
   - BackgroundColor: #28a745 (Green)
   - Padding: 5px

6. **Label** - Warp Title
   - Text: "Warp"
   - FontBold: True
   - TextColor: White
   - AlignHorizontal: Center

7. **Label** - Warp Count
   - Text: "0"
   - FontSize: 24
   - FontBold: True
   - TextColor: White
   - AlignHorizontal: Center

8. **VerticalArrangement** - Weft Container
   - Width: 30%
   - Height: Automatic
   - BackgroundColor: #17a2b8 (Blue)
   - Padding: 5px

9. **Label** - Weft Title
   - Text: "Weft"
   - FontBold: True
   - TextColor: White
   - AlignHorizontal: Center

10. **Label** - Weft Count
    - Text: "0"
    - FontSize: 24
    - FontBold: True
    - TextColor: White
    - AlignHorizontal: Center

11. **VerticalArrangement** - Density Container
    - Width: 30%
    - Height: Automatic
    - BackgroundColor: #ffc107 (Yellow)
    - Padding: 5px

12. **Label** - Density Title
    - Text: "Density"
    - FontBold: True
    - TextColor: Black
    - AlignHorizontal: Center

13. **Label** - Density Value
    - Text: "0"
    - FontSize: 24
    - FontBold: True
    - TextColor: Black
    - AlignHorizontal: Center

14. **Label** - Density Unit
    - Text: "threads/cm"
    - FontSize: 12
    - TextColor: Black
    - AlignHorizontal: Center

15. **Label** - Confidence Label
    - Text: "Confidence Score:"
    - TextColor: White
    - AlignHorizontal: Center

16. **HorizontalArrangement** - Confidence Bar Container
    - Width: Fill parent
    - Height: 30px
    - BackgroundColor: #343a40

17. **HorizontalArrangement** - Confidence Bar
    - Width: 0%
    - Height: Fill parent
    - BackgroundColor: #28a745

18. **Button** - Back Button
    - Text: "Back"
    - Width: 40%
    - BackgroundColor: #6c757d

19. **Button** - Save Button
    - Text: "Save Results"
    - Width: 40%
    - BackgroundColor: #28a745

### HistoryScreen

Create a new screen named "HistoryScreen" with the following components:

1. **VerticalArrangement** - Main container
   - Width: Fill parent
   - Height: Fill parent
   - AlignHorizontal: Center
   - Background Color: Dark Gray (#212529)

2. **Label** - Screen Title
   - Text: "Analysis History"
   - FontSize: 24
   - FontBold: True
   - TextColor: White
   - AlignHorizontal: Center

3. **ListView** - History List
   - Width: Fill parent
   - Height: Fill parent
   - TextColor: White
   - BackgroundColor: #343a40

4. **Button** - Back Button
   - Text: "Back to Home"
   - Width: Fill parent
   - BackgroundColor: #6c757d

5. **Web** - For API communication
   - (Non-visible component)

6. **TinyDB** - For local storage
   - (Non-visible component)

7. **Notifier** - For displaying messages
   - (Non-visible component)

## 3. Programming Blocks

### Screen1 Blocks

1. **Initialize the app**:
   - Create an "when Screen1.Initialize" block
   - Set ActivityStarter properties for gallery picking
   - Set TinyDB to store API endpoint

2. **Camera Button**:
   - Create a "when CameraButton.Click" block
   - Use Camera.TakePicture to capture an image

3. **Gallery Button**:
   - Create a "when GalleryButton.Click" block
   - Use ActivityStarter to open gallery

4. **Process the selected/captured image**:
   - Create a "when Camera.AfterPicture" block
   - Create a "when ActivityStarter.AfterActivity" block
   - Both should call a procedure to upload the image to the server

5. **Upload Image Procedure**:
   - Create a procedure "UploadImage" that takes an image path
   - Set up Web.PostFile to upload to the API endpoint
   - Include unit and reference length parameters
   - Show loading indicator

6. **Handle API Response**:
   - Create a "when Web.GotText" block
   - Parse the JSON response
   - Store results in TinyDB
   - Navigate to ResultsScreen

7. **History Button**:
   - Create a "when HistoryButton.Click" block
   - Navigate to HistoryScreen

### ResultsScreen Blocks

1. **Initialize Results Screen**:
   - Create a "when ResultsScreen.Initialize" block
   - Get results from TinyDB
   - Display warp, weft, and density values
   - Set confidence score bar width based on confidence percentage
   - Load and display the visualization image

2. **Back Button**:
   - Create a "when BackButton.Click" block
   - Navigate back to Screen1

3. **Save Button**:
   - Create a "when SaveButton.Click" block
   - Save the current analysis in TinyDB's history list
   - Show confirmation message

### HistoryScreen Blocks

1. **Initialize History Screen**:
   - Create a "when HistoryScreen.Initialize" block
   - Load history data from TinyDB
   - Format and display in ListView
   - If empty, show message "No analysis history"

2. **Select History Item**:
   - Create a "when ListView.AfterPicking" block
   - Get the selected analysis details
   - Store in TinyDB as current result
   - Navigate to ResultsScreen

3. **Back Button**:
   - Create a "when BackButton.Click" block
   - Navigate back to Screen1

4. **Refresh History**:
   - Add a procedure to refresh history from API
   - Create a "when Web.GotText" block to handle the response

## 4. API Integration

The mobile app will communicate with the Flask backend using the following endpoints:

1. **Upload and Analyze Image**:
   - Endpoint: `http://your-flask-server:5000/api/analyze`
   - Method: POST
   - Parameters:
     - file: The image file
     - unit: "cm" or "inch"
     - reference_length: Numeric value

2. **Get Analysis History**:
   - Endpoint: `http://your-flask-server:5000/api/history`
   - Method: GET

3. **Get Specific Analysis**:
   - Endpoint: `http://your-flask-server:5000/api/result/<analysis_id>`
   - Method: GET

## 5. Offline Functionality

1. Store the server URL in TinyDB for easy configuration
2. Cache analysis results in TinyDB for offline viewing
3. Implement error handling for network failures

## 6. Deployment

1. Generate the APK from MIT App Inventor
2. Install on Android devices
3. Configure the server URL in the app settings

## Notes for Best Results

1. Ensure good lighting when taking photos of fabric
2. Hold the camera steady and at a consistent distance
3. Use a reference object if precise measurements are needed
4. Avoid capturing wrinkled or stretched fabric for accurate results
