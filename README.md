
| Command     | Description                       |
| :---------- | :-------------------------------- |
| INIT        | First server respond.|
| EXIT        | Exit Game.|
| LOGN        | Login. |
| LOGT        | Logout. |
| ENTL        | User enters lobby. |
| ENTR        | User enters room. |
| LVER        | User leaves room. |
| LVEL        |	User leaves lobby. |
| CRTR        | Create Room. |
| SRTG        | Start Game. |
| MOVE        | Tank move. |
| SHOT        | Tank shot. |
| MESG        | Message to chat. |
| DOWN        | Server closed. |


### server return codes

| Code     | Explanation                       |
| :---------- | :-------------------------------- |
| 100         | The requested action is being initiated |
| 200         | The requested action has been successfully completed. |
| 400         | Transient Negative Completion reply |
| 500         | Permanent Negative Completion reply |
### expected stream
*   {*command*, *data*}
*   *E.g*:  
    
    ```json
    {
        "command": "LOG", 
        "data": {
            "username": "user1", 
            "password": "pass1"
        }
    }
    ```