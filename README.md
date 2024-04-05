This is a Todo app written with FastAPI that follows along with Eric Roby's Udemy course. 

I have added a few things to make it unique, and plan on building it out with other features.
Consider it a student project, but it is up on Heroku and works. 

For the latest version of pandas the yahoo finance library, yahoo-fin, does not work. To continue the 'Get Stocks'
feature, you'll have to manually edit the site-package 'yahoo-fin/stock_info.py'. The only changes needed are
modifying the '.append' function to ._append'. That's it. There are only three instances of this, so it's a quick change and works.  

Try it out!
