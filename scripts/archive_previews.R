# Generates the listing images (preview.png) for the archived blog posts.
# Square, with all content inside the central circle (listing thumbnails are round).
# Run from the project root:  Rscript scripts/archive_previews.R
library(ggplot2)
bg <- "#FFFDF8"; accent <- "#8c2f39"; gold <- "#b08d4a"; ink <- "#5d6070"; txt <- "#23262e"
base <- theme_void() + theme(plot.background = element_rect(fill = bg, colour = NA),
                             plot.margin = margin(0, 0, 0, 0))
save <- function(p, path) { ragg::agg_png(path, width = 800, height = 800, res = 144); print(p); invisible(dev.off()) }
sq <- function(p) p + coord_fixed(xlim = c(0, 1), ylim = c(0, 1), expand = FALSE)

# 1. Mapping between assemblies: two coordinate tracks joined by marker, one marker unmatched
top <- c(.22, .34, .46, .60, .72, .80); bot <- c(.25, .31, .52, NA, .70, .78)
ln <- data.frame(x = top, xend = bot, y = .64, yend = .36)
p1 <- ggplot() + base +
  annotate("segment", x = .16, xend = .86, y = .64, yend = .64, colour = ink, linewidth = .5) +
  annotate("segment", x = .16, xend = .86, y = .36, yend = .36, colour = ink, linewidth = .5) +
  geom_segment(data = ln[!is.na(ln$xend), ], aes(x = x, xend = xend, y = y, yend = yend), colour = gold, linewidth = .7) +
  geom_segment(data = ln[is.na(ln$xend), ], aes(x = x, xend = x, y = y, yend = .5), colour = accent, linewidth = .7, linetype = "22") +
  geom_point(aes(top, .64), colour = accent, size = 3.4) +
  geom_point(aes(bot[!is.na(bot)], .36), colour = accent, size = 3.4) +
  annotate("text", x = .60, y = .45, label = "NA", colour = accent, family = "Menlo", fontface = "bold", size = 4.2) +
  annotate("text", x = .16, y = .71, label = "canFam2", hjust = 0, colour = txt, family = "Georgia", fontface = "italic", size = 4.4) +
  annotate("text", x = .16, y = .29, label = "CanFam3", hjust = 0, colour = txt, family = "Georgia", fontface = "italic", size = 4.4)
save(sq(p1), "posts/archive-genome-assembly-mapping/preview.png")

# 2. vGWAS: same mean in every genotype group, different spread (illustration, simulated data)
set.seed(7)
d <- data.frame(g = rep(c("AA", "Aa", "aa"), each = 40),
                y = c(rnorm(40, 0, .35), rnorm(40, 0, .7), rnorm(40, 0, 1.25)))
d$x <- as.numeric(factor(d$g, c("AA", "Aa", "aa")))
d$x <- .27 + (d$x - 1) * .23 + runif(nrow(d), -.065, .065); d$yy <- .5 + d$y * .09
p2 <- ggplot(d) + base +
  geom_point(aes(x, yy, colour = g), size = 2.1, alpha = .85, show.legend = FALSE) +
  annotate("segment", x = .17, xend = .83, y = .5, yend = .5, colour = ink, linetype = "22", linewidth = .5) +
  scale_colour_manual(values = c(AA = gold, Aa = "#8a6f3b", aa = accent)) +
  annotate("text", x = c(.27, .50, .73), y = .27, label = c("AA", "Aa", "aa"), colour = txt, family = "Georgia", fontface = "italic", size = 4.4)
save(sq(p2), "posts/archive-variance-controlling-genes/preview.png")

# 3 and 4: terminal-style text images (real content: ACARS output, randomart of a throwaway key)
term <- function(lines, width, lh = 1.45) {
  # one left-aligned monospace block, centred; `width` = fraction of the image width
  n <- max(nchar(lines)); pts <- width * (800 / 144) * 72 / (n * .6)
  ggplot() + base + annotate("text", x = .5 - width / 2, y = .5, label = paste(lines, collapse = "\n"),
    hjust = 0, vjust = .5, family = "Menlo", colour = txt, size = pts / 2.845, lineheight = lh)
}
acars <- c("RX_IDX: 0", "ACARS mode: V", "message label: H1", "Block id: 55", "msg. no: D02A", "", "Message content:-", "#DFBCL2N14121ESSAKEWR",
           "3008072336 222 -075-215", "20028064524168000691CLMBB")
p3 <- term(acars, .5) +
  annotate("segment", x = .22, xend = .78, y = .83, yend = .83, colour = gold, linewidth = .6) +
  annotate("segment", x = .22, xend = .78, y = .17, yend = .17, colour = gold, linewidth = .6)
save(sq(p3), "posts/archive-rtl-acars-osx/preview.png")

art <- c("+--[ED25519 256]--+", "|        .o+O=o   |", "|         o=.=.o  |", "|       . +.oo. +.|", "|        o.+.++. =|",
         "|        Eoo*=o . |", "|         B*.... .|", "|          .+.  +o|", "|          ......o|", "|           . .o.+|", "+----[SHA256]-----+")
p4 <- term(art, .46, lh = 1.2)
save(sq(p4), "posts/archive-bash-ssh-basics/preview.png")
