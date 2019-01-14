p_str <- "
x,y
0,0
1,0
0,0
0,-1
0,0
-1,0
0,0
0,1
0,0
"
p <- read.csv(text = p_str, header = TRUE)
p <- p$x + p$y * 1i
plot(p, type = "o", asp = 1)
