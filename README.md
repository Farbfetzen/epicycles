## Drawing shapes with epicycles.

Requires Python >= 3.6, PyGame 2 and NumPy.
 
To run the app you must provide a path to a textfile containg the waypoints of the desired shape:
```
python epicycles.py paths/heart.txt
```


### optional command line arguments
- **-h**, **--help**: Show a help message and exit.
- **-n \<int>**: Limit the maximum number of harmonics or circles.
- **-s**, **--scale_factor \<float>**: A number > 0 and <= 1 indicating how much of the width and height of the window the shape should occupy. To disable scaling set it to 0.
- **-f**, **--fade**: Fade the line over time so that it vanishes after one cycle.
- **-r**, **--reverse**: Reverse the rotation direction of all circles causing the shape to be drawn counterclockwise.
- **-p**, **--paused**: Start the app paused.
- **--window_size \<width> \<height>**: Specify a custom window width and height in pixels.


### controls
- **Space**: Pause/unpause. 
- **Backspace**: Erase the line.
- **F**: Toggle line fading.
- **C**: Toggle visibility of the circles.
- **+**: Increase speed.
- **-**: Decrease speed.
- **ESC**: Quit.
