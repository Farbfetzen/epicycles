"""Draw various intricate shapes by adding rotating circles."""

import argparse
import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

from src import scene_manager
from src import constants


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file",
        help="Path to file containing the desired shape."
    )
    parser.add_argument(
        "-n",
        type=int,
        metavar="<int>",
        help="Limit the maximum number of harmonics or circles.",
        default=0
    )
    parser.add_argument(
        "-s",
        "--scale",
        type=float,
        metavar="<float>",
        help="A number > 0 and <= 1 indicating how much of the width and " +
             "height of the window the shape should occupy. To disable " +
             f"scaling set it to 0. Defaults to {constants.DEFAULT_SCALE_FACTOR}.",
        default=constants.DEFAULT_SCALE_FACTOR
    )
    parser.add_argument(
        "-f",
        "--fade",
        action="store_true",
        help="Fade the line over time so that it vanishes after one cycle."
    )
    parser.add_argument(
        "-r",
        "--reverse",
        action="store_true",
        help="Reverse the rotation direction of all circles " +
             "causing the shape to be drawn counterclockwise."
    )
    parser.add_argument(
        "-p",
        "--paused",
        action="store_true",
        help="Start the app paused."
    )
    parser.add_argument(
        "--window-size",
        metavar=("<width>", "<height>"),
        nargs=2,
        type=int,
        help="Specify a custom window width and height in pixels.",
        default=constants.DEFAULT_WINDOW_SIZE
    )
    args = parser.parse_args()
    app = scene_manager.SceneManager(
        args.file,
        args.n,
        args.scale,
        args.fade,
        args.reverse,
        args.paused,
        args.window_size
    )
    app.run()
