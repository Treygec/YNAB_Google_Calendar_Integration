# YNAB_Google_Calendar_Integration
This project is made to add the ability to create YNAB transcations in Google Calendar events. 

#USAGE

To add a YNAB transcation from Google Calendar you must add 3 lines of text to the event description in below format:  
  
ynab  
category name  
amount  

for example  
  
ynab  
going out  
75  


The way the programs works is it searches for the keyword "ynab" and that triggers the flow to read the rest and adds that information
to YNAB as a transaction. The amount is really just a guess at how much that will cost so that you can account for a future spending
event earlier in the month. 

# CURRENT IMPLEMENTATION
If set to run on a schedule it will work and create the transcations when run. 

# FEATURES TO ADD
* Add Google Oauth to remove need to use api keys
* Set up Google API watch events to trigger the program to run when a calendar event is created for real time updates
* Add function that will remove transaction on the date of the event so that you can input the true number
* set it to only check this months calendar events. 
