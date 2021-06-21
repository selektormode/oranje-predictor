# oranje-predictor
Predict which opponont the Dutch team faces in the RO16 of EURO2020

To run: 
python3 main.py

The program creates a jpg file with the results in a bar plot and a pickle file. 

Input files:
 * Standings.csv:
  The current standings 
  
 * Odds.csv:
  odds taken from some random bookmaker last friday/saturday
  
 * game_results.csv:
  results of the previous matches. 
  
Used packages: 
 * Pandas
 * Numpy 
 * Matplotlib
 * Pickle 

all further info is in the comments of main.py 

The code is a bit of a mess and quite slow. 
I used this project to learn Pandas a bit. Someone with more experience with pandas and programming should be able to speed up te simulation. 
But, it works. 

To improve:
Make the number of goals scored in games more realistic. 
 
