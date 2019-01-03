# Sebastian Henz (2019)
# License: MIT (see file LICENSE for details)

# https://www.youtube.com/watch?v=qS4H6PEcCCA

# TODO: better variable names
# TODO: alles in python übersetzen und animieren

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
#
# Je mehr Punkte voranden sind, desto genauer ist die fft(). Also am besten
# sowas wie:
# t <- seq(0, 2 * pi, length.out = 1000)

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


x <- seq(0, 2 * pi, length.out = 100)
p1 <- complex(real = cos(x), imaginary = sin(x))
p2 <- complex(real = cos(-2*x), imaginary = sin(-2*x)) / 2
# das n*x ist die Drehgeschwindigkeit. Das /2 ist der Radius. Ein negatives n*x
# kehrt die Drehrichtung um.
p <- p1 + p2
par(pty = "s")
plot(p, pch = 20, asp = 1)

p1 <- complex(real = cos(x), imaginary = sin(x))
p2 <- complex(real = cos(-3 * x), imaginary = sin(-3 * x)) / 3**2
p3 <- complex(real = cos(5 * x), imaginary = sin(5 * x)) / 5**2
p4 <- complex(real = cos(-7 * x), imaginary = sin(-7 * x)) / 7**2
p <- p1 + p2 + p3 + p4
plot(p, pch = 20, asp = 1)

# alternative Schreibweise:
p1 <- exp(1i * x)
p2 <- 1/9 * exp(-3i * x)
p3 <- 1/25 * exp(5i * x)
p4 <- 1/49 * exp(-7i * x)
p <- p1 + p2 + p3 + p4
plot(p, pch = 20, asp = 1)

# Rotieren, damit die flache Kanten unten liegt. Laut dem Video muss ich nur die
# erste Zahl ändern, denn diese gibt den Startpunkt an:
z <- 1/sqrt(2); p1 <- (z+z*1i) * exp(1i * x)
z <- 1/(9*sqrt(2)); p2 <- (z+z*1i) * exp(-3i * x)
z <- 1/(25*sqrt(2)); p3 <- (z+z*1i) * exp(5i * x)
z <- 1/(49*sqrt(2)); p4 <- (z+z*1i) * exp(-7i * x)
p <- p1 + p2 + p3 + p4
plot(p, pch = 20, asp = 1)


foo <- fft(p, inverse = TRUE) / length(p)
q1 <- foo[1] * exp(0i * x)
q2 <- foo[length(foo)] * exp(1i * x)
q3 <- foo[2] * exp(-1i * x)
q4 <- foo[length(foo)-1] * exp(2i * x)
q5 <- foo[3] * exp(-2i * x)
q <- q1 + q2 + q3 + q4 + q5
plot(q, pch = 20, asp = 1)


construct <- function(v, n, m) {
    # v: vector of points to be approximated
    # n: number of circles
    # m: number of points to return
    # Returns the complex coordinates of the shape.

    foo <- fft(p, inverse = TRUE) / length(p)

    indices <- integer(n)
    indices[seq(1, n, 2)] <- 1:ceiling(n / 2)
    indices[seq(2, n, 2)] <- seq(length(foo), length(foo) - floor(n / 2) + 1)
    indices

    bla <- rep(1:n, each = 2, length.out = n - 1)
    bla <- bla * rep(c(1, -1), length.out = n - 1)
    bla <- c(0, bla)

    x <- seq(0, 2 * pi, length.out = m)

    p <- complex(length(t))
    for (j in 1:n) {
        p <- p + foo[indices[j]] * exp(bla[j] * 1i * x)
    }
    p
}

s <- construct(p, 5, 100)
plot(s, pch = 20, asp = 1)

s <- construct(p, 10, 100)
plot(p, asp = 1)
lines(s)
