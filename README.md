# swagger diff slack notify

This project is for continuously tracking API changes and monitoring them through Slack notification messages.


## Requirements

* python 3.13+
* open api 3.0.x
* python library
  - deepdiff
  - slack_sdk
  - request
  - http
  - re
  - urllib
  - json
  - datetime
* Slack Env Setting
  - add workspace
  - bot setup

## Usage

* install python modules
* You can configure the Slack details in the env.json.
     ```
      {
        "slack_token": "",
        "slack_channel_id": ""
      }
    ```

## Execute
* with run argument
  ```
      python main.py http://localhost.co.kr:8080
  ```


## Features
- compare the api spec as-is and to-be
- send the comparison results to a Slack channel
  

## Output snapshot
* slack message
  
    ![slack_message](https://tnfhrnsss.github.io/docs/sub-projects/img/swagger_diff_slack_notify_1.png)


## Blog reference

For further reference, please consider the following sections:

* [blog](https://tnfhrnsss.github.io/docs/sub-projects/swagger_diff_slack_notify/)

