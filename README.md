### `tank-protocol` commands 

| Command     | Description                       |
| :---------- | :-------------------------------- |
| LOG         | Login user. |
| REG         | Register new user. |
| DEL         | Delete user. |
| QUIT        | Disconnect. |
| CRTR        | Create new room. |
| DELR        | Delete room. |
| AVBL        |	Get available game rooms |
| MOVE        | Move tank with position |
| SHOT        | Bullets..           |
| SCRS        | Get user scores. |
| SCRA        | Get user scores. (Ascending) |
| SCRD        | Get user scores. (Descending). |
| BRDC        | Broadcast message. |
| SEND        | Send message. |
| STAT        | Returns information of server, including address and port to which the client should connect. |
| ACCT        | User account information. |

### server return codes

| Code     | Explanation                       |
| :---------- | :-------------------------------- |
| 100         | The requested action is being initiated |
| 200         | The requested action has been successfully completed. |
| 400         | Transient Negative Completion reply |
| 500         | Permanent Negative Completion reply |
### expected stream
*   {*command*, *data*}
*   *E.g*: "{"command": "LOG", "data": {"username": "user1", "password": "pass1"}}