

The collision detection methods use the coordinates directly stored in the rectangle. 
So if a pygame event sends absolute coordinates in `event.pos`, the collision methods such as
`collidepoint` or `colliderect` will fail. 