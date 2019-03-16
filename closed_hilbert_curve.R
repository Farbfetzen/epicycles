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

p_str <- "
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
p <- read.csv(text = p_str, header = TRUE)
p <- p$x + p$y * 1i
p <- c(p, p + 8i)
p <- c(p, rev(p + (7 - Re(p)) * 2 + 1))
p <- c(p, p[1])
plot(p, type = "o", asp = 1)
# For the rest see H_curve.R


# Interpolate:
n <- 20  # number of points between corners
result <- rep(0+0i, n * (length(p) - 1) + length(p))
for (i in 2:length(p)) {
    new <- seq(p[i-1], p[i], length.out = n+2)
    j <- i + i * n - n
    result[seq(j-n-1, j)] <- new
}
# Remove duplicate:
result <- result[-length(result)]
# Move center to 0+0i:
result <- result - (max(Re(result)) / 2 + (max(Im(result)) / 2) * 1i)
plot(result, type = "o", asp = 1)
length(result)

x <- Re(result)
y <- Im(result)
xy <- cbind(x, y)
xy <- xy * 40
plot(xy, asp = 1)
head(xy)
write.table(xy, "closed_hilbert_curve.txt", row.names = FALSE, col.names = FALSE)
