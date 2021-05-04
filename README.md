## Drawing shapes with epicycles

This app lets you draw any 2d shape using a combination of circles with different radii and rotation speeds.  For more info see [this Video by The Coding Train](https://www.youtube.com/watch?v=qS4H6PEcCCA) or [this Video by Mathologer](https://www.youtube.com/watch?v=MY4luNgGfms).

![heart](readme_visuals/heart.png)  
![closed hilbert curve](readme_visuals/hilbert.png)


Requires Python >= 3.6, PyGame 2 and NumPy.
 
To run the app you can provide a path to a text file containing the points of the desired shape:
```
python epicycles.py shapes/heart.txt
```
If you run it without a file path then the app will go into "draw" mode. There you you can draw a shape with the mouse. Then hit enter to watch the circles go.


### Controls
Action | Binding
--- | ---
Pause/unpause | Space
Erase the line | Backspace
Toggle line fading | F
Toggle visibility of the circles | C
Increase speed | +
Decrease speed | -
Reverse rotation | R
Switch between the circles and the drawing mode | Enter
Toggle debug mode | F1
Quit | Esc


### Optional Command Line Arguments
- -h, --help: Show a help message and exit.
- -n \<int>: Limit the maximum number of circles.
- -s, --scale \<float>: A number > 0 and <= 1 indicating how much of the width and height of the window the shape should occupy. To disable scaling set it to 0.
- -f, --fade: Fade the line color over time so that it vanishes after one cycle.
- -r, --reverse: Reverse the rotation direction.
- -p, --paused: Start the app paused.
- -w, --window-size \<width> \<height>: Specify a custom window width and height in pixels.
- -d, --debug: Start the app in debug mode.
