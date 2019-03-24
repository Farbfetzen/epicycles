# Copyright (C) 2019 Sebastian Henz
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.



# path templates ----------------------------------------------------------

H <- "
x,y
0,0
1,0
1,1
2,1
2,0
3,0
3,1
3,2
3,3
2,3
2,2
1,2
1,3
0,3
0,2
0,1
0,0
"

triangle <- "
x,y
0,0
1,0
0.5,0.866
0,0
"

closed_hilbert <- "
x,y
7,0
6,0
6,1
7,1
7,2
7,3
6,3
6,2
5,2
5,3
4,3
4,2
4,1
5,1
5,0
4,0
3,0
3,1
2,1
2,0
1,0
0,0
0,1
1,1
1,2
0,2
0,3
1,3
2,3
2,2
3,2
3,3
3,4
3,5
2,5
2,4
1,4
0,4
0,5
1,5
1,6
0,6
0,7
1,7
2,7
2,6
3,6
3,7
4,7
5,7
5,6
4,6
4,5
4,4
5,4
5,5
6,5
6,4
7,4
7,5
7,6
6,6
6,7
7,7
"
p <- read.csv(text = closed_hilbert, header = TRUE)
p <- p$x + p$y * 1i
p <- c(p, p + 8i)
p <- c(p,rev(p + (7 - Re(p)) * 2 + 1))
p <- c(p, p[1])
p <- cbind(x = Re(p), y = Im(p))
closed_hilbert <- capture.output(
    write.table(p, "", row.names = FALSE, quote = FALSE, sep = ",")
)

t <- seq(0.1, by = 0.8, length.out = 6) * pi
p <- exp(t * 1i)
p <- cbind(x = Re(p), y = Im(p))
star <- capture.output(
    write.table(p, "", row.names = FALSE, quote = FALSE, sep = ",")
)

t <- seq(0, 2 * pi, length.out = 200)
t <- t[-length(t)]
x = 16 * sin(t)^3
y = 13 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t)
p <- cbind(x, y)
heart <- capture.output(
    write.table(p, "", row.names = FALSE, quote = FALSE, sep = ",")
)


# read, interpolate, save path --------------------------------------------

make_path <- function(template, filename, interpolate = 20, plot = TRUE) {
    # interpolate: Number of points to generate between the corners. To
    #   suppress interpolation use 'interpolate = 0'.
    p <- read.csv(
        text = template,
        header = TRUE
    )
    p <- p$x + p$y * 1i
    # Move center to 0+0i:
    p <- p - (mean(range(Re(p))) + mean(range(Im(p))) * 1i)

    if (interpolate > 0) {
        n <- interpolate  # number of points between corners
        result <- rep(0+0i, n * (length(p) - 1) + length(p))
        for (i in 2:length(p)) {
            new <- seq(p[i-1], p[i], length.out = n+2)
            j <- i + i * n - n
            result[seq(j-n-1, j)] <- new
        }
        result <- result[-length(result)]
    } else {
        result <- p
    }

    xy <- data.frame(x = Re(result), y = Im(result))
    if (plot) plot(xy, asp = 1, type = "o")
    write.table(xy, paste0("paths/", filename), quote = FALSE,
                row.names = FALSE, col.names = FALSE)
}
