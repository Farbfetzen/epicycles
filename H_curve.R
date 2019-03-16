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


# First find the corners and then interpolate.

p_str <- "
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
p <- read.csv(text = p_str, header = TRUE)
p <- p$x + p$y * 1i
p <- p * 200
plot(p, type = "o")

# Interpolate:
n <- 98  # number of points between corners
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

# ---
xy <- data.frame(x = Re(result), y = Im(result))
write.table(xy, "H_path.txt", quote = FALSE,
            row.names = FALSE, col.names = FALSE)
# ---


par(mar = c(4, 4, 0, 0)+0.1)
plot(result, type = "o", asp = 1)

foo <- construct(result, 100, 1000)  # from the other script
plot(foo$p, asp = 1)
foo$values

bla <- foo$values

# remove all circles with zero radius:
bla
bla <- bla[abs(bla$a) > 0, ]
bla

bla$a <- sub("i", "j", as.character(bla$a), fixed = TRUE)
bla$a <- paste0("[", bla$a)
bla$b <- paste0(bla$b, "j],")
bla[nrow(bla), 2] <- sub(",", "", bla[nrow(bla), 2], fixed = TRUE)
write.table(bla, "H_circles.txt", row.names = FALSE, col.names = FALSE,
            quote = FALSE, sep = ", ")
# Now open the file and copy everything into the python script.
# TODO: Write the python script so that it can load from that file.

