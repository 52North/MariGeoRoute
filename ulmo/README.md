# ULMO -  **U**nderwater **L**andscape **M**odifying **O**rganism
Manipulate environmental datasets <br>
[<img alt="Ulmo" height="250" src="https://static.wikia.nocookie.net/lotr/images/6/6a/Ulmo_on_the_shore.jpg/revision/latest/scale-to-width-down/1000?cb=20141229140915" width="250"/>](https://lotr.fandom.com/wiki/Ulmo)

## workflow
### preprocessing
- create a raster mask of the area you want to manipulate with the resolution of your environmental data
    - draw polygon
    - rasterize
### ULMO
ULMO generates a new set of pixels for every timestep which are then manipulated according to their order of creation.
It grows in a quadratic shape (each pixel next to the pixels of generation before will be in the next generation, if they are within the geometry of the mask)
<br> It uses a function to estimate the new values (e.g. f(x)=x):
- the for the first generation there will be only one point (the starting point) with the value 1
- for the 10th generation the starting point will have the value 10, the points create last will be at value 1 
