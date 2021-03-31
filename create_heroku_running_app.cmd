REM login to your Heroku account
heroku login

REM change dash-app to a unique name
heroku create moves3-2014b-running-app

REM deploy to Heroku
git push heroku master

REM run the app with a 1 heroku "dyno"
heroku ps:scale web=1

