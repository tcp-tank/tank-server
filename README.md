### `tank-protocol` commands 

| Command     | Description                       |
| :---------- | :-------------------------------- |
| LOG         | Login user. |
| REG         | Register new user. |
| QUIT        | Disconnect. |
| STAT        | Returns information of server, including address and port to which the client should connect. |
| ACCT        | User account information. |
| DELE        | Delete user. |
| BRDC        | Broadcast message. |
| SEND        | Send message. |

### server return codes

| Code     | Explanation                       |
| :---------- | :-------------------------------- |
| 100         | The requested action is being initiated |
| 200         | The requested action has been successfully completed. |
| 400         | Transient Negative Completion reply |
| 500         | Permanent Negative Completion reply |

### expected stream
*   [*command*, *data*]
*   *E.g*: ["LOG", {"username": "user1", "password": "pass1"}]