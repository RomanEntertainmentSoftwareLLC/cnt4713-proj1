# CNT-4731 Project 1

Template for for FIU CNT-4731 Project 1

## Academic Integrity Note

You are encouraged to host your code in private repositories on [GitHub](https://github.com/), [GitLab](https://gitlab.com), or other places.  At the same time, you are PROHIBITED to make your code for the class project public during the class or any time after the class.  If you do so, you will be violating academic honestly policy that you have signed, as well as the student code of conduct and be subject to serious sanctions.

## Provided Files

`client.py`, `server-s.py`, and  `server.py` are the entry points for the client, simplified server, and server parts of the project.

## TODO

##The problems you ran into and how you solved the problem: 
Honestly, I've done socket programming before in C++, VB6, VB.Net, and Java, but never have in Python. I ended up stuck receiving data from the server on the second 
receiving phase and was unable to submit large files as a result. As it turns out, I was sending the server the wrong command and the wrong format. Turns out on the 
first receiving phase, I had to use b'confirm-accio\r\n', not "accio\r\n". After I figured that out, had to use some funky abilities to manipulate the byte string for 
the second receiving phase to equate b'confirm-accio-again\r\n\r\n'. And after some Googling, it turns out bytearray() was the solution to that, as I am able to append 
them together. Then I had to separate them using a list using characters (although looking back, I could have stuck with the bytearray), and store them into the buffer 
one character at a time. Once that worked, I unlocked the ability to upload a 10 MiB file.

##Acknowledgement of any online tutorials or code example (except class website) you have been using:
GeeksforGeeks.com and some sample stackoverflow questions regarding byte strings, as I never used them before in python. The rest of the code was mainly personal knowledge as I been coding for over 30 years now.
