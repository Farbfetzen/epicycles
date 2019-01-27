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
8,1
7,1
7,2
8,2
8,3
8,4
7,4
7,3
6,3
6,4
5,4
5,3
5,2
6,2
6,1
5,1
4,1
4,2
3,2
3,1
2,1
1,1
1,2
2,2
2,3
1,3
1,4
2,4
3,4
3,3
4,3
4,4
4,5
4,6
3,6
3,5
2,5
1,5
1,6
2,6
2,7
1,7
1,8
2,8
3,8
3,7
4,7
4,8
5,8
6,8
6,7
5,7
5,6
5,5
6,5
6,6
7,6
7,5
8,5
8,6
8,7
7,7
7,8
8,8
"
p <- read.csv(text = p_str, header = TRUE)
p <- p$x + p$y * 1i
p <- c(p, p + 8i)
p <- c(p, rev(p + (8 - Re(p)) * 2 + 1))
p <- c(p, p[1])
plot(p, type = "o", asp = 1)
# For the rest see H_curve.R
