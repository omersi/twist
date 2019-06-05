Getting into the DevOps Challenge

1. I found the hint in the landing quickly by looking at the source code.
2. I first thought this is a token to access dynamodb via a tokenized connection :/
3. It took me some reading and testing to figure out I was wrong, but didn't think of a better way yet.
4. Then, I figured out it was encrypted in a way, but couldn't find a key to decrypt it with.
   I then realized it was base64 encoded. 

From that point thing went easy. 
5. Figuring out more about DynamoDB - quick.
6. Learning how to create drone.io configuration file.
6.1. I first missed the part that said to push the image to docker hub... as soon as I read the instructions again I 
     found the plugin, and did some tweaks to the code to make it work as I wanted, including storing secret credentials
     in their blob. 
7. Add mock gateway to test workflow
8. Added unittesting to the module to find out everything is working as expected.