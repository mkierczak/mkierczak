library('renv')
library('cropcircles')
#renv::install("cropcircles")
cropcircles::crop_hex(images = "assets/marcin1.webp", 
                      to = 'assets/marcin1.png', 
                      border_size = 24,
                      border_colour = 'brown')
