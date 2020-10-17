## Drawing shapes with epicycles.

Requires Python >= 3.6, PyGame 2 and NumPy.
 
To run the app you must provide a path to a text file containing the points of the desired shape:
```
python epicycles.py shapes/heart.txt
```


### optional command line arguments
- **-h**, **--help**: Show a help message and exit.
- **-n \<int>**: Limit the maximum number of circles.
- **-s**, **--scale \<float>**: A number > 0 and <= 1 indicating how much of the width and height of the window the shape should occupy. To disable scaling set it to 0.
- **-f**, **--fade**: Fade the line color over time so that it vanishes after one cycle.
- **-r**, **--reverse**: Reverse the rotation direction.
- **-p**, **--paused**: Start the app paused.
- **--window-size \<width> \<height>**: Specify a custom window width and height in pixels.
- **-d**, **--debug**: Start the app in debug mode.


### controls
- **Space**: Pause/unpause. 
- **Backspace**: Erase the line.
- **F**: Toggle line fading.
- **C**: Toggle visibility of the circles.
- **+**: Increase speed.
- **-**: Decrease speed.
- **R**: Reverse rotation.
- **ESC**: Quit.
- **F1**: Toggle debug mode.
