# Bruce  

[![Discord](https://img.shields.io/discord/402356550133350411.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2)](https://discord.gg/sXDbtp4)
![GitHub deployments](https://img.shields.io/github/deployments/CNDRD/Bruce/bruce-discord?label=Deployment&logo=heroku)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/fbf1a0369b054703a5a337ea37f588c3)](https://app.codacy.com/gh/CNDRD/Bruce)  
![Python Version](https://img.shields.io/badge/python-3.9-blue.svg?logo=python)
![GitHub repo size](https://img.shields.io/github/repo-size/CNDRD/bruce)
![GitHub License](https://img.shields.io/github/license/CNDRD/bruce)  

`/r6sapi` is my fork of [r6sapi](https://github.com/billy-yoyo/RainbowSixSiege-Python-API) that I tricked into working..  

---  

## Deployment  
(Kinda step, by step..)  

1. Go to [Firebase](https://firebase.google.com/), create an account, create and setup a project (Realtime Database)  
2. Go to [Heroku](https://signup.heroku.com/), and create a free account  
3. Create an app on Heroku  
4. In the "Settings" tab set-up config variables (shown in the table below).  
5. In the "Deploy" tab, section "Deployment method", select the best deployment method for you.  
6. If you want to deploy from GitHub, You will first need to create a fork of this repo so you can connect it to your Heroku app.  
7. Before deploying, You will need to change all of the ID's in `/config.yml` to reflect _your_ server..  

|          KEY          | VALUE                                                                                                                            |
|:---------------------:|----------------------------------------------------------------------------------------------------------------------------------|
| bruce_token           | Your Bot's token you've got from the [Discord developer portal](https://discord.com/developers/applications)                     |
| R6STATS_API_KEY       | Your [r6stats](https://r6stats.com/) API key. You can get that from their [Discord](https://discord.com/invite/pUdraS3)          |
| serviceAccountKeyJSON | Firebase service account key in JSON                                                                                             |
| TRN_API_KEY           | Tracker Network API key                                                                                                          |
| UBISOFT_EMAIL         | Ubisoft email*                                                                                                                   |
| UBISOFT_PASSW         | Ubisoft password*                                                                                                                |

(\* You can create a dummy account just for this)  

---  

I'm willing to help answer any questions that you may have  
You can either join my [Discord](https://discord.com/invite/sXDbtp4) or send me on Discord at __CNDRD#2233__  

---  

Made with ❤️ by [CNDRD](https://cndrd.github.io/)  
