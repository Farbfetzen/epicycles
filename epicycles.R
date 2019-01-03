# Sebastian Henz (2019)
# License: MIT (see file LICENSE for details)

# https://www.youtube.com/watch?v=qS4H6PEcCCA

t <- seq(0, 2 * pi, length.out = 100)
p1 <- (10.72 + 16.52i) * exp(0i * t)
p2 <- (-12.64 + 20.90i) * exp(1i * t)
p3 <- (-135.66 - 45.57i) * exp(-1i * t)
p4 <- (-44.85 - 23.71i) * exp(2i * t)
p5 <- (66.75 - 53.07i) * exp(-2i * t)
p <- p1 + p2 + p3 + p4 + p5
par(pty = "s")
plot(p, pch = 20, asp = 1)

points(p1, pch = 4)

plot(p4)
points(0, abs(-44.85 - 23.71i), pch = 4)

# Die erste komplexe Zahl ist der Radius. Das t ist die Phase von 0 bis 2pi.
# Die Zahl vor dem i im exp() ist die Richtung und Anzahl der Rotationen.
# Bei p1 rotiert nichts. Das ist glaube ich die Mitte des ersten Kreises.

# Kurve zerlegen und wieder aufbauen:
foo <- fft(p, inverse = TRUE) / length(p)
t <- seq(0, 2 * pi, length.out = 100)
p1 <- foo[1] * exp(0i * t)
p2 <- foo[length(foo)] * exp(1i * t)
p3 <- foo[2] * exp(-1i * t)
p4 <- foo[length(foo) - 1] * exp(2i * t)
p5 <- foo[3] * exp(-2i * t)
p_sum <- p1 + p2 + p3 + p4 + p5
plot(p_sum, pch = 20, asp = 1)
