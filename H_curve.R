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

par(mar = c(4, 4, 0, 0)+0.1)
plot(result, type = "o", asp = 1)

transformed <- fft(result, inverse = TRUE) / length(result)
transformed

foo <- construct(result, 15, 1000)  # from the other script
plot(foo$p, asp = 1)
foo$values

# Interessant: Alle a bei geraden b sind null.

bla <- foo$values
bla$a <- sub("i", "j", as.character(bla$a), fixed = TRUE)
bla$a <- paste0("[", bla$a)
bla$b <- paste0(bla$b, "j],")
bla <- bla[-1, ]
bla[nrow(bla), 2] <- sub(",", "", bla[nrow(bla), 2], fixed = TRUE)
bla
write.table(bla, "H_circles.csv", row.names = FALSE, col.names = FALSE,
            quote = FALSE, sep = ", ")
# Now open the file and copy everything into the python script.
# TODO: Write the python script so that it can load from that file.

