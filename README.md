# Dissertation
Dissertation Project on the Analysis and Prediction of eSports Matches(League of Legends)

In order to analyse and predict matches in league of legends, I will be creating a flask web-app that utilizes Riot's api to store match data, aswell as create infographics to aid players in improving their peformance. This data will also be used in a machine learning algorithm to predict the winner of live games.

### Access

App can be found at http://leaguematchpredictor.net/

If the App is unavalable, please email me at nsmallcalder5@gmail.com

### Running App

Users can query League of Legends account names to use the application.
If a user does not have a League of Legends Account, use any from below:
```
Name          Region
Mealsz        EUW1
Lil Natchy    EUW1
ItWoZnOtMee   EUW1
```
### Hosting

Request a Config file from me nsmallcalder5@gmail.com
clone or download repository
```
cd server
make build
make run
```

####


### Match Predictor Solo

Users can input their name, role, region, champion and enemy champ and run the simulator, after a short period of time, the server will return a match prediction.

[SoloPredictor.webm](https://user-images.githubusercontent.com/74361286/235540717-139ac77e-5f96-4f95-bc75-d500a72b17b3.webm)



### Match Predictor Team

Users can select 10 summoners, champions and run the simulator, after 1-2 mins, the server will return a response either blue or red match win.

[TeamPredictor.webm](https://user-images.githubusercontent.com/74361286/235540711-49027c7a-7615-4782-b390-632ee31b5b2e.webm)


